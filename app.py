import logging
import os
import re
import asyncio
import time
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientConnectorError
from Tasks import c_task, PeriodType, timedelta, Task

logging.basicConfig(filename='error.log',
                    format='[%(asctime)s] => %(message)s',
                    level=logging.ERROR)
from dotenv import load_dotenv

load_dotenv()
PHONE = os.getenv('PHONE')
assert PHONE
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

try:
    from DbController import Links, Selected, c_database
    from Telephon import Client as client
except AssertionError as e:
    logging.error(e)

    exit(1)
from bs4 import BeautifulSoup as bs

BOT_API = os.getenv('BOT_API')
assert BOT_API
bot = TeleBot(BOT_API)
from selenium.webdriver import Chrome, ChromeOptions, DesiredCapabilities
from selenium.common import SessionNotCreatedException


class LinkScraber:
    MAIN = 'https://www.youtube.com'
    LINK_THREDS = 'https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl'
    options = ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('log-level=3')
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    def __init__(self, headless=True):
        self._driver = self._get_driver(headless)
        self._windows = {}
        self.links = []
        self.timeout = ClientTimeout(total=60)

    async def _aget(self, url):
        async with ClientSession(timeout=self.timeout) as session:
            async with session.get(url) as response:
                return await response.text()

    def _get_driver(self, headless: bool = True):
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

    async def get_youtube_link(self):
        print('start grab y_link')
        resp = await self._aget('https://whatstat.ru/channels/science_technology')
        soup = bs(resp, 'html.parser')
        links = ['https://whatstat.ru' + a.find('a').get('href') for a in soup.find_all("td") if a.find('a')]
        await self.paralle_get(self.get_from_top, links)
        self.load(self.LINK_THREDS)
        soup = bs(self._get_text(), 'html.parser')
        self._driver.close()
        links = ['https://youtube.com' + a.get('href') for a in soup.find_all('a') if a.get('href')]
        await self.paralle_get(self.get_from_thrends, links)

    @staticmethod
    async def paralle_get(func, links):
        for count in range(0, len(links), 10):
            async with asyncio.TaskGroup() as tg:
                print(f'Проверка {func.__name__} завершена на {int(count / len(links) * 100) if count > 0 else 0}%')
                for link in links[count:count + 10]:
                    tg.create_task(func(link))

    async def get_from_top(self, url):
        try:
            y_link = bs(await self._aget(url), 'html.parser').find(
                attrs={'class': 'channel-header'}).find('a').get('href')
            assert y_link
            self.get_tg(await self._aget(y_link))
        except (asyncio.exceptions.TimeoutError, AssertionError, ClientConnectorError):
            print(url)
            return

    async def get_from_thrends(self, url):
        try:
            self.get_tg(await self._aget(url))
        except asyncio.exceptions.TimeoutError:
            return

    def get_tg(self, text):
        try:
            links = re.findall("https:\/\/t.me[\w@^\/][a-zA-Z][\w\d]{3,30}[a-zA-Z\d]", text)
        except BaseException as e:
            return
        else:
            for link in links:
                if link not in self.links:
                    self.links.append(link)
                    c_database.upsert(Links, 'href', 'href', href=link)


class Notyfier:
    def __init__(self):
        ...

    @staticmethod
    def _send_message(uid: int, text: str, keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup): bot.send_message(uid,
                                                                                                                   text,
                                                                                                                   reply_markup=keyboard)

    def get_stat(self):
        pattern = ''
        ...


def bootstrap():
    ls = LinkScraber()
    # task = Task(PeriodType.FOREVER, ls.get_youtube_link, name='yl',period=timedelta(days=1))
    # c_task.create(task)
    # task = Task(PeriodType.FOREVER, client(PHONE).check_entity, func_args=(True,), name='SOT',
    #             period=timedelta(days=1))
    # c_task.create(task)
    task = Task(PeriodType.FOREVER, client(PHONE).check_entity , name='SOT',
                period=timedelta(days=1))
    c_task.create(task)
    # c_task.create_task(ls.get_youtube_link,
    #                    _async=True,name='Thrends',
    #                    type=PeriodType.FOREVER,
    #                    period=datetime.timedelta(days=1))
    # task = Task(PeriodType.FOREVER, client(PHONE).check_entity, func_args=(True,), name='SOT',
    #             period=timedelta(hours=24))
    # c_task.create(task)
    while True:
        time.sleep(1000)
        ...


def main():
    @bot.message_handler(content_types=['text'])
    def text(message):
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(message.chat.id, str(c_task._tasks))
        print(message.text)

    bot.polling(none_stop=True)


if __name__ == "__main__":
    # try:
    #     main()
    bootstrap()

# except Exception as e:
#
#     bot.stop_polling()
#
#     logging.error(e)
#     with open('dump.pickle', 'wb') as handle:
#         pickle.dump('any', handle)
#     exit(1)
