"""CallbackHandler instances can handle callbacks (for Natlink, natlinkmain)$
"""
#pylint:disable=C0116, W0703
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
        if func not in self.callbacks:
            self.callbacks.insert(0, func)

    def delete(self, func):
        if func in self.callbacks:
            self.callbacks.remove(func)
            
    def run(self):
        for i in range(len(self.callbacks)-1, -1, -1):
            self._call_and_catch_all_exceptions(i)
            
            
            
    def _call_and_catch_all_exceptions(self, i: int) -> None:
        """call in reverse order, and remove if it raises an exception
        """
        fn = self.callbacks[i]
        try:
            fn()
        except Exception:
            del self.callbacks[i]
            print(traceback.format_exc())
           
if __name__ == "__main__":
    
    def a1():
        print("a1")
    def a2():
        print("a2")
    def a3():
        b = 1/0
        print(f'a3: {b}')
    
    cbh = CallbackHandler('test handler')
    print(cbh.info())
    cbh.set(a1)
    cbh.set(a3)
    cbh.set(a2)
    print(cbh.info())
    cbh.run()
    print(cbh.info())
    cbh.run()
    print(cbh.info())
            