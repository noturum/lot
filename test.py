class Singl:
    __inst__=None
    def __new__(cls, *args, **kwargs):
        if cls.__inst__:
            print('2')
            return cls.__inst__
        else:
            print('1')
            cls.__inst__=cls
            return cls
    def task(func):
        def move():
            for _ in range(10):
                print(func())
        return move
a=Singl()

@a.task
def r():
    return 2


