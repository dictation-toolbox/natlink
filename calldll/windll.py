# -*- Mode: Python; tab-width: 4 -*-
#    Author: Sam Rushing <rushing@nightmare.com>

"""\
lets you call functions in win32 dll directly,
using the calldll module.

Usage:
To create a dll module object:
>>> kernel32 = windll.module ('kernel32')
>>> kernel32
<win32 module 'kernel32' (0 functions)>
To reference a function:
>>> kernel32.Beep
<callable function "Beep">
To call a function:
>>> kernel32.Beep (1000, 50)
"""

import calldll

# A convenience for the vast majority of functions which take long
# parameters (addresses or integers) and return a long.  Assumes that
# the caller knows the correct number of arguments!  If you use the
# wrong number of args it _will_ crash.  Be especially wary of extra
# arguments expected by 'X---Y--Ex' functions.

class callable_function:
    def __init__ (self, address, name=''):
        self.address = address
        self.name = name
        self.called = 0

    def __repr__ (self):
        return '<callable function "%s">' % self.name

    def __call__ (self, *args):

        self.called = self.called + 1
        return calldll.call_foreign_function (
            self.address,
            'l'*len(args),
            'l',
            args
            )
            
class module:
    callable_function_class = callable_function
    def __init__ (self, name, ext='.dll'):
        self.name = name
        self.handle = calldll.load_library (name+ext)
        if not self.handle:
            raise SystemError, "couldn't load module '%s'" % (name+ext)
        self.funs = {}
        self.loaded = 1

    def unload (self):
        if self.loaded and self.handle:
            self.funs = {}
        if calldll:
            calldll.free_library (self.handle)

    # this will never happen unless this module is deleted from
    # 'module_map' (see below).
    def __del__ (self):
        self.funs = {}
        self.unload()
        self.loaded = 0

    def __repr__ (self):
        return "<win32 module '%s' (%d functions)>" % (
            self.name,
            len(self.funs)
            )

    def __getattr__ (self, name):
        if not self.loaded:
            raise SystemError, "module has been unloaded!"
        # I wonder which is faster, using try/except or <has_key> ?
        try:
            return self.funs[name]
        except KeyError:
            addr = calldll.get_proc_address (self.handle, name)
            if addr:
                self.funs[name] = self.callable_function_class (addr, name)
            else:
                # try tacking on the 'ASCII' modifier
                addr = calldll.get_proc_address (self.handle, name+'A')
                if addr:
                    self.funs[name] = self.callable_function_class (addr, name)
                else:
                    raise AttributeError, 'GetProcAddress failed for %s' % name                
            return self.funs[name]

# cache modules
cmodule = module
module_map = {}
def module (name, ext='.dll'):
    full_name = name + ext
    if module_map.has_key (full_name):
        return module_map[full_name]
    else:
        mod = cmodule (name, ext)
        module_map[full_name] = mod
        return mod

class _dll:
    "Can I use some feature of the package system to make this work?"
    def __getattr__ (self, name):
        return module (name)

dll = _dll()

def dump_module_info():
    print '-'*20
    print 'WINDLL Function Call Stats:'
    for mod in module_map.values():
        print '--- %s ---' % mod
        fun_items = mod.funs.items()
        fun_items.sort()
        for name, fun in fun_items:
            print '%d\t%s' % (fun.called, name)

import string

class cstring: 
    immortal = {}

    def __init__ (self, s, length=0, remember=0):
        # make sure to zero-terminate the string
        if length > len(s):
            s = s + '\000' * (length - len(s))
        elif not s:
            s = '\000'
        elif s[-1] != '\000':
            s = s + '\000'
        self.mb = calldll.membuf (len(s))
        self.mb.write (s)
        if remember:
            cstring.immortal[self.mb] = 1

    def address (self):
        return self.mb.address()

    # Provides automatic conversion to an integer, for convenience.
    # This lets us pass in an object to call_foreign_function, rather
    # than calling 'address()' explicitly.

    __int__ = address

    def __len__ (self):
        # don't count the NULL char
        return self.mb.size() - 1

    def __del__ (self):
        del self.mb

    def strlen (self):
        # this could be certainly be more efficient. 8^)
        return len(self.trunc())

    def __repr__ (self):
        return "'%s'" % self.trunc()

    def __getitem__ (self, index):
        return self.value()[index]

    def value (self):
        return self.mb.read()

    def trunc (self):
        s = self.mb.read()
        i = string.find (s, '\000')
        if i != -1:
            return s[:i]
        else:
            return s

    def write (self, s):
        if len(s) >= self.mb.size()-1:
            raise ValueError, 'string too big for buffer'
        else:
            self.mb.write (s+'\000')

# compatibility
addressable_string = cstring

class membuf:
    def __init__ (self, initval=None):
        # initval can be either a length, or a string
        # [most likely packed by struct/npstruct]
        if type(initval) == type(0):
            self.mb = calldll.membuf (initval)
        elif type(initval) == type (''):
            self.mb = calldll.membuf (len (initval))
            self.mb.write (initval)

    def __len__ (self):
        return self.mb.size()

    def __getattr__ (self, attr):
        return getattr (self.mb, attr)

    def __int__ (self):
        return self.mb.address()

    def __getitem__ (self, index, size=1):
        return self.mb.read (index, size)

    def __setitem__ (self, index, value):
        self.mb.write (value, index)
