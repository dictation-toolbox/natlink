## {{{ http://code.activestate.com/recipes/573466/ (r4)
# From the recipe at http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/551761
# A backwards compatible enhancement has been made to allow full access to registry types still through the dictionary metaphor

"""Slightly magical Win32api Registry -> Dictionary-like-object wrapper

now based on winreg (QH, April 2020)
"""
import winreg
from collections import UserDict

class RegistryDict(UserDict):
    def __init__(self, keyhandle = winreg.HKEY_LOCAL_MACHINE, keypath = None, flags = None):
        """If flags=None, then it will create the key.. otherwise pass a winreg.KEY_* """
        UserDict.__init__(self)
        self.keyhandle = None
        self.open(keyhandle, keypath, flags)
        pass
    
    @staticmethod
    def massageIncomingRegistryValue(xxx_todo_changeme, bReturnType=False):
        (obj, objtype) = xxx_todo_changeme
        r=None
        if objtype == winreg.REG_BINARY and obj[:8]=='PyPickle':
            obj = obj[8:]
            r = (pickle.loads(obj), objtype)
        elif objtype == winreg.REG_NONE:
            r = (None, objtype)
        elif objtype in (winreg.REG_SZ, winreg.REG_EXPAND_SZ,
                         winreg.REG_RESOURCE_LIST, winreg.REG_LINK,
                         winreg.REG_BINARY, winreg.REG_DWORD,
                         winreg.REG_DWORD_LITTLE_ENDIAN, winreg.REG_DWORD_BIG_ENDIAN,
                         winreg.REG_MULTI_SZ):
            r = (obj,objtype)
        if r == None:
            raise NotImplementedError("Registry type 0x%08X not supported" % (objtype,))
        if bReturnType:
            return r
        else:
            return r[0]

    def __getitem__(self, key):
        bReturnType=False
        if (type(key) is tuple) and (len(key)==1):
            key = key[0]
            bReturnType=True
        # is it data?
        try:
            return self.massageIncomingRegistryValue(winreg.QueryValueEx(self.keyhandle, key),bReturnType)
        except:
            if key == '':
                # Special case: this dictionary key means "default value"
                raise KeyError(key)
            pass
        # it's probably a registry key then
        try:
            return RegistryDict(self.keyhandle, key, winreg.KEY_ALL_ACCESS)
        except:
            pass
        # must not be there
        raise KeyError(key)

    # def has_key(self, key):
    #     return self.__contains__(key)

    # def __contains__(self, key):
    #     try:
    #         self.__getitem__(key)
    #         return 1
    #     except KeyError:
    #         return 0

    # def copy(self):
    #     return dict(iter(self.items()))
    # 
    # def __repr__(self):
    #     return repr(self.copy())
    # 
    # def __str__(self):
    #     return self.__repr__()

    def __cmp__(self, other):
        # Do the objects have the same state?
        return self.keyhandle == other.keyhandle

    def __hash__(self):
        raise TypeError("RegistryDict objects are unhashable")

    def clear(self):
        keylist = list(self.keys())
        # Two-step to avoid changing the set while iterating over it
        for k in keylist:
            del self.data[k]

    def iteritems_data(self):
        i = 0
        # yield data
        try:
            while 1:
                s, obj, objtype = winreg.EnumValue(self.keyhandle, i)
                yield s, self.massageIncomingRegistryValue((obj, objtype))
                i += 1
        except:
            pass

    def iteritems_children(self, access=winreg.KEY_ALL_ACCESS):
        i = 0
        try:
            while 1:
                s = winreg.RegEnumKey(self.keyhandle, i)
                yield s, RegistryDict(self.keyhandle, [s], access)
                i += 1
        except:
            pass

    def iteritems(self, access=winreg.KEY_ALL_ACCESS):
       # yield children
        for item in self.iteritems_data():
            yield item
        for item in self.iteritems_children(access):
            yield item

    def iterkeys_data(self):
        for key, value in self.iteritems_data():
            yield key

    def iterkeys_children(self, access=winreg.KEY_ALL_ACCESS):
        for key, value in self.iteritems_children(access):
            yield key

    def iterkeys(self):
        for key, value in self.items():
            yield key

    def itervalues_data(self):
        for key, value in self.iteritems_data():
            yield value

    def itervalues_children(self, access=winreg.KEY_ALL_ACCESS):
        for key, value in self.iteritems_children(access):
            yield value

    def itervalues(self, access=winreg.KEY_ALL_ACCESS):
        for key, value in self.iteritems(access):
            yield value

    def items(self, access=winreg.KEY_ALL_ACCESS):
        return list(self.iteritems(access))

    def keys(self):
        return list(self.iterkeys())

    def values(self, access=winreg.KEY_ALL_ACCESS):
        return list(self.itervalues(access))

    def __delitem__(self, key):
        # Delete a string value or a subkey, depending on the type
        try:
            item = self.data[key]
        except:
            return  # Silently ignore bad keys
        itemtype = type(item)
        if itemtype in (str, int):
            winreg.DeleteValue(self.keyhandle, key)
            pass
        elif isinstance(item, RegistryDict):
            # Delete everything in the subkey, then the subkey itself
            winreg.DeleteKey(self.keyhandle, key)
        else:
            raise ValueError("Unknown item type in RegistryDict")
        del self.data[key]

    def __len__(self):
        return len(list(self.items()))

    def __iter__(self):
        return iter(self.keys())

    def popitem(self):
        try:
            k, v = next(iter(self.items()))
            del self.data[k]
            return k, v
        except StopIteration:
            raise KeyError("RegistryDict is empty")

    def get(self,key,default=None):
        try:
            return self.__getitem__(key)
        except:
            return default

    def setdefault(self,key,default=None):
        try:
            return self.__getitem__(key)
        except:
            self.__setitem__(key)
            return default

    def update(self,d):
        for k,v in list(d.items()):
            self.__setitem__(k, v)

    def __setitem__(self, item, value):
        item = str(item)
        pyvalue = type(value)
        if pyvalue is tuple and len(value)==2:
            valuetype = value[1]
            value = value[0]
        else:
            if pyvalue is dict or isinstance(value, RegistryDict):
                d = RegistryDict(self.keyhandle, item)
                d.clear()
                d.update(value)
                return
            if pyvalue is str:
                valuetype = winreg.REG_SZ
            elif pyvalue is int:
                valuetype = winreg.REG_DWORD
            else:
                valuetype = winreg.REG_BINARY
                value = 'PyPickle' + pickle.dumps(value)
        winreg.SetValueEx(self.keyhandle, item, 0, valuetype, value)
        self.data[item] = value

    def open(self, keyhandle, keypath, flags = None):
        if self.keyhandle:
            self.close()
        root = winreg.ConnectRegistry(None, keyhandle)
        if type(keypath) == str:
            keypath = keypath.split('\\')
        nextKey = root
        if flags in (None, winreg.KEY_ALL_ACCESS):
            for subkey in keypath:
                try:
                    nextKey = winreg.CreateKey(nextKey, subkey)
                except PermissionError:
                    raise KeyError("cannot create subkey %s, you probably need elevation (admin rights)"% subkey)
        else:
            for subkey in keypath:
                try:
                    nextKey = winreg.OpenKeyEx(nextKey, subkey)
                except:
                    raise KeyError("key not found (readonly): %s in %s"% (subkey, keypath))
        self.keyhandle = nextKey

    def close(self):
        try:
            winreg.RegCloseKey(self.keyhandle)
        except:
            pass

    def __del__(self):
        self.close()
