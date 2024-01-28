## Project Structure <!-- {docsify-ignore} -->

A high level overview Of how the Natlink project is structured.

#### COM Module (C++)

Located in `NatlinkSource`

The folder NatlinkSource, which contains all the C++ code, is for generating an in-process [Component Object Model (COM)](https://docs.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal) server. The output is `_natlink_core*.pyd` (a .pyd is essentially a .dll that is also a python module). The `_natlink_core*.pyd`. can be used both as a COM server or just as a plain python package. When Dragon starts, it will start natlink.pyd, which does some setup and quickly passes things off to the Python side by importing `natlinkmain.py`. (A different version of `_natlink_core*.pyd` is compiled for each supported version of Python.)

- `_natlink_core.pyd` Supports - DPI 15, 16

- `_natlink_core_legacy.pyd` Supports- DNS 13, DPI 14

#### Python Code

Very little Python is used in Natlink (this package). However, there is some python to provide a veneer over the functions exported in the natlink .pyd files and export them to as the "natlink" python package. 

`pythonsrc` contains `_natlink_core.pyi` Which is meant to provide introspection (for pylint etc) from the pyd file.

[NatlinkCore](https://github.com/dictation-toolbox/natlinkcore) is a sister project that contains the majority of Python code. NatlinkCore job is to load the configuration files and then load any user scripts From any supported project. NatlinkCore also as modules for interacting with Windows OS and parsing Natlink Grammars.

#### Installer (Inno Setup)

Located in `InstallerSource`

The Natlink installer/uninstaller is compiled using [Inno Setup](https://jrsoftware.org/isinfo.php) with a inno setup script.