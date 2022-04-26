Developers instructions
=======================

Here come the instructions for developers

Setup Visual Studio environment
-----------------------------------

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


So issue#86_ is solved and explained with this all.


.. _issue#86: https://github.com/dictation-toolbox/natlink/issues/86

