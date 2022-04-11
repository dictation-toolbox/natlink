"""implement a Singleton type

"""
#pylint:disable=C0115

import weakref 

class Singleton(type):
    _instances = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        if cls in cls._instances:
            try:
                the_ref = weakref.ref(cls._instances[cls])
            except KeyError:
                pass
            else:
                if the_ref:
                    # still a valid reference:
                    return cls._instances[cls]
            print(f'weakref is/was there, but ref is None: {cls}')
        # This variable declaration is required to force a strong reference on the instance.
        instance = super(Singleton, cls).__call__(*args, **kwargs)
        cls._instances[cls] = instance
        return cls._instances[cls]


class MockObject(metaclass=Singleton):
    #pylint:disable=R0903
    def __init__(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    #pylint:disable=W0212
    m = MockObject()
    print('one instance, m:')
    print(dict(Singleton._instances))
    del m
    print(dict(Singleton._instances))
    print('M and N')
    M = MockObject()
    N = MockObject()
    print(dict(Singleton._instances))
    del M
    print(dict(Singleton._instances))
    del N
    print(dict(Singleton._instances))
    
    
