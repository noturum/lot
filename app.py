import os, logging, pickle, re, lxml, requests

logging.basicConfig(filename='error.log',
                    format='[%(asctime)s] => %(message)s',
                    level=logging.ERROR)
from dotenv import load_dotenv

load_dotenv()
PHONE=os.getenv('PHONE')
assert PHONE
from telebot import TeleBot

try:
    from DbController import User, Group, Database as db
    from Telephon import Client as client
except AssertionError as e:
    logging.error(e)
    exit(1)
from threading import Thread, Event

from bs4 import BeautifulSoup as bs

BOT_API = os.getenv('BOT_API')
assert BOT_API
bot = TeleBot(BOT_API)
from selenium.webdriver import Chrome, ChromeOptions, DesiredCapabilities
from selenium.common import SessionNotCreatedException


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
        super().__init__(daemon=False)
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
            text = requests.get(url).text

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
                        print(link)


class TaskController:
    __inst__ = None
    def __new__(cls, *args, **kwargs):
        _inst = None
        def __new__(cls, *args, **kwargs):
            if not isinstance(cls._inst, cls):
                cls._instance = object.__new__(cls, *args, **kwargs)
            return cls._instance

    def __init__(self):
        self._tasks = []

    def add_task(self, func, *arg, name=None):

        self._tasks.append(task := (Thread.__init__(target=func, args=arg, name=name)))
        task.start()

    def stop(self, name):
        for task in self._tasks:
            if task.name == name and task.isAlive():
                task.join()

tasker = TaskController()


class Message:
    def __init__(self, text, keyboard=None):
        self.__msg = None
        self.text = text
        self.keyboard = keyboard

    def send_message(self, chat_id):
        self.__msg = bot.send_message(chat_id=chat_id, text=self.text, reply_markup=self.keyboard)


class Chat:

    def __init__(self, id):
        self.__id = id
        self.__state = None

    def get_user(self):
        return db.select(User, [User.chat_id == self.__id])[0]

    def add_message(self, msg: Message):
        msg.send_message(self.__id)

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state

    @property
    def chat_id(self):
        return self.__id


def init(message):
    if len(db.select(User, [User.chat_id == message.chat.id])) == 0:
        db.insert(User, chat_id=message.chat.id, name=message.from_user.username)

    chats[message.chat.id] = Chat(message.chat.id)


chats = {}
if os.path.exists('dump.pickle'):
    with open('dump.pickle', 'rb') as handle:
        chats = pickle.load(handle)


def main():
    @bot.message_handler(content_types=['text'])
    def text(message):
        print(message.text)

    _client = client(PHONE)
    _client.start()
    bot.polling(none_stop=True)


if __name__ == "__main__":
    try:
        # main()
        LinkScraber().start()
    except Exception as e:

        bot.stop_polling()

        logging.error(e)
        with open('dump.pickle', 'wb') as handle:
            pickle.dump(chats, handle)
        exit(1)
