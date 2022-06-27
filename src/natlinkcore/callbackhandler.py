"""CallbackHandler instances can handle callbacks (for Natlink, natlinkmain)$
"""
#pylint:disable=C0115, C0116, W0703, R0201
import traceback

class CallbackHandler:
    """callbacks can be set, unset (not necessary) and called
    
    The callbacks are inserted at 0, because they are "run" in reverse order.
    When a func raises an error, it is removed from the callbacks list.
    """
    def __init__(self, name):
        self.callbacks = []
        self.name = name
        
    def info(self):
        if self.callbacks:
            return f'{self.name}: {self.callbacks}'
        return f'{self.name}: empty'
        
    def set(self, func):
        if not callable(func):
            raise TypeError(f'callbackhandler "{self.name}", set: not a callable: {func}, (type: {type(func)})')
        if func not in self.callbacks:
            self.callbacks.insert(0, func)

    def delete(self, func):
        if func in self.callbacks:
            self.callbacks.remove(func)
        # else:
        #     print(f'{self.name}: not a callback function for this callbackhandler ({func})')
            
    def run(self):
        """call funcs in reverse order, and remove if it raises an exception
        """
        for i in range(len(self.callbacks)-1, -1, -1):
            self._call_and_catch_all_exceptions(i)
            
    def _call_and_catch_all_exceptions(self, i: int) -> None:
        fn = self.callbacks[i]
        try:
            fn()
        # except AttributeError:
        #     ## delete silently:
        #     del self.callbacks[i]
        except Exception:
            del self.callbacks[i]
            print(traceback.format_exc())
        
if __name__ == "__main__":
    class MakeFunctions:
        def __init__(self):
            self.text = ''
        def a1(self):
            self.text = 'a1'
            print("a1")
        def a2(self):
            self.text = 'a2'
            print("a2")
        def a3(self):
            self.text = 'a3'
            b = 1/0
            print(f'a3: {b}')
    
    functions1 = MakeFunctions()
    
    cbh = CallbackHandler('test handler')
    print(cbh.info())
    cbh.set(functions1.a1)
    print(cbh.info())
    functions1 = None
    cbh.run()
    print(cbh.info())
    
            