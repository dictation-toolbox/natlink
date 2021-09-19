# Goal

Create a minimal working version of Natlink a dragonspeak to python API. The immediate goal is to
create a more reliable 32-bit python 3.8 or later for dragon 13+ implementation that is easy to compile, understand and 
contribute to.

 

Later on the python 3 port as well as x64 support may be added. 
# important developer notes

natlink runs as  in process COM object hosted in a windows program.

make sure any Command Shell or Power Shell sessions are opened with administrator privileges (i.e. "run as administrator").  
Otherwise the regsvr32 command will fail without any useful error messages.



# PowerShell Prerequisite

Powershell is used from scripting things to put compiled output in the correct folders.  If you haven't used 
powershell before you need to run this in a powershell, after starting PowerShell as administrator:
```set-executionpolicy unrestricted```

You won't have to learn any powershell other than changing folders (cd, same as other shells) and running the 
scripts provided.

You can start Powershell from Windows or Visual Studio (using the "tools/command line" menu).  

Another  easy way to do this is to right click on "natlink" in the Solution Explorer and select "Open in Terminal".
It should open a Developer Powershell in natlinksource.  `cd ..` to move up one folder.


You can launch   a PowerShell from a command prompt by typing "powershell"

The powershell scripts you need to run are at the natlink project root.  Open an administrative powershell at this location, 
or change to that location, and keep it open.



#Installation Instructions.

IF you are building natlink.pyd locally with Visual studio, the easiest way to have dragon use your natlink.pyd is:
- install natlink with flit or pip.  As a developer, you should probably use flit.   See the development instrutions for the natlink package --
the are in the readme.md at the project root.
- make sure you have registered natlink already with `natlinkconfig_cli -r` or use the `natlinkconfig` GUI.
- use the ```cpnatlink_site_packages.ps1``` comand to copy the natlink.pyd you built (it will be in the debug Folder) to your python Lib/site-packages/natlinkcore folder.  No need to re-register.

# Important

Please avoid  goofing with the Visual Studio settings to customize to your local machine.  It needs to build
without confusion on any workstation. Your Python include header and lib files are found using an environment variable.

There is a DRAGON_VERSION to set in the preprocessor section of Visual Studio. DRAGON_VERSION preprocessor varaible are 13, 14 and 15 and version < 15 uses UNICODE.
Each version must be compiled per DNS/DPI version or natlink will crash at runtime.

If you have to recreate the visual studio project, be sure to set the runtime library option to ""Multi-threaded Debug (/MTd)""
or you will have problems distributing the natlink.pyd becuase of dependent dlls.

Please do not use a new version of Python than 3.8.  If we let IronPython catch up, we could potentially switch to that
and eliminate C++ altogther.


# Developer workflow

See compile instructions below.

You must install natlinkcore with flit or pip or some of the developer workflow will not work.  natlinkcore includes
some command lines and powershell scripts that are required.

Register natlink and get it working.  If you would like to use the command line, in an elevated commmand or powershell run:

`natlinkconfig_cli -r'.  Or run the GUI `natlinkconfig` from an elevated shell or as adminstrator from
Windows Explorer.   These programs will bein your Python   Scripts folder.


Once you compile the binaries will be in Debug/natlink.pyd (it is a DLL with a .pyd extension) and the debug symbols in Debug/natlink.pdb.

You do not need to reregister these binaries.  Just overwrite the binaries in your Python Lib/site-packages/natlinkcore
with the ```cpnatlink_site_packages``` command in powershell.



```
PS C:\Users\dougr\OneDrive\doug\codingprojects\dt\natlinkkb100\natlink> .\cpnatlink.ps1
Natlink binary C:\Users\dougr\OneDrive\doug\codingprojects\dt\natlinkkb100\natlink\NatlinkSource\Debug\natlink.pyd
copied natlink.dll and natlink.pyd to c:\python38-32\Lib\site-packages\natlinkcore
PS C:\Users\dougr\OneDrive\doug\codingprojects\dt\natlinkkb100\natlink>
```

When you have a  natlink.pyd ready to add to the natlinkcore package, 
```cpnatlink_to_python38_PYD.ps1``` will put the pyd  in the correct location, so that when the natlink
package is built with flit it will include it.


You must exit Dragon before running cpnatlink or you will get  errors.



# Compile instructions


Create a user or system environment variable "Natlink_Python" pointing to where you installed Python for natlink. If you have installed 
natlink already with pip, you can run pye_prefix to get the location if you don't know it:

```...\natlink> pye_prefix
c:\python38-32
```



THe easiest way to set the environment variable:   launch an adminstrative power shell,
change to the natlink project root folder, and run 
```setup_compile_environment.ps1```.  You must have already done a 'pip install natlink'.

You only have to set that variable once.






Currently only tested on windows 
- Visual Studio 2019 only.  

- Install python 3.8 **32  bit build** on your computer.  it is a good idea to install it 
   at c:\python38-32 rather than in c:\Program files (x86)\ to reduce the directory navigation requirements.  If you install just for 
   yourself rather than all users you will get a very long path like ```c:\users\dougr\appdata\local\programs\python\python38-32```.

   Be sure the location where you installed python (i.e. C:\Python38-32)  and the scripts directory (i.e. "C:\Python38-32\Scripts")
   are in your system path - either with the correct options at install time or edit the system path yourself.

 
 
- upgrade pip right away as  a good practice
- `pip install --upgrade pip`

If you did not install Python for all users, and pip is not available, rerun the installer and you will have an option to add pip.
 
 
Clone the natlink project with git to your computer if you haven't already.

 
The visual studio solution project file natlink.vxproj.  

  **At this time python virtualenvs are not supported for natlink building or deployment**
 

Double click on it natlink.vxproj with Visual Studio 2022.  

You should be able to build natlink.pyd.
It will appear in a   Debug subfolder.  See the workflow section above for how to 
use it as your natlink.pyd.

IF you want to include it in a package for others to use,  use ```cpnatlink_to_python38_PYD.ps1``  to put it in the right place in natlinkcore,
and rebuild the natlinkcore pthon package.

 
# Debugging

