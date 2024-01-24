from threading import Thread
class TaskController:
    __inst__ = None

    def __new__(cls, *args, **kwargs):
        if not cls.__inst__:
            cls.__inst__=super().__new__(cls)
        return cls.__inst__


    def __init__(self):
        self._tasks = []

    def add_task(self, func, *arg, name=None):

        self._tasks.append(task := (Thread(target=func, args=arg, name=name,daemon=False)))
        task.start()

    def stop(self, name):
        for task in self._tasks:
            if task.name == name and task.isAlive():
                task.join()

if __name__ !="__main__":
    c_task= TaskController()
