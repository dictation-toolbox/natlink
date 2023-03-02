# Natlink

Natlink is a compatibility module for Dragon NaturallySpeaking (DNS/DPI) v13-v16 on Windows that allows the user to run Python scripts that interact with DNS. 

Documentation available at [natlink.reddthedocs.io](https://natlink.readthedocs.io/en/latest/) or in the documentation folder of the github repository.

The documention is not yet complete at [natlink.reddthedocs.io](https://natlink.readthedocs.io/en/latest/).  The remainder of this document contains information that  has not yet been introduced into [natlink.readthedocs.io](https://natlink.readthedocs.io/en/latest/):

## Editing Documentation
The documentation is in the documentation folder.  In that folder you can type
`pip install -r requirements.txt` which will bring in the tools that build the documentation 
from text files in that folder.

`make.bat html` will build the documentation.

# Section: \[directories\] 



Python packages can be specified by their name instead of full path to where the module was installed (tyically with pip).  pip can put packages in varying places difficult for end-users to local.  typically in c:/program files/.../site-packages or ~/AppData/.../site-packages.

For example

`unimacro=unimacro`

instead of 

`unimacro=C:\Users\Doug\AppData\Roaming\Python\Python39\site-packages\unimacro`
 

### Section: \[\<user\>-directories\] (optional)
Same as \[directories\], but scripts are only loaded if the active user profile is \<user\>.
This section may be repeated any number of times for different users.
This is useful e.g. if you have multiple user profiles for different languages.
The relative load order between global and user directories is the order of appearance in the config.

### Section: \[settings\] (optional)
The currently supported settings are:

- log_level: the log level to set the Natlink logger to. 
    Possible values are: CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET.
- load_on_begin_utterance (default: False): check for and load or reload any new or changed scripts at the beginning of each utterance.
- load_on_mic_on (default: True): check for and load or reload any new or changed scripts when the microphone state changes to "on". 
- load_on_startup (default: True): check for and load scripts as soon as Dragon loads Natlink.
- load_on_user_changed (default: True): check for and load scripts when the user profile changes.



## Python Code
Very little Python is used in natlink (this package).  See the note on  [NatlinkCore](#NatlinkCore).  

However, there is some python to provide a veneer over the functions exported in the natlink .pyd files and export them to as the "natlink" python package.  
Presently the entire python for natlink is in NatlinkSource/__init__.py



## Updating after Compilation or Python Edit

If you have a natlink installed, and just wish to update the _natlinkcore.pyd and .pdb from _natlinkcore15.pyd and __init__.py,
run the powershell scripts local_publish_15.ps1 in and administrative powershell to update. 

If you wish a different install location or pyd, pleasee copy local_publish_15.ps1 to a script update_natlink.ps1 and make edits.  update_natlink1.ps1 is in .gitignore so it won't be checked in to git.


## Debugging
### Debugging and Diagnostics
The C++ code uses OutputDebugString and the Python code uses OutputDebugString from  `from pydebugstring.output import outputDebugString` to write diagnostic output.  This diagnostic output doesn't require the Natlink window to be active, and can be left in production code so that it is avaialble if there are issues to resolve.

 To view the output of OutputDebugString, you can use [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview).  The output will also be displayed in some debuggers if you have managed to attach one.
### Debugging Without Dragon

Whether or not you use the debugger, you need a python console to drive natlink.
You need some code to connect to natlink, run a command, and 
if you won't want your shell to hang, disconnect from natlink when you are done.
Type something like this in to a python console.

`import natlink as n
n.natConnect()
 
n.playString("naïve brachialis")
n.natDisconnect()
`

There are samples you can copy and paste into your python console in the samples_for_interactive_debugging folder.



During developement you may wish to debug the C++ code with Visual Studio Code, without using dictation.  Use the script mentioned above to update 
natlinkcore.pyd/dbb.

Create a Debug Configuration that looks something like this:
`
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
        },
  `
Launch it.  That will launch a python console somewhere.

In that python console, import natlink or whatever python you want to run.
`import natlink as n`

Now, set breakpoints in your C++.  `pythwrap.cpp` is a good place to start.

### Debugging Without Dragon

If you know how to debug natlink when dragon is running, please update this section.

### which dragon

This will tell us what DLL to load.

Computer\HKEY_CLASSES_ROOT\WOW6432Node\CLSID\{dd990001-bb89-11d2-b031-0060088dc929}\InprocServer32
