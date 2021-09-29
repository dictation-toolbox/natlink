
# Natlink 
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg) [![PyPI Version fury.io](https://badge.fury.io/py/natlink.svg)](https://pypi.org/project/natlink/) [![PyPI status](https://img.shields.io/pypi/status/natlink.svg)](https://pypi.python.org/pypi/natlink/)

NatLink is an OpenSource extension module for the speech recognition program [dragon](https://www.nuance.com/dragon.html). NatLink is required
for add on packages such as [Unimacro](https://github.com/dictation-toolbox/unimacro), [Vocola2](https://github.com/dictation-toolbox/Vocola2), and [Dragonfly](https://github.com/dictation-toolbox/dragonfly).


## Status

Natlink code has been updated from Python 2 to Python 3. It is relatively stable, but not released per se as a stable release. Only Dragonfly is supported at this time. Enabling Unimacro and Vocola(2) is not implemented. 

## Instructions for End Users

Preinstall requirements
- DNS 13, DPI 14, and DPI 15 or derivative of the same versions
- Install [**Python 3.8.X 32 bit**](https://www.python.org/downloads/release/python-3810/) on your system, and select **add Python to Path**.
- Make sure any previous versions of Natlink are unregistered and uninstalled. (Dragon must be close during that process)

Natlink Install via CLI

1. Close Dragon if open
2. Open cmd/power shell **as administrator**
3. Upgrade pip: `pip install --upgrade pip`
4. `pip install natlink` from [PyPI](https://pypi.org/project/natlink/)
5. `natlinkconfig_cli` # should auto setup and register itself.
6. Set natlink user directory: type `n C:\your-grammars-folder` Modify path to your dragonfly grammars.
7. Restart Dragon and "Messages from Natlink" window should start with Dragon.

Extra commands if needed
- type `u`  to see all CLI options
- type `r` or `R` register/unregister natlink
- type `e` or `E` enable/disable Natlink
- type `n` or `N` set/clear the natlink user directory

**Info**
- By default, config files for Natlink are stored in the `.natlink` subdirectory of the Home directory (something like `C:\Users\User`).
   - When you want to change this default location, specify a valid directory in the environment variable DICTATIONTOOLBOXUSER (for example `C:\Users\Your-User-Name\Documents\.natlink`).
     The `.natlink` directory (with config file `natlinkstatus.ini`) will be created in this directory.
   - If natlink is properly registered `natlink.pyd` file path location stored in `natlinkstatus.ini`

**Support**
 - Review current [issues](https://github.com/dictation-toolbox/natlink/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)
 - Join us on [![Gitter](https://badges.gitter.im/dictation-toolbox/natlink.svg)](https://gitter.im/dictation-toolbox/natlink?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Matrix](https://img.shields.io/matrix/caster:matrix.org?label=Matrix%20Chat&server_fqdn=matrix.org)](https://matrix.to/#/#dictation-toolbox_natlink:gitter.im&via=matrix.org)
 
**Troubleshooting** 
_On non-administrator accounts_:
- You may need to manually delete **natlink.pyd** as administrator after closing the CLI
- Running terminal as administrator changes the user account causing a mismatch between user directories between administrator/non-administrator. This impacts where your settings are stored for natlink.
   - Fix:- [Create an OS environment variable](https://phoenixnap.com/kb/windows-set-environment-variable) **DICTATIONTOOLBOXUSER** pointing to a directory to store `.natlink`. 


## Instructions for Developers

- Natlink and other packages are all installed as packages in (\python38-32)\Lib\site-packges. 
- As all packages (the root directory) are recognised in the PythonPath, we do not need a special reference in the registry any more, that
  points to the natlinkcore directory where natlink.pyd is copied to (in the natlinkconfig program) and registered.
- For all these packages we need qualified imports, for example:
=== from natlinkcore import natlink
=== from dtactions import sendkeys 

Your local git repository can be anywhere conveninent. It no longer needs to be in a specific location relative to other
[dictation-toolbox](https://github.com/dictation-toolbox) packages.

- Install as per the instructions for end users, to get any python prequisites in.
- Install [flit](https://pypi.org/project/flit/) `pip install flit`. This is a python package build tool that is required for developer workflow.
- Uninstall the packages you wish to develop. i.e pip if you want to work on natlink:
  `pip uninstall natlink` and answer yes to all the questions about removing files from your python scripts folder.
- Build the Python packages. In the root folder of your natlink repository, run `build_package` in your shell. This creates the package.  
  At this step, if you have any untracked files
  in your git repository, you will have to correct them with a `git add` command or adding those files to .gitignore.
- The cool part: `flit install --symlink'. This will install natlink into site-packages by symolically linking
  site-packages/natlink to the src/natlink folder of your git repository. You can edit the files in site-packages/natlink or
  in your git repository area as you prefer - they are the same files, not copies.

Oddly, when you follow this workflow and register natlink by running startnatlinkcofig or natlinkconfigfunctions, even though the
python paths those commands pickup, you will find that the natlinkcorepath will be in our git repository.

If you uninstall natlink, and install it with pip, and reregister natlink, you will find the core diretory is
recognized as a subfolder of site-packages.

### FAQ for compiling with Visual Studio

If you need to build natlinksource (the C++ code) refer to the readme.md in the NatlinkSource folder.

## Notes About Packaging for Developers

This is because there are import statements in macrosystem/core `import natlink`. So modules trying to import from a natlink folder break.
This is particularly problematic for scripts end-users might run while setting up natlink. This probably won't be resolved
by moving natlink.pyd to another folder or name.

The package is specified in `pyproject.toml` and built with [flit](https://pypi.org/project/flit/). The build_package command
(a batch file in the root folder of natlink) builds a source distribution.

Several scripts are specfied in pyproject.toml in the scripts section. Scripts are automatically generated
and placed in the python distribution "Scripts" folder. Those scripts are then available in the system path for
users to run. Note the `flit install --symlink` will install scripts as batchfiles; `pip install natlink ...` will install
scripts as .exe files.

Version numbers of the packages must be increased before your publish to  [Python Packaging Index](https://pypi.org/). These are specified in **init**.py in `src/natlink`. Don't bother changing the
version numbers unless you are publishing.

This will publish to [Python Packaging Index](https://pypi.org/): `publish_package_pypy`.

If you are going to publish to a package index, you will need a .pypirc in your home directory. If you don't have one,
it is suggested you start with pypirc_template as the file format is rather finicky.

### Debugging

A lot of extra diagnostic information is written using outputDebugString (```from pydebugstring.output import outputDebugString```).  
You can add extra diagnostic information to natlink or your own code and leave it in.  To view this diagnostic 
information you an use DebugView from https://docs.microsoft.com/en-us/sysinternals/.  There are some diagnostics for natlink startup that are always 
available if you start DebugView.

If you want to attach a python debugger, the instructions are in a word document "debugging python instructions.doc" in natlinkcore. 




