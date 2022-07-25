#pylint:disable= C0114, C0115, C0116, W0401, W0614, W0621, W0108. W0212, R0201

import pytest

from natlinkcore.callbackhandler import CallbackHandler
    
class MakeFunctions:    
    def a1(self):
        print("a1")
    def a2(self):
        print("a2")
    def a3(self):
        b = 1/0
        print(f'a3: {b}')
    
def test_callbacks():
    """try to make an invalid function,
    by removing an instance that hold these functions.
    the function in question still remains valid as it seems.
    
    """
    functions1 = MakeFunctions()
    functions2 = MakeFunctions()
    cbh = CallbackHandler('test handler')
    print(cbh.info())
    assert len(cbh.callbacks) == 0
    cbh.set(functions1.a1)
    assert len(cbh.callbacks) == 1
    print(cbh.info())
    cbh.set(functions2.a1)
    assert len(cbh.callbacks) == 2
    print(cbh.info())
    cbh.run()
    print(cbh.info())
    assert len(cbh.callbacks) == 2
    
    # remove from functions1
    # only removint functions1 does not seem to have effect.
    cbh.delete(functions1.a1)
    cbh.run()
    assert len(cbh.callbacks) == 1
    print(cbh.info())
            
if __name__ == "__main__":
    pytest.main(['test_callbackhandler.py'])