## end of http://code.activestate.com/recipes/573466/ }}}





if __name__=='__main__':
    ##
    ##    try some of the functions and remove the TestRegistryDict section again.
    ##    in case of doubt, follow this in the regedit program...
    ##
    lm = RegistryDict(winreg.HKEY_LOCAL_MACHINE, r"Software\TestRegistryDictWinreg\TestSmall", flags=None)

    print('should start with empty dict: ', lm)
    lm['test'] = "abcd"
    print('should contain test/abcd: ', lm)
    lm['test'] = "xxxx"
    
    print('should contain test/xxxx: ', lm)

    ltest = RegistryDict(winreg.HKEY_LOCAL_MACHINE, r"Software\TestRegistryDictWinreg\TestSmall", flags=None)
    print('ltest should also contain test/abcd: ', ltest)
    pass

    del lm['test']
    print('should be empty again: ', lm)
    del lm['dummy']
    print('should be still empty: ', lm)
    print('--- now test int values (REG_DWORD)')
    lm['test'] = 1
    print('should contain: test/1', lm)
    lm['test'] = 0
    print('should contain: test/1', lm)
    del lm['test']
    print('should be empty again: ', lm)

    # now put a dict in:
    # lm['testdict'] = {"": "path/to/natlink", "Unimacro": "path/to/unimacro"}
    # print('should contain a dict with two items: ', lm)
    # del lm['testdict']
    # print('should be empty again: ', lm)

    ls = RegistryDict(winreg.HKEY_LOCAL_MACHINE,r"Software\TestRegistryDictWinreg")
    del ls['TestSmall']



