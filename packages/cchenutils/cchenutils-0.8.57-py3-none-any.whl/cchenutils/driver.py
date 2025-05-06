import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Chrome(webdriver.Chrome):
    scroll_pause = 4

    def __init__(self, incognito=True, image=False, proxy=None, window_size='960,720', window_position='0,0',
                 headless=False):
        options = Options()
        if incognito:
            options.add_argument("--incognito")
        if not image:
            options.add_argument('--blink-settings=imagesEnabled=false')
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        options.add_argument(f'--window-size={window_size}')
        options.add_argument(f'--window-position={window_position}')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('enable-features=NetworkServiceInProcess')
        options.add_argument('disable-features=NetworkService')
        if headless:
            options.add_argument('--headless')
        super().__init__(options=options)

    def scroll_to_bottom(self):
        this_height = self.page_height
        last_height = -1
        while this_height != last_height:
            self.scroll_down()
            last_height = this_height
            this_height = self.page_height
            time.sleep(self.scroll_pause)

    def scroll_down(self):
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return self

    @property
    def page_height(self):
        return self.execute_script("return document.body.scrollHeight")
