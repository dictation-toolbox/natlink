# Natlink

NatLink is an OpenSource extension module for the speech recognition program Dragon. It is required
for add on packages such as Unimacro, Vocola2, and Dragonfly.

This document describes how to install Natlink for end users and for developers.

## Status

Natlink code has been updated from Python 2 to Python 3. It is relatively stable, but not released per se as a stable release. 

Release 5.1.0 (August 1, 2021): should work reasonable for the UserDirectory users, so Dragonfly users could try this release. Note this release is done from the makeflitinstall branch.

For Unimacro and Vocola(2), please wait a little bit longer...

You can ask for help in getting in working on the [KnowBrainer Forums](https://www.knowbrainer.com/forums/forum/categories.cfm?catid=25&entercat=y&CFTREEITEMKEY=25) forums if you have difficulty in getting Natlink working.

The packages are currently published in the 
the [Python Packaging Index](https://pypi.org/). 

## Instructions for End Users

If you would like to install Natlink for use, but not as a developer, here are the instructions:

Install a [**Python 3.8 32 bit**](https://www.python.org/downloads/) on your system, and select install for **all users**.  
It is wise, but not required, to install python into a c:/python38-32 folder instead of c:/program files (x86)/... This will save
you a lot of typing and mouse clicking over the long run.

Start a command prompt or powershell as **adminstrator**. All command line actions described for end users must be performed in
a command shell with adminstrator privileges.

1. Check and upgrade pip immediately:
   
   - `pip -V   # should give something like:
              # pip 21.1 from c:\python38-32\lib\site-packages\pip (python 3.8)`
   - `pip install --upgrade pip`

2. Install natlink
   - Exit Dragon...
   - pip install natlink

   This will install the packages in your Python site-packages area. 
   It will also add the following commands, which should be
   in your path now in your commmand prompt:

   - natlinkconfig_cli
   - natlinkconfig

3. Change the location for the config files, if you wish
   - By default, config files for Natlink are stored in the `.natlink` subdirectory of the Home directory (something like `C:\Users\User`).
   - When you want to change this default location, specify a valid directory in the environment variable DICTATIONTOOLBOXUSER (for example `C:\Users\User\Documents\.dictationtoolbox`).
     The `.natlink` directory (with config file `natlinkstatus.ini`) will be created in this directory.

4. Run natlinkconfig to configure Natlink.
   - do a (re)register command, "r" in the natlinkconfig_cli
   - specify a UserDirectory, "u path-to-userdirectoery" in the natlinkconfig_cli

5. Start Dragon

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
