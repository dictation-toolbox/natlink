# Program Flow

This section documents how natlink is registered with Dragon and Windows, initialized and loaded by Dragon NaturallySpeaking.

The compiled dynamic link library `_natlink_core*.pyd` (which we call the natlink dll) is registered with natspeak as a COM-Server support module.

Dragon loads the natlink dll through a COM-Interface whenever Dragon started. 


When the natlink dll loads, it starts a Python interpreter and loads the natlinkcore  python modules.

Dragon itself provides a COM-Server which is called from the natlink dll. Python code in natlinkcore or various other packages that use natlinkcore can provide information to Dragon this way. Default location: `c:\program files (x86)\natlink\site-packages`

## Support module registration

First we need to register our COM-Server with the windows registry.
This is done by the installer. Windows will associate the path of the libary with the GUID that we choose for Natlink (`dd990001-bb89-11d2-b031-0060088dc929`) 
which will set the `HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\CLSID\{dd990001-bb89-11d2-b031-0060088dc929}\InprocServer32`for x64 systems.
Then we need to inform dragon of the new module. To do so we add

```ini
[.Natlink]
App Support GUID={dd990001-bb89-11d2-b031-0060088dc929}
```

to `C:\ProgramData\Nuance\NaturallySpeaking15\nsapps.ini` which also gives the module the identifier `.Natlink`
 
We can then activate/deactivate our support Module by either adding or removing `.Natlink=Default` it from the 
`[Global Clients]:` section of :  `C:\ProgramData\Nuance\NaturallySpeaking15\nssystem.ini`
As far as I can tell the value to the `.Natlink` key is irrelevant.
 
## COM-Server implementation
The natlink COM Server bridges between the COM subsystem Natlink expects, and the Python subsystem, so function calls can cross between them.  This bridge is primarily implemented in C++ and compiled into `_natlink_core*.pyd`.  Where it is easier, parts of this bridge are written in Python. It is a relatively small amount of Python actually in natlink, and it is in `src/natlink/__init__.py`.

The Python in __init__.py provides:
- some wrappers of the functions in the natlink dll, that encode Python strings to Windows Encoded Strings.   It is much easier to do the encodings Python than in C++. The Python version of the functions expect Python strings, and call the C++ versions with Windows Encoded Strings.   

- a context manager NatlinkConnector for managing the connection to Natlink.  



### `appsupp.h/appsupp.cpp`

Apparently we do not have access to the IDL (interface definition language) files. 

Indentation is important in the .reg file! I also remove my comments now .dll should work.

These files seem to implement the support interface defined in `COM/dspeech.h`.

## DLL initialization and python Interpreter

The Python Intrepreter is initialized in com/appsupp.cpp in a method
`STDMETHODIMP CDgnAppSupport::Register( IServiceProvider * pIDgnSite )`.

This method:
* Starts the Python intrepter
* Starts the natlinkcore subsystem.  


`TODO`

## COM-Python Wrapper
Does this have something to do with the Python system understanding where the inrpreter is?

The python natlink module is added to `HKEY_CURRENT_USER\SOFTWARE\WOW6432Node\Python\PythonCore\3.10\PythonPath`
as a Key/Subentry(?). This allows the sys module loader to find natlinkmain module.

As this library is loaded as support-module the working directory during runtime is that of the dragon system and
not the location of the library. Thus our python-module that we want to load from the library has to be
found through the `sys.path`.
