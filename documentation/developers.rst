Developers instructions
=======================

When you want to contribute to the Natlink development, you will need to compile the C++ code and compile the inno setup program. Try the instructions below.

Setup Visual Studio Code environment
------------------------------------

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

      -  |image|

6. The ``build`` directory will generate containing the configuration
   selected and build artifacts (compiled code and installer)

   -  The ``build`` directory can be safely deleted if you need to
      reconfigure the project as it will just regenerate.

7. Click the "build" button at the bottom of the editor to to build the
   project and create the installer.

   -  |image|
   -  ``build`` directory Installer location
      ``{project source directory}\build\InstallerSource\natlink5.1-py3.10-32-setup.exe``

.. |image| image:: https://user-images.githubusercontent.com/24551569/164927468-68f101a5-9eed-4568-b251-0d09fde0394c.png
.. |image| image:: https://user-images.githubusercontent.com/24551569/164919729-bd4b2096-6af3-4307-ba3c-ef6ff3b98c41.png


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

