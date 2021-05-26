# Natlink

NatLink is an OpenSource extension module for the speech recognition program Dragon. It is required
for add on packages such as Unimacro, Vocola2, and Dragonfly.

This document describes how to instlall Natlink for end users and for developers.

## Status

Natlink code has been updated from Python 2 to Python 3. It is relatively stable, but not released per se as a stable release. You can use
it with Vocola2, Unimacro, etc. You can ask for
help in getting in working on the [KnowBrainer Forums](https://www.knowbrainer.com/forums/forum/categories.cfm?catid=25&entercat=y&CFTREEITEMKEY=25) forums if you have difficulty in getting Natlink, Unimacro, or Vocola2 working.

The packages are ccurrently published in the [Test Python Packaging Index](https://test.pypi.org/) rather than
the [Python Packaging Index](https://pypi.org/). The pip commands are a bit more complicated for this.

## Instructions for End Users

If you would like to install Natlink for use, but not as a developer, here are the instructions:

Install a [**Python 3.8 32 bit**](https://www.python.org/downloads/) on your system, and select install for **all users**.  
It is wise, but not required, to install python into a c:/python38 folder instead of c:/program files(x86)/... This will save
you a lot of typing and mouse clicking over the long run.

Start a command prompt as **adminstrator**. All command line actions described for end users must be performed in
a command shell with adminstrator privileges.

1. Upgrade pip immediately:

   - `pip install --upgrade pip`

2. Install natlink, Unimacro, and Vocola2 from [Test Python Packaging Index](https://test.pypi.org/). The following command will do that.  
   It will also pull any prequisites from the [Python Packaging Index](https://pypi.org/).

   - `pip install --no-cache --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple natlink unimacro vocola2`

   This will install the packages in your Python site-packages area. It will also add the following commands, which should be
   in your path now in your commmand prompt:

   - natlinkconfigfunctions
   - natlinkstatus
   - startnatlinkconfig

3. Run startnatlinkconfig to configure Natlink.

## Instructions for Developers

Your local git repository can be anywhere conveninent. It no longer needs to be in a specific location relative to other
[dictation-toolbox](https://github.com/dictation-toolbox) packages.

- Install as per the instructions for end users, to get any python prequisites in.
- Install [flit](https://pypi.org/project/flit/) `pip install flit`. This is a python package build tool that is required for developer workflow.
- Uninstall the packages you wish to develop. i.e pip if you want to work on natlink:
  `pip uninstall natlinkpy natlink` and answer yes to all the questions about removing files from your python scripts folder.
- Build the Python packages. In the root folder of your natlink repository, run `build_package` in your shell. This creates the package.  
  At this step, if you have any untracked files
  in your git repository, you will have to correct them with a `git add` command or adding those files to .gitignore.
- The cool part: `flit install --symlink'. This will install natlink into site-packages by symolically linking
  site-packages/natlink to the src/natlink folder of your git repository. You can edit the files in site-packages/natlink or
  in your git repository area as you prefer - they are the same files, not copies.

Oddly, when you follow this workflow and register natlink by running startnatlinkcofig or natlinkconfigfunctions, even though the
python paths those commands pickup, you will find that the natlinkcorepath will be in our git repository.

If you uninstall natlink, and install it with pip, and reregister natlink, you will find the core diretory is
reognized as a subfolder of site-packages.

### FAQ for compiling with Visual Studio

The Visual Studio project file needs to be set up to the specific location of your system Python install.

- Error: `Python.h: No such file or directory`
  You should be able to include dir that contains `Python.h`
  1. Right click on the Project `Properties -> Configuration Properties -> C/C++ -> General Menu`
  2. In the field `Additional Include Directories` add path `;C:\Users\Main\AppData\Local\Programs\Python\Python38-32\include\`

- Error: `LINK : fatal error LNK1104: cannot open file 'python38.lib'`
  1. Right click on the Project `Properties -> Linker -> Input`
  2. In the field `AdditionalDependencies` type `;C:\Users\Main\AppData\Local\Programs\Python\Python38-32\libs\python38.lib`
- Warning: `This function or variable may be unsafe when compling`
  1. Right click on the Project `Properties -> Configuration Properties -> C/C++ -> Preprocessor`
  2. In the field `PreprocessorDefinitions` add `;_CRT_SECURE_NO_WARNINGS` to turn those warnings off.

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

Version numbers of the packages must be increased before your publish to [Test Python Packaging Index](https://test.pypi.org/)
or [Python Packaging Index](https://pypi.org/). These are specified in **init**.py in `src/natlink`. Don't bother changing the
version numbers unless you are publishing.

This command will publish to [Test Python Packaging Index](https://test.pypi.org/): `publish_package_testpypi`.
This will publish to [Python Packaging Index](https://pypi.org/): `publish_package_pypy`.

If you are going to publish to a package index, you will need a .pypirc in your home directory. If you don't have one,
it is suggested you start with pypirc_template as the file format is rather finicky.
