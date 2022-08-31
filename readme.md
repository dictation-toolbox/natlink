# Natlink

Natlink is a compatibility module for Dragon NaturallySpeaking (DNS/DPI) v13-v15 on Windows that allows the user to run Python scripts that interact with DNS.

This fork does not include
 [Dragonfly](https://github.com/dictation-toolbox/dragonfly),
 [Unimacro](https://qh.antenna.nl/unimacro/aboutunimacro/index.html).
 [Vocola](http://vocola.net/v2/default.asp).

These should be installed separately and included in the Natlink config as necessary.

## Installation

Easy installation/uninstallation is one of the primary goals of this repository.
If you had to install any extra dependencies first in order to get it working,
please file a bug report.

The currently supported versions of Python are: 3.9.x (32 bit required)

To install:
 - Install Dragon NaturallySpeaking
 - Download and run the [Natlink Installer](https://github.com/dictation-toolbox/natlink/releases): choose the most recent release. eg `natlink?.?.?-py3.10-32-setup.exe`.
    - if the supported 32 bit version of Python is not installed the Natlink installer will install it for you "off" system path
 - Configure natlink `natlink.ini` with:
    - the natlink config gui program: `natlinkconfig_gui.exe`, that auto launchs the end of the install 
 - Add your scripts the directory locations
 - Start Dragon

To Upgrade:
- The Nalink Project has two components NatlinkCore and a C++ COM Module. Most upgrades will be to NatlinkCore.
    - NatlinkCore can be upgraded independently from C++ COM Module.
    `py -3.10-32 -m pip install natlinkcore --upgrade`
    - The installer with COM Module should only change if there is a new version of Dragon Professional Individual/Dragon NaturallySpeaking or a C++ bug. 
    [Natlink Installer](https://github.com/dictation-toolbox/natlink/releases)

To Uninstall:
 - Run the uninstaller, via `Add or remove programs` 
    - Note: if you have used a used a pre-release natlink delete `C:\Program Files (x86)\Natlink`

## CLI Configuration
 - Run the Command Line Interface program `natlinkconfig_cli.exe`, that comes with the installer.
 - Type `u` to get a list CLI commands.
 - Set UserDirectory `n/N` e.g `n C:\Users\%UserProfile%\YourSripts`
 - `x/X` - enable/disable debug output of Natlink

 - Note: this program can also be used in batch mode.


## Manual Configuration
Configuration is done in .natlink ini-style files.
Upon starting, Natlink will first look in the user's home directory `C:\Users\%UserProfile%\.natlink` for `natlink.ini`. If no config is found there, it will use `natlink.ini` in `C:\Program Files (x86)\Natlink\DefaultConfig`

Here is an example config.

````ini
[directories]
vocoladirectory = vocola2
vocolagrammarsdirectory = natlink_userdir\vocolagrammars

[settings]
log_level = INFO
load_on_startup = True
load_on_begin_utterance = False
load_on_mic_on = True
load_on_user_changed = True

[manual configuration]
instruction1 = set next line in the directories section when you
instruction2 = want to define a Natlink user directory, independent of
instruction3 = any package, like Dragonfly, Unimacro or Vocola.
instruction4 = Note: you can drop a python grammar file in any of the directories,
instruction5 = the distinction is made for package updates, and for convenience
natlinkuserdirectory = ~\Documents\UserDirectory

[vocola]
vocolauserdirectory = ~\Documents\vocola_user
vocolatakeslanguages = True
vocolatakesunimacroactions = True

[previous settings]
log_level = DEBUG
dragonflyuserdirectory = ~\Documents\DragonflyUser
````


### Section: \[directories\] 
These are directories that Natlink will look for scripts to load in. Each directory has a name that may be used for debugging purposes and a value that is the absolute path to the directory. 

The directories are loaded in the order they appear. Scripts starting with an underscore and ending in .py (\_*.py) will be imported in alphabetical order, except \_\_init\_\_.py will be loaded first if it exists. If no directories are listed or this section is omitted, then no scripts will be loaded.

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


## Read the Docs
For more information, please goto [ReadTheDocs](https://natlink.readthedocs.io/en/latest/)



## COM Module (C++)
The folder NatlinkSource, which contains all the C++ code, 
is for generating an in-process [Component Object Model (COM)](https://docs.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal)
server. The output is `natlink.pyd` (a .pyd is essentially a .dll that is also a python module). 

The `natlink.pyd` can be used both as a COM server or just as a plain python package. When Dragon starts, it will start natlink.pyd, which does some setup and quickly passes things off to the Python side by importing `natlinkmain.py`.

*NOTE: Currently, a version tested for v13 and 14/15 is provided.*
(A different version of `natlink.pyd` is compiled for each supported version of Python)

## Python Code
Very little Python is used in natlink (this package).  See the note on  [NatlinkCore](#NatlinkCore).  

However, there is some python to provide a veneer over the functions exported in the natlink .pyd files and export them to as the "natlink" python package.  
Presently the entire python for natlink is in NatlinkSource/__init__.py


#### Compilation
To compile, run the `CMakeLists.txt` file from Visual Studio 2019 after selecting the desired Python. Or, use Visual Studio Code CMake extension. First configure for a compiler version, known as a kit. It must be specified (by suffix) to force crosscompilation from amd64 to x86, that is from 64-bit to 32-bit. This is a CMAKE configuration setting.

After configuration, the build system is generated in the  `build` directory created as the only thing that's changed in the source directoy. At this point, `build` contains all information that relates to the actual build process, such as choice of compilers, build flags, settings configured by CMAKE, and of course the Visual Studio project files. Now, the build can be initated after choosing the 'Debug' variant. The 'Debug' subdirectories in the build tree will be populated by object code and the Python code that is to be part of the installation.  Also, the installer phase of the build wraps everything up in the distributable executable.

CMake settings for different versions of Python are included in `CMakeSettings.json`.

You must have the corresponding Python (and it must be 32 bit) already installed on your system.  

#### Updating after Compilation or Python Edit

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

## NatlinkCore
[NatlinkCore](https://pypi.org/project/natlinkcore/) the Python layer is found in MacroSystem\\core. The file natlinkmain.py is imported when Dragon starts, and its job is to load the configuration files and then load any user scripts.

## Installer (Inno Setup)
The installer/uninstaller is compiled using [Inno Setup](https://jrsoftware.org/isinfo.php).
The inno setup script is found under the InstallerSource directory.
Make sure the Inno Setup compiler iscc.exe is in your PATH.
To compile, run the CMakeLists.txt file from Visual Studio after selecting the desired Python. The installer will appear as `\build\InstallerSource\natlinkX.X-pyY.Y-32-setup.exe`  The installer executable is self-contained and may be distributed.



## Why 32-bit?
Currently Dragon NaturallySpeaking (up to version 15) is itself a 32-bit application and it is therefore not possible for it to directly call a 64-bit .pyd.
