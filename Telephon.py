import time

from telethon.errors.rpcerrorlist import UsernameInvalidError, FloodWaitError,UsernameInvalidError
from dotenv import load_dotenv
from telethon.tl.types import InputMessagesFilterPinned
import re, os, asyncio
from telethon import TelegramClient, events
from DbController import c_database, Links, Selected

load_dotenv()
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')

assert TELEGRAM_API_ID, 'TELEGRAM_API_ID not found'
assert TELEGRAM_API_HASH, 'TELEGRAM_API_HASH not found'


class Client:
    def __init__(self, phone: str):
        self._client = TelegramClient(session=phone, api_id=TELEGRAM_API_ID,
                                      api_hash=TELEGRAM_API_HASH, system_version="4.16.30-vxCUSTOM")
        self._phone = phone

    @property
    async def is_login(self):
        if not self._client:
            return False
        async with self._client as client:
            if await client.is_user_authorized():
                return True
            else:
                await client.start(self._phone)

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, loop):
        self._loop = loop

    async def get_message(self, entity, limit):
        if await self.is_login:
            async with self._client:
                return await self._client.get_messages(entity, limit=limit)

    async def get_dialogs(self):
        if await self.is_login:
            async with self._client:
                return [dialog async for dialog in self._client.iter_dialogs()]

    async def check_entity(self, from_me=True):
        print('Check entity start')
        if not await self.is_login:
            print('nologin')
            return
        async with self._client as client:
            sel_messages = [(row.message_id, row.peer_id) for row in c_database.select(Selected)]
            if from_me:
                links = [dialog.entity async for dialog in client.iter_dialogs() if dialog]
            else:
                links = [link.href for link in c_database.select(Links)]
            for link in links:
                try:

                    pin_messages = await client.get_messages(link, filter=InputMessagesFilterPinned)
                    messages = await self._client.get_messages(link, limit=10)
                    messages += pin_messages
                    for message in messages:
                        uid = message.peer_id.to_dict().get('channel_id') or message.peer_id.to_dict().get(
                            'user_id')

                        if len(re.findall(r'(.онкурс)|(.озыгрыш*)|(.частвоват.)',
                                          message.message if message.message else '')) and (
                                message.id, uid) not in sel_messages:
                            await client.forward_messages(5288842675, message.id, message.peer_id)
                            c_database.insert(Selected, message_id=message.id, peer_id=uid,
                                              isforwarded=True)
                except (ValueError, UsernameInvalidError):
                    print('bad entity')
                    #c_database.delete(Links, [Links.href == link])
                except FloodWaitError as e:
                    print(f'Бан по времени - {e}')
                    return

                finally:
                    time.sleep(2)
                    # if not from_me:
                    #     c_database.update(Links, [Links.href == link], isVerified=True)
        print('Check entity stop')

    def run_loop(self, func, *args, **kwargs):
        return self._client.loop.run_until_complete(func(*args, **kwargs))
