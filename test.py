# class Singl:
#     def __init__(self):
#         self.tasks=[]
#     def task(self,t):
#         def decorator(func):
#             def wrapper():
#                 print(t)
#                 return func()
#             return wrapper
#         return decorator
# a=Singl()
#
# @a.task(20)
# def rr():
#     return 2
# rr()

import lxml,requests
from bs4 import BeautifulSoup as bs

from selenium.webdriver import Chrome,ChromeOptions,DesiredCapabilities
from selenium.common import SessionNotCreatedException
from threading import Thread
import re
class LinkScraber():
    MAIN = 'https://www.youtube.com'
    LINK_THREDS = 'https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl'
    options = ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('log-level=3')
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    def __init__(self, headless=False):

        self._driver = self._get_driver(headless)
        self._windows = {}
        self.links = []

    def _get_driver(self, headless: bool = False):
        if headless == True:
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')
        try:
            return Chrome(options=self.options)
        except SessionNotCreatedException as e:
            print(e)
            exit(1)

    def load(self, url, tab_name='main'):
        if tab_name in self._windows.keys():
            self._driver.switch_to.window(self._windows[tab_name])
        else:
            self._driver.switch_to.new_window('tab')
            self._windows[tab_name] = self._driver.window_handles[-1]
        self._driver.get(url)

    def _get_text(self, tab_name=None):
        if tab_name:
            self._driver.switch_to.window(self._windows[tab_name])
        return self._driver.page_source

    def get_threds(self):
        self.load(self.LINK_THREDS)
        soup = bs(self._get_text(), 'lxml')
        links = soup.find_all('a')
        threds = []
        for link in links:
            if (hr := link.get('href')) and hr not in threds:
                threds.append(hr)
        return threds




    def _get_tg(self, url):

        try:
            text=requests.get(url).text

            links = re.findall("https:\/\/t.me[\w@^\/]*",
                               text)
            return links

        except BaseException as e:
            print(e)
            return None

    def run(self):
        for thred in self.get_threds():
            if tg:=self._get_tg(self.MAIN + thred):
                for link in tg:
                    if link not in self.links:
                        self.links.append(link)


LinkScraber(False).run()