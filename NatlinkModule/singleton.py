from weakref import WeakValueDictionary


class Singleton(type):
    _instances = WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # This variable declaration is required to force a
            # strong reference on the instance.
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MockObject(metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    m = MockObject()
    print(dict(Singleton._instances))
    del m
    print(dict(Singleton._instances))
