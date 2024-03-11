
import logging
import os
import re
import asyncio
import time

from aiohttp import ClientSession, ClientTimeout

from Tasks import c_task, PeriodType, datetime

logging.basicConfig(filename='error.log',
                    format='[%(asctime)s] => %(message)s',
                    level=logging.ERROR)
from dotenv import load_dotenv

load_dotenv()
PHONE=os.getenv('PHONE')
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
        self.timeout= ClientTimeout(total=6)

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
    async def get_youtube_link(self):
        print('start grab y_link')
        async with ClientSession(timeout=self.timeout) as session:
            async with session.get('https://whatstat.ru/channels/science_technology') as resp:
                soup = bs(await resp.text(), 'lxml')
                links = ['https://whatstat.ru' +a.find('a').get('href') for a in soup.find_all("td") if a.find('a')]
                await self.paralle_get(self.get_from_top,links)
        self.load(self.LINK_THREDS)
        soup = bs(self._get_text(), 'lxml')
        self._driver.close()
        links = ['https://youtube.com'+a.get('href') for a in soup.find_all('a') if a.get('href')]
        await self.paralle_get(self.get_from_thrends, links)

    @staticmethod
    async def paralle_get(func,list):
        for count in range(0, len(list), 20):
            tasks=[]
            print(f'Проверка {0} завершена на {count/len(list)*100 if count>0 else 0}%')
            for link in list[count:count + 20]:

                tasks.append(asyncio.create_task(func(link)))
            await asyncio.gather(*tasks)

    async def get_from_top(self,url):
        try:
            async with ClientSession(timeout=self.timeout) as session:
                async with session.get(url, timeout=self.timeout) as resp_y:
                    y_link = bs(await resp_y.text(), 'lxml').find(
                        attrs={'class': 'channel-header'}).find('a').get('href')

                    async with session.get(y_link, timeout=self.timeout) as resp_t:
                        self.get_tg(await resp_t.text())
        except asyncio.exceptions.TimeoutError:
            return
    async def get_from_thrends(self,url):
        try:
            async with ClientSession(timeout=self.timeout) as session:
                async with session.get(url, timeout=self.timeout) as resp_t:
                    self.get_tg(await resp_t.text())
        except asyncio.exceptions.TimeoutError:
            return

    def get_tg(self, text):

        try:
            links = re.findall("https:\/\/t.me[\w@^\/]*",
                               text)
        except BaseException as e:
            print(e)
        else:
            for link in links:
                if link not in self.links:
                    self.links.append(link)
                    c_database.upsert(Links, 'href', 'href', href=link)

class Notyfier:
    def __init__(self):
        ...
    @staticmethod
    def _send_message(uid: int, text: str,keyboard:InlineKeyboardMarkup|ReplyKeyboardMarkup): bot.send_message(uid, text,reply_markup=keyboard)
    def get_stat(self):
        pattern=''
        ...




def bootstrap():
    c_task.create_task(c_task.scheduler, name='SHELDULER', type=PeriodType.SYSTEM)
    ls=LinkScraber()
    # c_task.create_task(ls.get_youtube_link,
    #                    _async=True,name='Thrends',
    #                    type=PeriodType.FOREVER,
    #                    period=datetime.timedelta(days=1))
    c_task.create_task(client(PHONE).check_entity,
                       True ,_async=True,
                       name='Check_LOT'
                       ,type=PeriodType.FOREVER,
                       period=datetime.timedelta(days=1))
    while True:
        ...


def main():
    @bot.message_handler(content_types=['text'])
    def text(message):
        bot.delete_message(message.chat.id,message.id)
        bot.send_message(message.chat.id,str(c_task._tasks))
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
