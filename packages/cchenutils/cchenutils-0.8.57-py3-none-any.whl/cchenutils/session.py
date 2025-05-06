import requests
import time
import urllib
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import ConnectionError, ProxyError, JSONDecodeError

from .dictutils import Dict


class Session(requests.Session):
    def __init__(self, max_retries=3, sleep=0, timeout=60, headers=None,
                 status_whitelist=None, status_retry_forcelist=None, proxy=None):
        super().__init__()
        self.mount('https://',
                   HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1, status_forcelist=status_retry_forcelist)))
        if headers is None:
            self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                                          'Chrome/112.0.0.0 Safari/537.36'}
        else:
            self.headers = headers
        self.max_retries = max_retries
        self.status_whitelist = [200] if status_whitelist is None else [200] + status_whitelist
        self.sleep = sleep
        self.timeout = timeout
        if proxy:
            if proxy.startswith('http'):
                self.proxies |= {'http': proxy, 'https': proxy}
            else:
                self.proxies |= {'http': f'http://{proxy}:8888', 'https': f'https://{proxy}:8888'}

    def get(self, url, session_cookies=False, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.
        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        kwargs.setdefault('allow_redirects', True)
        _retry = kwargs.pop('_retry', 0)
        if 'params' in kwargs and isinstance(kwargs['params'], dict):
            kwargs['params'] = urllib.parse.urlencode(kwargs['params'], quote_via=urllib.parse.quote)

        cookies = kwargs.pop('cookies', {})
        if isinstance(cookies, str):
            cookies = dict(kv.split('=') for kv in cookies.split('; '))
        if session_cookies:
            cookies = self.cookiejar2dict(self.cookies) | cookies

        headers = self.headers
        if 'headers' in kwargs:
            headers |= kwargs['headers']
        if cookies:
            headers['cookies'] = '; '.join(f'{k}={v}' for k, v in cookies.items())

        try:
            r = self.request("GET", url, headers=headers, **kwargs)
            if r.status_code in self.status_whitelist or _retry == self.max_retries:
                return r
        except (ProxyError, ConnectionError):
            pass
        time.sleep(self.sleep)
        kwargs['_retry'] = _retry + 1
        return self.get(url, **kwargs)

    def post(self, url, session_cookies=False, **kwargs):
        if session_cookies and 'cookies' not in kwargs and 'cookies' not in kwargs.get('headers', {}):
            kwargs['cookies'] = self.cookies
        if 'headers' in kwargs:
            kwargs['headers'] |= self.headers
        return self.request("POST", url, **kwargs)

    def get_json(self, url, **kwargs):
        return Dict(self.get(url, **kwargs).json())

    def get_soup(self, url, **kwargs):
        return BeautifulSoup(self.get(url, **kwargs).text, features='lxml')

    def get_json_or_soup(self, url, **kwargs):
        r = self.get(url, **kwargs)
        try:
            return Dict(r.json())
        except JSONDecodeError:
            return BeautifulSoup(r.text, features='lxml')

    def add_cookie(self, name, value, **kwargs):
        cookie = requests.cookies.create_cookie(name, value, **kwargs)
        self.cookies.set_cookie(cookie)

    @staticmethod
    def cookiejar2dict(cookiejar):
        return {cookie.name: cookie.value for cookie in cookiejar} if len(cookiejar) else {}
