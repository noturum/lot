import os.path
from Strings import *
from telebot import TeleBot
from DbController import User,Group, Database as db
import logging
import pickle
from threading import Thread,Event
logging.basicConfig(filename='/root/bot/error.log',
                    format='[%(asctime)s] => %(message)s',
                    level=logging.ERROR)
import bs4,lxml,requests
bot = TeleBot(API_KEY)


class LinkScraber(Thread):
    def __init__(self):
        
        super().__init__(daemon=True)

    def run(self):
        self.client.get(link)
        ...






class TaskController(Thread):
    __inst__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__inst__:
            return cls.__inst__
        else:
            cls.__inst__ = cls(*args, **kwargs)
            return cls
    def __init__(self):
        self._tasks=[]
    def add_task(self,func,*arg,name=None):

        self._tasks.append(task:=(super().__init__(target=func,args=arg,name=name)))
        task.start()
    def stop(self,name):
        for task in self._tasks:
            if task.name==name and task.isAlive():
                task.join()


tasker=TaskController()

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
if os.path.exists('/root/bot/dump.pickle'):
    with open('/root/bot/dump.pickle', 'rb') as handle:
        chats = pickle.load(handle)
def main():
    @bot.edited_message_handler(func=lambda message: True)
    def handler_function(message):
        ...
    bot.polling(none_stop=True)
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        bot.stop_polling()
        logging.error(e)
        with open('/root/bot/dump.pickle', 'wb') as handle:
            pickle.dump(chats, handle)
        exit(1)
