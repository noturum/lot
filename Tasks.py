import asyncio
import time

from threading import Thread


class TaskController:
    __inst__ = None

    def __new__(cls, *args, **kwargs):
        if not cls.__inst__:
            cls.__inst__ = super().__new__(cls)
        return cls.__inst__

    def __init__(self):
        self._tasks = []

    def add_task(self, func, *arg, _async=False, name=None):
        if _async:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            self._tasks.append(
                task := (Thread(target=(lambda func, arg: loop.run_until_complete(func(*arg)))(func, arg),
                                args=arg,
                                name=name,
                                daemon=False)))
            task.start()
            task.join()
        else:
            self._tasks.append(task := (Thread(target=func, args=arg, name=name, daemon=False)))
            task.start()

    def stop(self, name):
        for task in self._tasks:
            if task.name == name and not task.is_alive():
                task.join()

    def cleaner(self):
        while True:
            for task in self._tasks:
                if not task.is_alive():
                    task.join()
            time.sleep(100)


if __name__ != "__main__":
    c_task = TaskController()
    c_task.add_task(c_task.cleaner)
