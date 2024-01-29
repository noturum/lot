import asyncio
import time
from typing import TypedDict, Callable

from threading import Thread
import datetime
from enum import Enum


class PeriodType(Enum):
    ONCE = 0
    FOREVER = 1
    COUNT = 2
    SYSTEM = 3


class Task(TypedDict):
    thread: Thread | None
    func: Callable
    args: list
    name: str
    _async: bool


class TaskTime(Task, total=False):
    type: PeriodType
    period: datetime.datetime
    timestamp: datetime.datetime
    count: int


class TaskController:
    __inst__ = None

    def __new__(cls, *args, **kwargs):
        if not cls.__inst__:
            cls.__inst__ = super().__new__(cls)
        return cls.__inst__

    def __init__(self):
        self._tasks: [Task] = []
        self._timeout: int = 10 * 60

    @property
    def _break(self):
        time.sleep(self._timeout)
        return True

    def create_task(self, func, *args, _async: bool = False, name: str | None = None,
                    type: PeriodType = PeriodType.ONCE, **kwargs):
        """
        Добавляет таску в отдельный паток
        :param func: ссылка на функциюю
        :param args: аргументы функции (если есть)
        :param _async: если функция ассинхроная
        :param name: имя таски
        :param kwargs: кварги для периода (передать count,period)
        :return:
        """
        def ase(func,*args):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.get_event_loop().run_until_complete(func(*args))
        if _async:
            target=ase


        else:
            target = func
        thread = Thread(target=target, args=(func,*args) if _async else [], name=name, daemon=False)
        if type != PeriodType.SYSTEM:
            period = kwargs.get('period') or 1
            assert period
            count = kwargs.get('count')
            task = Task(thread=thread, name=name, func=target, args=args, _async=_async, type=type, period=period,
                        timestamp=datetime.datetime.now(), count=count)
            self._tasks.append(task)
        print(name)
        thread.start()


    def scheduler(self):
        while True:
            for task in self._tasks:
                if task['thread']._is_stopped:
                    match task['type']:
                        case PeriodType.ONCE:
                            self._tasks.pop(self._tasks.index(task))
                        case PeriodType.COUNT:
                            if task['count'] > 0:
                                if task['timestamp'] + task['period'] >= datetime.datetime.now():
                                    self.create_task(task['func'], task['args'], task['_async'], name=task['name'],
                                                 type=PeriodType.SYSTEM)
                                    task['timestamp']=datetime.datetime.now()
                                task['count'] -= 1
                            else:
                                self._tasks.pop(self._tasks.index(task))
                        case PeriodType.FOREVER:
                            if task['timestamp'] + task['period'] >= datetime.datetime.now():
                                self.create_task(task['func'], task['args'], task['_async'], name=task['name'],
                                                 type=PeriodType.SYSTEM)
                            task['timestamp'] = datetime.datetime.now()
        time.sleep(self._timeout)


if __name__ != "__main__":
    c_task = TaskController()

