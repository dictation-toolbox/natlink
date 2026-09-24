# Compiling Instructions

When you want to contribute to the Natlink development, you will need to
compile the C++ code and compile the inno setup program. Try the
instructions below.

### Setup Visual Studio Code Environment

1. Install [Python](https://www.python.org/downloads/) version 3.10.x 32-bit/X86 (Does not need to be on path) 

2. Install [Visual Studio](https://visualstudio.microsoft.com/)
   (Community Edition 2019 or above) with `C++ Desktop Development` and
   `Microsoft Visual C++ Redistributable`.
   
   - [C++ Desktop Development](https://docs.microsoft.com/en-us/cpp/ide/using-the-visual-studio-ide-for-cpp-desktop-development) compilers for **(Visual Studio** and **Visual Studio Code)**
   - [Microsoft Visual C++ Redistributable 14.40.33816.0 (recommended) or above](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170) (32-bit/X86 required)

3. Install[cmake](https://cmake.org/download/) v3.31.0 (recommended) or above
4. Install [Visual Studio Code](https://visualstudio.microsoft.com/)
   with the following Extensions
   
   - [C/C++](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)
   - [CMake Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools)

5. Install [Inno](https://jrsoftware.org/isdl.php) version 6.x. - 
   - Inno Setup compiler iscc.exe needs to be sys PATH.

6.  Instally the pyproject-build command.   This builds python modules in isolated enironments.  A good idea to have on your system.
     You can install pipx https://pipx.pypa.io/stable/installation/ (also a good idea) then `pipx installl build`.  Or install build on any python on your system that will be in the path.  You can even use natlink's 32 bit python if you want, though it unecessarily brings build into that environment.

   
### Building Natlink

1. After cloning Natlink open the project up in Visual Studio Code
   - Set the Python Version `PYTHON_VERSION` in [CMakeLists.txt](https://github.com/dictation-toolbox/natlink/blob/master/CMakeLists.txt) in top directory of the project
   - example for Python 3.10.x `set(PYTHON_VERSION 3.10 CACHE STRING "3.X for X >= 10")`

2. Selective equivalent to`Visual Studio Community 2022 Release - x86` (32-bit/X86 required) to configure the compiler.
     - ![vs_x86.png](/images/vs_x86.png)

3. The `build` directory will generate containing the configuration
   selected and build artifacts (compiled code and installer)
   
   - The `build` directory can be safely deleted if you need to
     reconfigure the project as it will just regenerate.

4. Click the `build` button at the bottom of the editor to to build
   the project and create the installer.
   
   - ![build](/images/build.png)
5. The installer will appear as `\build\InstallerSource\natlinkX.X-pyY.Y-32-setup.exe` The installer executable is self-contained and may be distributed.

## Compiling FAQ

### How do I check for statically compiled C++ dependencies?

Microsoft Visual C++ Redistributable must be statically compiled. If not this can cause issues during runtime. Utilize `dumpbin.exe` to check if `VCRUNTIME140D.dll` Is listed as a dependency for the .pyd. See [this issue](https://github.com/dictation-toolbox/natlink/issues/86#issuecomment-1065217999) for a detailed explanation and walk-through

1. Make sure [Microsoft Visual C++ Redistributable 32 bit](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) is installed

2. Delete the `build` directory

3. Recompile

### How do I update after compilation or python edit?

If you have a natlink installed, and just wish to update the .pyd new `_natlink_core*.pyd` and `__init__.py`, run the powershell scripts `local_publish.ps1` in and administrative powershell to update. 

If you wish a different install location or pyd, pleasee copy `local_publish.ps1` to a script update_natlink.ps1 and make edits.  `update_natlink1.ps1` is in `.gitignore` so it won't be checked in to git.
