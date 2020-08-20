# Natlink

Natlink is a compatibility module for Dragon NaturallySpeaking (DNS) on Windows
that allows the user to run Python scripts that interact with DNS.
This fork does not include
 [Dragonfly](https://github.com/dictation-toolbox/dragonfly),
 [Unimacro, or Vocolo](https://qh.antenna.nl/unimacro/aboutunimacro/index.html).
These should be installed separately and included in the Natlink config as necessary.
The currently supported versions of Python are: 3.8-32, 3.7-32, and 3.6-32.

## Installation

Easy installation/uninstallation is one of the primary goals of this repository.
If you had to install any extra dependencies first in order to get it working,
please file a bug report.

To install:
 - Install Dragon NaturallySpeaking
 - Install Python (32 bit required), and make sure to check the box to add it to your PATH
 - Pip install your desired extra packages (e.g. dragonfly)
 - Download and run the Natlink installer
 - Put a .natlink file in your home directory (see example below)
 - Add your scripts
 - Start Dragon
  
To uninstall:
 - Run the uninstaller, 
    which will be found in the Natlink start menu entry or the installation directory.
  
## Configuration

Configuration is done in .natlink ini-style files.
Upon starting, Natlink will first look in the user's home directory for .natlink.
If no config is found there,
it will then look for .natlink in INSTALL_DIRECTORY\\natlink.
Here is an example config.

````ini
[directories]
# for most users, this section is all you need
my_scripts=C:\Users\user\dragonfly-scripts
system_wide_scripts=C:\Path\To\Shared\Scripts

[userenglish-directories]
only_loaded_if_profile_userenglish_active=C:\User\user\english-only-scripts

[userspanish-directories]
only_loaded_if_profile_userspanish_active=C:\User\user\spanish-only-scripts

[settings]
log_level=INFO
````

#### Section: \[directories\] (optional)
These are directories that Natlink will look for scripts to load in.
Each directory has a name that may be used for debugging purposes
and a value that is the absolute path to the directory.
The directories are loaded in the order they appear.
Scripts starting with an underscore and ending in .py (\_*.py)
will be imported in alphabetical order, except \_\_init\_\_.py will be
loaded first if it exists.
If no directories are listed or this section is omitted,
then no scripts will be loaded.

#### Section: \[\<user\>-directories\] (optional)
Same as \[directories\], but scripts are only loaded if the active user profile is \<user\>.
This section may be repeated any number of times for different users.
This is useful e.g. if you have multiple user profiles for different languages.
The relative load order between global and user directories is the order of appearance in the config.

#### Section: \[settings\] (optional)
The currently supported settings are:

- log_level: the log level to set the Natlink logger to. 
    Possible values are: CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG, NOTSET.
- load_on_begin_utterance (default: False): check for and load or reload any new or changed scripts at the beginning of each utterance.
- load_on_mic_on (default: True): check for and load or reload any new or changed scripts when the microphone state changes to "on". 
- load_on_startup (default: True): check for and load scripts as soon as Dragon loads Natlink.
- load_on_user_changed (default: True): check for and load scripts when the user profile changes.


## COM Module (C++)
The folder NatlinkSource, which contains all the C++ code, 
is for generating an in-process [Component Object Model (COM)](https://docs.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal)
server.
The output is natlink.pyd (a .pyd is essentially a .dll that is also a python module).
The natlink.pyd can be used both as a COM server or just as a plain python package.
When Dragon starts, it will start natlink.pyd, 
which does some setup and quickly passes things off to the Python side by importing natlinkmain.py.
A different version of natlink.pyd is compiled for each supported version of Python.

#### Compilation
To compile, run the CMakeLists.txt file from Visual Studio after selecting the desired Python.
CMake settings for different versions of Python are included in CMakeSettings.json.
You must be compiling in 32-bit release mode with debug info using the Microsoft Visual C++ compiler.
You must have the corresponding Python (and it must be 32 bit) already installed on your system.
Output will appear under out\\build\\\[PythonVersion\]\\NatlinkSource.

## Main (Python)
The Python layer is found in MacroSystem\\core.
The file natlinkmain.py is imported when Dragon starts,
and its job is to load the configuration files and then load any user scripts.

## Installer (Inno Setup)
The installer/uninstaller is compiled using [Inno Setup](https://jrsoftware.org/isinfo.php).
The inno setup script is found under the InstallerSource directory.
Make sure the Inno Setup compiler iscc.exe is in your PATH.
To compile, run the CMakeLists.txt file from Visual Studio after selecting the desired Python.
Output will appear under out\\build\\\[PythonVersion\]\\InstallerSource.
The installer executable is self-contained and may be distributed.


## Why 32-bit?
Currently Dragon NaturallySpeaking (up to version 15) is itself a 32-bit application and it is therefore
not possible for it to directly call a 64-bit .pyd.