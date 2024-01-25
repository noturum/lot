import asyncio
import os, logging, pickle, re, lxml, requests
import time

import aiohttp

from Tasks import c_task
logging.basicConfig(filename='error.log',
                    format='[%(asctime)s] => %(message)s',
                    level=logging.ERROR)
from dotenv import load_dotenv

load_dotenv()
PHONE=os.getenv('PHONE')
assert PHONE
from telebot import TeleBot

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
    async def check_blogs(self):
        print('Run Check Blogs')
        timeout = aiohttp.ClientTimeout(total=600)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('https://whatstat.ru/channels/science_technology') as resp:
                soup = bs(await resp.text(), 'lxml')
                links = [a.find('a').get('href') for a in soup.find_all("td") if a.find('a')]

        async def get(url):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:

                    async with session.get(url, timeout=timeout) as resp_y:
                        y_link = bs(await resp_y.text(), 'lxml').find(
                            attrs={'class': 'channel-header'}).find('a').get('href')

                        async with session.get(y_link, timeout=timeout) as resp_t:
                            if tg := self._get_tg(await resp_t.text()):
                                for link in tg:
                                    if link not in self.links:
                                        self.links.append(link)
                                        c_database.upsert(Links, 'href', 'href', href=link)
            except:
                f = lambda url: bs(requests.get(url).text, 'lxml').find(
                    attrs={'class': 'channel-header'}).find('a').get('href')
                t = await asyncio.get_event_loop().run_in_executor(None, f, url)
                async with aiohttp.ClientSession(timeout=timeout) as session:

                    async with session.get(t, timeout=timeout) as resp_t:
                        if tg:=self._get_tg(await resp_t.text()):
                            for link in tg:
                                if link not in self.links:
                                    self.links.append(link)
                                    c_database.upsert(Links, 'href', 'href', href=link)



        for count in range(0, len(links), 20):
            tasks=[]
            print(f'Проверка блогеров завершена на {count/len(links)*100 if count>0 else 0}%')
            for link in links[count:count + 20]:

                tasks.append(asyncio.create_task(get('https://whatstat.ru' + link)))
            await asyncio.gather(*tasks)

    def get_threds(self):
        self.load(self.LINK_THREDS)
        soup = bs(self._get_text(), 'lxml')
        links = soup.find_all('a')
        threds = []
        for link in links:
            if (hr := link.get('href')) and hr not in threds:
                threds.append(hr)
        return threds

    def _get_tg(self, text):
        try:
            links = re.findall("https:\/\/t.me[\w@^\/]*",
                               text)
            return links
        except BaseException as e:
            print(e)
            return None
    def run(self):
        for thred in self.get_threds():
            if tg := self._get_tg(self.MAIN + thred):
                for link in tg:
                    if link not in self.links:
                        self.links.append(link)
                        c_database.upsert(Links, 'href', 'href', href=link)







# class Message:
#     def __init__(self, text, keyboard=None):
#         self.__msg = None
#         self.text = text
#         self.keyboard = keyboard
#
#     def send_message(self, chat_id):
#         self.__msg = bot.send_message(chat_id=chat_id, text=self.text, reply_markup=self.keyboard)
#
#
# class Chat:
#
#     def __init__(self, id):
#         self.__id = id
#         self.__state = None
#
#     def get_user(self):
#         return db.select(User, [User.chat_id == self.__id])[0]
#
#     def add_message(self, msg: Message):
#         msg.send_message(self.__id)
#
#     @property
#     def state(self):
#         return self.__state
#
#     @state.setter
#     def state(self, state):
#         self.__state = state
#
#     @property
#     def chat_id(self):
#         return self.__id
#

def bootstrap():
    global c_task
    #c_task.add_task(LinkScraber().run,name='Threads')
    c_task.add_task(LinkScraber().check_blogs,_async=True,name='Blogs')
    # b = c_database.select(Links, [Links.isVerified == False])
    # links=[i.href for i in b]
    # c_task.add_task((cli:=client(PHONE)).run_loop(cli.test,links),name='ToDO')
    # _client.start()
    # if os.path.exists('dump.pickle'):
    #     with open('dump.pickle', 'rb') as handle:
    #         chats = pickle.load(handle)





def main():
    @bot.message_handler(content_types=['text'])
    def text(message):
        bot.delete_message(message.chat.id,message.id)
        bot.send_message(message.chat.id,str(c_task._tasks))
        print(message.text)


    bot.polling(none_stop=True)


if __name__ == "__main__":
    try:
        bootstrap()
        #main()

    except Exception as e:

        bot.stop_polling()

        logging.error(e)
        with open('dump.pickle', 'wb') as handle:
            pickle.dump('any', handle)
        exit(1)
