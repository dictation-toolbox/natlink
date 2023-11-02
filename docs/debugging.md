# Debugging

### Debugging and Diagnostics

The C++ code uses OutputDebugString and the Python code uses OutputDebugString from  `from pydebugstring.output import outputDebugString` to write diagnostic output.  This diagnostic output doesn't require the Natlink window to be active, and can be left in production code so that it is avaialble if there are issues to resolve.

To view the output of OutputDebugString, you can use [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview). The output will also be displayed in some debuggers if you have managed to attach one.

### Which .PYD is loaded via registry

This will tell us what DLL to load.

`Computer\HKEY_CLASSES_ROOT\WOW6432Node\CLSID\{dd990001-bb89-11d2-b031-0060088dc929}\InprocServer32`

### Debugging Without Dragon

Whether or not you use the debugger, you need a python console to drive natlink.
You need some code to connect to natlink, run a command, and 
if you won't want your shell to hang, disconnect from natlink when you are done.
Type something like this in to a python console.

```python
import natlink as n
n.playString("naïve brachialis")
n.natDisconnect()
```

There are [samples](https://github.com/dictation-toolbox/natlink/tree/master/NatlinkSource/samples_for_interactive_debugging) you can copy and paste into your python console.

During developement you may wish to debug the C++ code with Visual Studio Code, without using dictation.  Use the script mentioned above to update 
`_natlink_core*.pyd`.

Create a Debug Configuration that looks something like this:

```json
 "configurations": [
             {
            "name": "Natlink (Windows) Launch",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "python.exe",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "console": "externalTerminal"
        },]
```

Launch it.  That will launch a python console somewhere.

In that python console, import natlink or whatever python you want to run.
`import natlink as n` Now, set breakpoints in your C++.  `pythwrap.cpp` is a good place to start.