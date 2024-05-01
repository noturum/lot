import asyncio
import time
from inspect import iscoroutinefunction as is_async
from threading import Thread
from datetime import datetime, timedelta
from enum import Enum


class PeriodType(Enum):
    ONCE = 0
    FOREVER = 1
    COUNT = 2
    SYSTEM = 3


class Task:
    def __init__(self, period_type: PeriodType,
                 func, func_args=(),
                 name=None, count=1,
                 period: timedelta = timedelta(seconds=1)):

        self.period_type = period_type
        self.func = func
        self.args = func_args
        self.name = name
        self.period = period
        self.count = count
        self.timestamp = None
        self.thread = None

    def _add_loop(self, func, args):
        with asyncio.Runner(debug=False) as r:
            r.run(func(*args))


    def run(self):
        self.timestamp = datetime.now()
        if is_async(self.func):
            thread = Thread(target=self._add_loop, args=(self.func, self.args), daemon=True)
        else:
            thread = Thread(target=self.func, args=self.args, daemon=True)
        thread.start()


class TaskController:
    __inst__ = None

    def __new__(cls, *args, **kwargs):
        if not cls.__inst__:
            cls.__inst__ = super().__new__(cls)
        return cls.__inst__

    def __init__(self):

        self._tasks: list[Task] = []
        self._timeout: int = 1

    @property
    def _break(self):
        time.sleep(self._timeout)
        return True

    def create(self, task: Task):
        self._tasks.append(task)
        task.run()

    def scheduler(self):
        while True:
            for task in self._tasks:
                match task.period_type:
                    case PeriodType.ONCE:
                        self._tasks.pop(self._tasks.index(task))
                    case PeriodType.COUNT:
                        if task.count > 0:
                            if (datetime.now() - task.timestamp) >= task.period:
                                task.count -= 1
                                self._tasks.pop(self._tasks.index(task))
                                self.create(task)
                        else:
                            self._tasks.pop(self._tasks.index(task))
                    case PeriodType.FOREVER:
                        if (datetime.now() - task.timestamp) >= task.period:
                            self._tasks.pop(self._tasks.index(task))
                            self.create(task)
                        task.timestamp = datetime.now()
                time.sleep(self._timeout)




if __name__ == "__main__":
    c_task = TaskController()
    task = Task(PeriodType.SYSTEM, c_task.scheduler, name='SH')
    c_task.create(task)
    while 1:
        ...
else:
    c_task = TaskController()
    task = Task(PeriodType.SYSTEM, c_task.scheduler, name='SH')
    c_task.create(task)
