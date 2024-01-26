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

        if _async:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            target = (lambda _func, _args: loop.run_until_complete(_func(*_args)))(func, args)
        else:
            target = func
        thread = Thread(target=target, args=args, name=name, daemon=False)
        if type != PeriodType.SYSTEM:
            period = kwargs.get('period') or 1
            assert period
            count = kwargs.get('count')
            task = Task(thread=thread, name=name, func=func, args=args, _async=_async, type=type, period=period,
                        timestamp=datetime.datetime.now(), count=count)
            self._tasks.append(task)
        thread.start()
        if _async:
            thread.join()

    def scheduler(self):
        while True:
            for task in self._tasks:
                if task['thread']._is_stoped:
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


if __name__ != "__main__":
    c_task = TaskController()
    c_task.create_task(c_task.scheduler, name='SHELDULER', type=PeriodType.SYSTEM)
