
from dotenv import load_dotenv


load_dotenv()


from telethon.tl.types import InputMessagesFilterPinned
import re


from telethon import TelegramClient,events
from threading import Thread
import os
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')

assert TELEGRAM_API_ID , 'TELEGRAM_API_ID not found'
assert TELEGRAM_API_HASH , 'TELEGRAM_API_HASH not found'
import asyncio
class Client(Thread):
    def __init__(self, phone: str):
        super().__init__(daemon=False)
        self._client = TelegramClient(session=phone, api_id=TELEGRAM_API_ID,
                                      api_hash=TELEGRAM_API_HASH, system_version="4.16.30-vxCUSTOM")
        self._phone=phone
    @property
    async def is_login(self):
        if self._client:
            async with self._client:

                return  await self._client.is_user_authorized()
    @property
    def loop(self):
        return self._loop
    @loop.setter
    def loop(self,loop):
        self._loop=loop
    async def login(self):
        if not self.is_login:
            self._client.start(self._phone)

    async def get_message(self,entity,limit):
        if await self.is_login:
            async with self._client:
                return await self._client.get_messages(entity,limit=limit)
    async def get_dialogs(self):
        if await self.is_login:
            async with self._client:
                return [dialog async for dialog in self._client.iter_dialogs()]
    async def forward_pinned_message(self):
        if await self.is_login:
            async with self._client:
                async for i in self._client.iter_dialogs():
                    messages = await self._client.get_messages(i.entity,filter=InputMessagesFilterPinned)
                    for message in messages:
                        if len(re.findall(r'(.онкурс)|(.озыгрыш*)|(.частвоват.)',message.message)):

                            await self._client.forward_messages(5288842675,message.id,message.peer_id)
    async def test(self):
        if await self.is_login:
            async with self._client:
                msgs = await self._client.get_messages('https://t.me/pospikasya', filter=InputMessagesFilterPinned)
                print(msgs)
    def run_loop(self,func,*args,**kwargs):
        return self._client.loop.run_until_complete(func(*args,**kwargs))
        ...
    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._client = TelegramClient(session=self._phone, api_id=TELEGRAM_API_ID,
                                      api_hash=TELEGRAM_API_HASH, loop=self.loop, system_version="4.16.30-vxCUSTOM")

        @self._client.on(events.NewMessage)
        async def new(event):
            print(event.raw_text)

        self._client.start()

        self._client.run_until_disconnected()



a=Client(os.getenv('PHONE'))
print(a.run_loop(a.test))