import asyncio
import threading
import time
from typing import TypedDict, Callable

from threading import Thread,Lock
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
        self._timeout: int = 1

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
        thread = Thread(target=target, name=name)
        if type != PeriodType.SYSTEM:
            period = kwargs.get('period') or datetime.timedelta(seconds=self._timeout)
            count = kwargs.get('count') or 0
            count-=1
            task = Task(thread=thread, name=name, func=target, args=args, _async=_async, type=type, period=period,
                        timestamp=datetime.datetime.now(), count=count)
            self._tasks.append(task)
        thread.start()



    def scheduler(self):
        while True:
            print(threading.main_thread())
            # print(threading.current_thread())
            #
            print(id(self._tasks))
            print(self._tasks)
            print(id(self._tasks))

            for task in self._tasks:
                if task['thread']._is_stopped:

                    match task['type']:
                        case PeriodType.ONCE:
                            self._tasks.pop(self._tasks.index(task))
                        case PeriodType.COUNT:

                            if task['count'] > 0:
                                print(1)
                                if task['timestamp'] + task['period'] <= datetime.datetime.now():
                                    self.create_task(task['func'], task['args'], task['_async'], name=task['name'],
                                                 type=PeriodType.SYSTEM)
                                    task['timestamp']=datetime.datetime.now()
                                task['count'] -= 1
                            else:
                                self._tasks.pop(self._tasks.index(task))
                        case PeriodType.FOREVER:
                            if task['timestamp'] + task['period'] <= datetime.datetime.now():
                                self.create_task(task['func'], task['args'], task['_async'], name=task['name'],
                                                 type=PeriodType.SYSTEM)
                            task['timestamp'] = datetime.datetime.now()
            time.sleep(self._timeout)


def r():
    with open('tr.txt','a') as f:
        print(3)
        f.write('w')
        f.close()
if __name__ != "__main__":
    c_task = TaskController()
else:
    c_task = TaskController()
    c_task.create_task(r, name='qw', type=PeriodType.COUNT, period=datetime.timedelta(seconds=1), count=3)
    c_task.create_task(c_task.scheduler,name="Scheduler",type=PeriodType.SYSTEM)


