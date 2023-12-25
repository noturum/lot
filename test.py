class Singl:
    def __init__(self):
        self.tasks=[]
    def task(self,t):
        def decorator(func):
            def wrapper():
                print(t)
                return func()
            return wrapper
        return decorator
a=Singl()

@a.task(20)
def rr():
    return 2
rr()
