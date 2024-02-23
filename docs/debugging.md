# Debugging
This document describes how to get started debugging natlink, natlinkcore, or any other Python
code executed by Dragon through natlink.

- [debugging python executed by natlink](#py)
- [debugging natlink CPP](#cpp)
- [Debugging and Testing Without Dragon](#wod)
- [Unit Testing](#u)

## Suggested Workspace Setup

Consider creating a folder for your dictation related projects, where you git clone each project.
Save the workspace in the folder with your IDE.  

For example `c:\users\yourname\code\dt`, and git clone the projects you want to view in your editor or IDE into dt.

It is also helpful to add the [`.natlink`](./configure_natlink_manually.md) folder to your workspace, so you can quickly edit and view natlink.ini.

## Debugging Python {#py}

### Print-Style Debugging

For print-style debugging, please use the Python Logging module rather than print statements.  
That way we don't have erroneus print statements accidentally checked into the source tree.  

The logging output generally goes to the natlink console  display.  In certain circumstances it goes to [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview) using the [PyDebugString](https://pypi.org/project/pydebugstring/) Logging Handler. This is mainly useful for debug output that may need to be viewed before the natlink message window is ready. 

You can also use `outputDebugString`  from  [PyDebugString](https://pypi.org/project/pydebugstring/) to send information to [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview).  

### Debugging With a Debugger

#### Visual Studio Code

[Visual Studio Code](https://code.visualstudio.com/) can attach to natlink, and you can set breakpoints in natlinkcore or any other Python code executed by natlink.  Even if Visual Studio Code is not your preferred IDE, it is a good choice for debugging natlink grammars.

Visual Studio Code connets to natlink using the Debug Adapter Protocol ([DAP](https://microsoft.github.io/debug-adapter-protocol/)).  

Understand that if you enable DAP, you are opening a TCP/IP port on your computer.  You should understand the security risks involved with that and how to mitigate them in your circumstances.

To enable DAP, add or edit your  natlink.ini to include this section.  Change the port if you need to.
```
   [settings.debugadapterprotocol]

   dap_enabled = True
   dap_port = 7474
   dap_wait_for_debugger_attach_on_startup = False
```
dap_enabled must be true to enable Python debugging when natlink starts.   If you change natlink.ini, restart Dragon.

Here is the Visual Studio code page on debugging with Python:  https://code.visualstudio.com/docs/python/debugging

Create a launch configuration in one of the projects, where you plan to set a breakpoint, for Python debugger and 
default type of Remote Attach. 

Here is a sample launch.json, which you can copy into one if your Python projects .vscode folder (i.e. unimacro/.vscode).  

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Natlink Remote Attach",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 7474
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "${workspaceFolder}"
                }
            ]
        }
    ]
}
```

It is *super important* the pathMappings are as shown.  If the pathMappings don't match the source files, your breakpoints and debugging won't work.  In theory localRoot and remoteRoot can be on different paths or even computers, as long as they have identical copies of the source files.

If you want to try remote debugging, you can explore pointing
remoteRoot to the source code on another computer.  You can also explore using SSH for remote debugging https://code.visualstudio.com/docs/remote/ssh.
If you have any sucess with those, please update this documentation.

##### Debugging Python on Startup With Visual Studio Code

Set `dap_wait_for_debugger_attach_on_startup = True` in natlink.ini:

```
   [settings.debugadapterprotocol]

   dap_enabled = True
   dap_port = 7474
   dap_wait_for_debugger_attach_on_startup = True
```

natlink will hang waiting for a debugger to atttach, in startDap in the natlinkcore/loader module.

If you need to start the debugger even earlier than the call to natlinkcore/loader run(),    
you have to modify the natlinkcore code to call startDap, or copy and paste some code from startDap, 

#### Starting DAP During Your Natlink Session

Currently there is no user interface to start DAP during a session.  You need to have a  way to call natlinkcore/loader/startDap(), perhaps through a simple grammar you write.  


#### Other Debuggers for Python

There are a [number of Debuggers which support DAP](https://microsoft.github.io/debug-adapter-protocol/implementors/tools/), and should be able to connect with natlink without requiring code changes.

If your debugger/IDE is not on the list (Pycharm and Komodo are notably absent), you can try their own mechanisms for debugging a running process.  Most debuggers have some sort of way to do remote debugging or to debug a running process.

If you get something working for your favorite IDE, you may want to add a configuration section to natlink.ini with any options, and supporting code in natlinkcore/loader.py, and add some instructions here.  

### Debugging Natlink C++ {#cpp}
 

####  Diagnostics and Print Sytle Debugging

The C++ code uses OutputDebugString and the Python code uses OutputDebugString from  `from pydebugstring.output import outputDebugString` to write diagnostic output.  This diagnostic output doesn't require the Natlink window to be active, and can be left in production code so that it is available if there are issues to resolve.

To view the output of OutputDebugString, you can use [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview). The output will also be displayed in some debuggers if you have managed to attach one.

#### Attaching the Debugger to natlink
Todo.     

#### Which .PYD is loaded via registry

This will tell us what DLL to load.

`Computer\HKEY_CLASSES_ROOT\WOW6432Node\CLSID\{dd990001-bb89-11d2-b031-0060088dc929}\InprocServer32`

## Debugging/Testing Without Dragon {#wod}

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

## Unit Testing {#u}

If you are working on natlink and natlinkcore, if you are fixing a bug, try and reproduce it first with a unit test, and if you are adding features, write the test first, then the code.  natlincore and natlink use pytest.  For natlink, look in the natlink/pythonsrc/tests folder for tests.  For natlinkcore, look in natlinkcore/tests.

