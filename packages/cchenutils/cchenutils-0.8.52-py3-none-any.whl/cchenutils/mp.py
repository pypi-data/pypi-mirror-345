import random
import time
import traceback

from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, Timeout, JSONDecodeError, ChunkedEncodingError

from .files import write, txt_write


def writer(queue):
    """
    Listens to `queue` for file writing tasks. Expects a tuple:

    - For CSV:
        (fp, data, headers, [optional scrape_time])
    - For JSON/JSONL:
        (fp, data)

    Use 'STOP' to end the loop.
    """
    while True:
        args = queue.get()
        if args == 'STOP':
            break
        if len(args) < 2:
            print(f'[writer] Invalid input: {args}')
            continue
        for _ in range(10):
            try:
                write(*args)
                break
            except PermissionError:
                time.sleep(1)


def scraper(func, *func_args,
            proxy_list=None, proxyerr=None, stderr=None, retries=3, debug=False,
            **kwargs):
    """
    A wrapper to call a function with optional proxy rotation, retry logic, and error logging.

    Args:
        func (callable): The function to be called (e.g., your scraper function).
        *func_args: Positional arguments to pass to `func`.
        proxy_list (multiprocessing.Manager().dict, optional): Shared dict of proxies and their quality.
            - Keys are proxy strings.
            - Values are booleans indicating whether the proxy works.
        proxyerr (str, optional): File path to log dead proxies.
        stderr (str, optional): File path to log errors (proxy + args + traceback).
        retries (int, optional): Number of retries. Defaults to 3 (via kwargs).
        debug (bool, optional): If True, will print and pause on errors for 300 seconds.
        **kwargs: Keyword arguments to pass to `func`.

    Returns:
        Any: The return value of `func` if successful. Otherwise, `None`.
    """
    if proxy_list is None:
        retries = min(1, retries)
    for _ in range(retries):
        proxy = random.choice([ip for ip, qual in proxy_list.items() if qual]) if proxy_list else None
        try:
            return func(*func_args, **kwargs, proxy=proxy)
        except (ProxyError, ConnectTimeout, ReadTimeout, Timeout):
            proxy_list[proxy] = False
            if proxyerr is not None:
                txt_write(proxyerr, proxy)
        except (JSONDecodeError, ChunkedEncodingError):
            pass
        except Exception:
            if stderr:
                err = ['------',
                       scraper.__name__,
                       proxy,
                       *func_args,
                       traceback.format_exc()]
                txt_write(stderr, err)
            else:
                print(proxy, *func_args)
            if debug:
                traceback.print_exc()
                time.sleep(300)
    return None