You can try and attached the Visual Studio debugger to natpspeak.exe or start natspeak.exe.
Either way we have had limited success - Visual Studio seems to hang altogether once
you hit a breakpoint.

Output can't be displayed on the natlink display window unless natlink is properly 
initialized.  Debug output clutters the display window anyway.

The solution is to use 'OutputDebugString' and you will see examples in the code.
You will need [DebugView](https://docs.microsoft.com/en-us/sysinternals/downloads/debugview)
to view and capture the output of OutputDebugString.

You can also send ouput to DebugView from python using

```from pydebugstring.output import outputDebugString```

and calling outputDebugString with any object.

You can leave your OutputDebugString calls in production code if 
they might help solve problems someone might come across.  


## Diagnostics

```.\check_com_registration.ps1 | more```

Will provide information about the Natlink COM registration, the start of which will look like this:  

```
checking the registration of the natlink COM objects


    Hive: HKEY_CLASSES_ROOT\WOW6432Node\CLSID\{dd990001-bb89-11d2-b031-0060088dc929}


Name                           Property
----                           --------
InprocServer32                 (default)      :
                               c:\users\dougr\appdata\local\programs\python\python38-32\lib\site-packages\natlinkcore\natlink.pyd
                               ThreadingModel : Apartment
Presenter
ProgID                         (default) : natlink.dragonsupport.1
Programmable
TypeLib                        (default) : {d1277b20-15d9-4f65-bacc-3e3257e89efd}
Version                        (default) : 1.0
VersionIndependentProgID       (default) : natlink.dragonsupport
checking the Python Core, make sure you are using the same version of Python as natlink


    Hive: HKEY_LOCAL_MACHINE\Software\Python\PythonCore

```

# Program flow


The compiled library natlink.pyd/natlink.dll is registered with natspeak as a COM-Server support module.
 This causes our library to be loaded through the COM-Interface whenever Dragon started.
 During the initialization of the library a Python interpreter it started which in turn loads the natlink python modules.
 All of this only starts python process to actually talk to dragons natspeak we need to go back into the library. 
 Dragon itself provides a COM-Server which we can call from the C++ libary. 
 These calls are wrapped into a Python/C API by the same library that just started the python process. 
 So the python process pulls back into that very same library to talk to natspeak.
 
 **TODO** Currently I am not sure how callbacks when a grammar is recognised by natspeak are handled.
 
 ### Support module registration
 
 the natlink class id is  `dd990001-bb89-11d2-b031-0060088dc929`.  


Note, natlinkconfigfunctions/natlinkconfigfunctions_cli do the registration as documented below:

 First we need to register our COM-Server with the windows registry. To do pass the dll/pyd to `regsvr32`. 
 Windows will associate the Natlink classid    
 which will set the ``HKEY_LOCAL_MACHINE\SOFTWARE\Classes\WOW6432Node\CLSID\{clsid}\InprocServer32``for x64 systems.
 
 Then we need to inform dragon of the new module by modifying the appropriate ini files. 
 
 this is done via the natlinkconfig_cli command or the natllinkconfig gui.   
  ```
[.Natlink]
App Support GUID={class id}
```
 to `C:\ProgramData\Nuance\NaturallySpeaking15\nsapps.ini` which also gives the module the identifier `.Natlink`
 
 We can then activate/deactivate our support Module by either adding or removing `.Natlink=Default` it from the 
 `[Global Clients]:` section of :  `C:\ProgramData\Nuance\NaturallySpeaking15\nssystem.ini`
 As far as I can tell the value to the `.Natlink` key is irrelevant.
 
 **TODO** figure out where the registration currently/previously takes place. I currently assume that it is 
 in``confignatlinkvocolaunimacro/natlinkconfigfunctions.py`` line 1045: ``registerNatlinkPyd()``
 
 ### COM-Server implementation

``CDgnAppSupport.cpp``  (used to be in ``appsupp.h/appsupp.cpp``)

Apparently we do not have access to the IDL (interface definition language) files. 

Indentation is important in the .reg file! I also remove my comments now .dll should work.

These files seem to implement the support interface defined in ``COM/dspeech.h``.

**TODO** The whole interface definition is littered with typdef. So I should go through and try to understand which methods are actually defined and what they do.
 
 ### DLL initialization and python Interpreter 
 ### COM-Python Wrapper

this section needs updating/correcting.
  
 The python natlink module is added to ``HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Python\PythonCore\2.7\PythonPath``
 as a Key/Subentry(?). This allows the sys module loader to find natlinkmain module.
 
 As this library is loaded as support-module the working directory during runtime is that of the dragon system and
 not the location of the library. Thus our python-module that we want to load from the library has to be
 found through the `sys.path`.