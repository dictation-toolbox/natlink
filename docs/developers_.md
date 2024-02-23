# Developers instructions

This document gives an overview of developing and 
debugging [natlink](https://github.com/dictation-toolbox/natlink), 
[natlinkcore](https://github.com/dictation-toolbox/natlinkcore), and 
Python executed by natlink such as user grammars.

The python modules of Natlink are in the  'natlinkcore' project. 

## Organizing Your workspace

Consider creating a folder for your dictation related projects, where you git clone each project.
For example `c:\users\yourname\code\dt`, and git clone the projects you want to view in your editor or IDE into dt.

It is also helpful to add the `.natlink`` folder to your workspace, so you can quickly edit and view natlink.ini, 
and any files natlink grammars might store there.   

If you are using Visual Studio Code, save the workspace in that folder.  

## Install Python Packages You Have Cloned.

Install each python package as local editable installs 
https://pip.pypa.io/en/stable/topics/local-project-installs/ with pip.  This allows the Python 
system to run the python code in your workspace rather than in the site-packages area. 

For example, from the workspace root, install dragonfly.

`C:\Users\doug\code\dt> pip install -e ./dragonfly``

or if you prefer, from the individual project root (Unimacro in this example):

`C:\Users\doug\code\dt\unimacro> pip install -e .[dev,test]`.  

The options  `[dev,test]` in the above example indicate pip should install the dependencies for development and test 
as well as the user code.  This will bring in any other python development tools, and libraries required to run any tests.  

If you are working on a module in dictation-toolbox, you should inspect pyproject.toml (if it exists) 
the in the project root and see if there are extra depencies in the `[project.optional-dependencies]` section,
and install them if they are available.  

## Building Python Packages 

If you wish to build a python package, in the project root diretory, use the [build](https://github.com/pypa/build) module, like this:

`C:\Users\doug\code\dt\natlinkcore> python -m build`

This will work regardless of whether the packaging is using [flit](https://github.com/pypa/flit), setuptools, Poetry, etc.  Using the  build instead of the underlying setuptools or flit commands is more robust.

If you get an error like this:
```PS C:\Users\doug\code\dt\natlinkcore> python -m build     
C:\Users\doug\AppData\Local\Programs\Python\Python310-32\python.exe: No module named build```

The just run `pip install build`.  Some of the python projects have added build to `[project.optional-dependencies]` section.  




### Debugging Natlink Python Code

### print-style debugging

For diagnostics and debugging, rather than using `print` statements, please using the [basic logging functions](https://docs.python.org/3/howto/logging.html#logging-basic-tutorial).  You are unlikely then to check in code with print statements you forgot to remove.  Just use something like `logging.debug("message")` and the output will only show in the natlink window
when the level is set to DEBUG in in natlink.ini.  The configured natlink debug levels are compatible with the Python logging module.


### Debug Adapters
IDEs usually have some sort of mechansim to allow debugging Python in a running process.  
Microsoft has one called the `Debug Adapter Protocol: https://microsoft.github.io/debug-adapter-protocol/`_ (DAP). It seems only Visual Studio Code currently supports this.  

Other IDEs have a simimilar mechanisms, and it may be possible to support them.  If you wish to support another IDE and have an idea how to connect your IDE to a running process, 
look in `natlinkcore/natlinkpydebug.py` for how support is implemented for the DAP.  Write a similar module for your favorite debugger.  You will also need to add a similar section to natlink.ini.

### Debugging with Visual Studio Code 

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

#### Debugging Python on Startup
In natlink.ini:

```
   [settings.debugadapterprotocol]

   dap_enabled = True
   dap_port = 7474
   dap_wait_for_debugger_attach_on_startup = False
```


## Compiling Natlink

You can skip this if you don't need to work on the C++ portion of natlink.

The 'glue' file between python code and 'Dragon', the heart if the 'Natlink' project is a `.pyd` file, which needs to be compiled from C++ code. With this compile step, also the 'inno setup program' is compiled.

When you want to contribute to python packages, look into the instructions there...

When you want to contribute to the Natlink development, you will need to compile the C++ code and compile the inno setup program. Try the instructions below.

### Setup Visual Studio Code environment

1. Install `Visual Studio <https://visualstudio.microsoft.com/>`__
   (Community Edition 2019 or above) with ``C++ Desktop Development``
   and ``Microsoft Visual C++ Redistributable``.

   -  `C++ Desktop
      Development <https://docs.microsoft.com/en-us/cpp/ide/using-the-visual-studio-ide-for-cpp-desktop-development>`__
      This contains the necessary compilers for **(Visual Studio** and
      **Visual Studio Code)**
   -  `Microsoft Visual C++ Redistributable 2015, 2017, 2019, and
      2022 <https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170>`__
      (32-bit/X86 required)

2. Install `Visual Studio Code <https://visualstudio.microsoft.com/>`__
   with the following Extensions

   -  `C/C++ <https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools>`__
   -  `CMake <https://marketplace.visualstudio.com/items?itemName=twxs.cmake>`__

3. Install `Inno <https://jrsoftware.org/isdl.php>`__ version 6.x.
4. Install `Python <https://www.python.org/downloads/>`__ version 3.8.x,
   3.9.x, or 3.10.x 32-bit/X86 (Does not need to be on path)
5. After cloning Nalink open the project up in Visual Studio Code

   -  Set the Python Version ``PYTHON_VERSION 3.10`` in
      `CMakeLists.txt <https://github.com/dictation-toolbox/natlink/blob/23b40fe23c0cb75c935cae6bc6800fa9cda748d9/CMakeLists.txt#L5>`__
      (The CMakeLists.txt in top directory of the project)

      -  example for Python 3.8.x
         ``set(PYTHON_VERSION 3.8 CACHE STRING "3.X for X >= 8")``

   -  Selective equivalent to
      ``Visual Studio Community 2022 Release - x86`` (32-bit/X86
      required) to configure the compiler.

      -  |image1|

6. The ``build`` directory will generate containing the configuration
   selected and build artifacts (compiled code and installer)

   -  The ``build`` directory can be safely deleted if you need to
      reconfigure the project as it will just regenerate.

7. Click the "build" button at the bottom of the editor to to build the
   project and create the installer.

   -  |image2|
   -  ``build`` directory Installer location
      ``{project source directory}\build\InstallerSource\natlink5.1-py3.10-32-setup.exe``

.. |image1| image:: https://user-images.githubusercontent.com/24551569/164927468-68f101a5-9eed-4568-b251-0d09fde0394c.png
.. |image2| image:: https://user-images.githubusercontent.com/24551569/164919729-bd4b2096-6af3-4307-ba3c-ef6ff3b98c41.png
Further instructions
--------------------




Invalid options Visual Studio
-----------------------------

When the C++ compile redistributale is wrongly configured, the program `dumpbinx.exe` reports a dependency, which is not wanted:

::

  PS C:\dt\NatlinkDoc\natlink\documentation> ."C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx86\x86\dumpbin.exe" /DEPENDENTS "C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd"
  Microsoft (R) COFF/PE Dumper Version 14.29.30136.0
  Copyright (C) Microsoft Corporation.  All rights reserved.
  
  
  Dump of file C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd
  
  File Type: DLL
  
    Image has the following dependencies:
  
      python38.dll
      KERNEL32.dll
      USER32.dll
      SHELL32.dll
      ole32.dll
      OLEAUT32.dll
      ADVAPI32.dll
      MSVCP140D.dll
      VCRUNTIME140D.dll
      ucrtbased.dll
      
  (...)

The `VCRUNTIME140D.dll` should not be there.

Fix
---

Static linking is established by installing:
https://docs.microsoft.com/en-us/cpp/c-runtime-library/crt-library-features?view=msvc-170&viewFallbackFrom=vs-2019

Also see "Bundling vc redistributables":
https://stackoverflow.com/questions/24574035/how-to-install-microsoft-vc-redistributables-silently-in-inno-setup


With install version 5.1.1  (with python 3.8), now the following output is given:

::

  (Powershell) ."C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx86\x86\dumpbin.exe" /DEPENDENTS "C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd"
  Dump of file C:\Program Files (x86)\Natlink\site-packages\natlink\_natlink_core.pyd
  
  File Type: DLL
  
    Image has the following dependencies:
  
      python38.dll
      KERNEL32.dll
      USER32.dll
      SHELL32.dll
      ole32.dll
      OLEAUT32.dll
      ADVAPI32.dll
  (...)


So issue#86(https://github.com/dictation-toolbox/natlink/issues/86) is hopefully solved and explained with this all.


.. _issue#86: https://github.com/dictation-toolbox/natlink/issues/86

