# Microsoft Developer Studio Project File - Name="natlink" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Dynamic-Link Library" 0x0102

CFG=natlink - Win32 Debug
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "natlink.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "natlink.mak" CFG="natlink - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "natlink - Win32 Debug" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE "natlink - Win32 Release MinDependency" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE "natlink - Win32 Inhouse Release" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 1
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "natlink - Win32 Debug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir "Debug"
# PROP BASE Intermediate_Dir "Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 1
# PROP Output_Dir "..\MacroSystem"
# PROP Intermediate_Dir "Debug"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MTd /W3 /Gm /Zi /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_USRDLL" /Yu"stdafx.h" /FD /c
# ADD CPP /nologo /MTd /W3 /Gm /ZI /Od /I "e:\Python\Include" /I "c:\Python\include" /I "d:\Python\include" /I "e:\Python\include" /I "c:\Program Files\Python\include" /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_USRDLL" /Yu"stdafx.h" /FD /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /o "NUL" /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /o "NUL" /win32
# ADD BASE RSC /l 0x409 /d "_DEBUG"
# ADD RSC /l 0x409 /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /subsystem:windows /dll /debug /machine:I386 /pdbtype:sept
# ADD LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /subsystem:windows /dll /incremental:no /debug /machine:I386 /pdbtype:sept /libpath:"c:\Python\libs" /libpath:"d:\Python\libs" /libpath:"e:\Python\libs" /libpath:"c:\Program Files\Python\libs"
# Begin Custom Build - Registering ActiveX Control...
OutDir=.\..\MacroSystem
TargetPath=\Programs\PBV Kit\Natlink\MacroSystem\natlink.dll
InputPath=\Programs\PBV Kit\Natlink\MacroSystem\natlink.dll
SOURCE="$(InputPath)"

"$(OutDir)\regsvr32.trg" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	regsvr32 /s /c "$(TargetPath)" 
	echo regsvr32 exec. time > "$(OutDir)\regsvr32.trg" 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "natlink - Win32 Release MinDependency"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "ReleaseMinDependency"
# PROP BASE Intermediate_Dir "ReleaseMinDependency"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "..\MacroSystem"
# PROP Intermediate_Dir "ReleaseMinDependency"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MT /W3 /O1 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_USRDLL" /D "_ATL_STATIC_REGISTRY" /D "_ATL_MIN_CRT" /Yu"stdafx.h" /FD /c
# ADD CPP /nologo /MT /W3 /O1 /I "c:\Programs\Python23\include" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_USRDLL" /D "_ATL_STATIC_REGISTRY" /Yu"stdafx.h" /FD /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /o "NUL" /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /o "NUL" /win32
# ADD BASE RSC /l 0x409 /d "NDEBUG"
# ADD RSC /l 0x409 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /subsystem:windows /dll /machine:I386
# ADD LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /subsystem:windows /dll /machine:I386 /libpath:"c:\Programs\Python23\libs"
# SUBTRACT LINK32 /pdb:none
# Begin Custom Build - Registering ActiveX Control...
OutDir=.\..\MacroSystem
TargetPath=\Programs\PBV Kit\Natlink\MacroSystem\natlink.dll
InputPath=\Programs\PBV Kit\Natlink\MacroSystem\natlink.dll
SOURCE="$(InputPath)"

"$(OutDir)\regsvr32.trg" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	regsvr32 /s /c "$(TargetPath)" 
	echo regsvr32 exec. time > "$(OutDir)\regsvr32.trg" 
	
# End Custom Build

!ELSEIF  "$(CFG)" == "natlink - Win32 Inhouse Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "natlink___Win32_Inhouse_Release"
# PROP BASE Intermediate_Dir "natlink___Win32_Inhouse_Release"
# PROP BASE Ignore_Export_Lib 0
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "..\MacroSystem"
# PROP Intermediate_Dir "InhouseRelease"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MT /W3 /O1 /I "c:\Python\include" /I "e:\Python\include" /I "d:\Python\include" /I "c:\Program Files\Python\include" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_USRDLL" /D "_ATL_STATIC_REGISTRY" /Yu"stdafx.h" /FD /c
# ADD CPP /nologo /MT /W3 /O1 /I "e:\Python\include" /I "c:\Python\include" /I "d:\Python\include" /I "c:\Program Files\Python\include" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_USRDLL" /D "_ATL_STATIC_REGISTRY" /D "INHOUSE" /Yu"stdafx.h" /FD /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /o "NUL" /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /o "NUL" /win32
# ADD BASE RSC /l 0x409 /d "NDEBUG"
# ADD RSC /l 0x409 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /subsystem:windows /dll /machine:I386 /libpath:"c:\Python\libs" /libpath:"e:\Python\libs" /libpath:"d:\Python\libs" /libpath:"c:\Program Files\Python\libs"
# ADD LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /subsystem:windows /dll /machine:I386 /libpath:"c:\Python\libs" /libpath:"d:\Python\libs" /libpath:"e:\Python\libs" /libpath:"c:\Program Files\Python\libs"
# Begin Custom Build - Registering ActiveX Control...
OutDir=.\..\MacroSystem
TargetPath=\Programs\PBV Kit\Natlink\MacroSystem\natlink.dll
InputPath=\Programs\PBV Kit\Natlink\MacroSystem\natlink.dll
SOURCE="$(InputPath)"

"$(OutDir)\regsvr32.trg" : $(SOURCE) "$(INTDIR)" "$(OUTDIR)"
	regsvr32 /s /c "$(TargetPath)" 
	echo regsvr32 exec. time > "$(OutDir)\regsvr32.trg" 
	
# End Custom Build

!ENDIF 

# Begin Target

# Name "natlink - Win32 Debug"
# Name "natlink - Win32 Release MinDependency"
# Name "natlink - Win32 Inhouse Release"
# Begin Group "Source Files"

# PROP Default_Filter "cpp;c;cxx;rc;def;r;odl;idl;hpj;bat"
# Begin Source File

SOURCE=.\appsupp.cpp
# End Source File
# Begin Source File

SOURCE=.\dictobj.cpp
# End Source File
# Begin Source File

SOURCE=.\DragCode.cpp
# End Source File
# Begin Source File

SOURCE=.\excepts.cpp
# End Source File
# Begin Source File

SOURCE=.\GramObj.cpp
# End Source File
# Begin Source File

SOURCE=.\inhouse.cpp

!IF  "$(CFG)" == "natlink - Win32 Debug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "natlink - Win32 Release MinDependency"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "natlink - Win32 Inhouse Release"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\natlink.cpp
# End Source File
# Begin Source File

SOURCE=.\natlink.def
# End Source File
# Begin Source File

SOURCE=.\natlink.rc

!IF  "$(CFG)" == "natlink - Win32 Debug"

!ELSEIF  "$(CFG)" == "natlink - Win32 Release MinDependency"

!ELSEIF  "$(CFG)" == "natlink - Win32 Inhouse Release"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\PythWrap.cpp
# End Source File
# Begin Source File

SOURCE=.\ResObj.cpp
# End Source File
# Begin Source File

SOURCE=.\SecdThrd.cpp
# End Source File
# Begin Source File

SOURCE=.\StdAfx.cpp
# ADD CPP /Yc"stdafx.h"
# End Source File
# End Group
# Begin Group "Header Files"

# PROP Default_Filter "h;hpp;hxx;hm;inl"
# Begin Source File

SOURCE=.\appsupp.h
# End Source File
# Begin Source File

SOURCE=.\comsupp.h
# End Source File
# Begin Source File

SOURCE=.\dictobj.h
# End Source File
# Begin Source File

SOURCE=.\DragCode.h
# End Source File
# Begin Source File

SOURCE=.\dspeech.h
# End Source File
# Begin Source File

SOURCE=.\excepts.h
# End Source File
# Begin Source File

SOURCE=.\GramObj.h
# End Source File
# Begin Source File

SOURCE=.\inh_com.h

!IF  "$(CFG)" == "natlink - Win32 Debug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "natlink - Win32 Release MinDependency"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "natlink - Win32 Inhouse Release"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\inhouse.h

!IF  "$(CFG)" == "natlink - Win32 Debug"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "natlink - Win32 Release MinDependency"

# PROP Exclude_From_Build 1

!ELSEIF  "$(CFG)" == "natlink - Win32 Inhouse Release"

!ENDIF 

# End Source File
# Begin Source File

SOURCE=.\ResObj.h
# End Source File
# Begin Source File

SOURCE=.\Resource.h
# End Source File
# Begin Source File

SOURCE=.\SecdThrd.h
# End Source File
# Begin Source File

SOURCE=.\speech.h
# End Source File
# Begin Source File

SOURCE=.\StdAfx.h
# End Source File
# End Group
# Begin Group "Resource Files"

# PROP Default_Filter "ico;cur;bmp;dlg;rc2;rct;bin;cnt;rtf;gif;jpg;jpeg;jpe"
# End Group
# Begin Source File

SOURCE=.\appsupp.reg
# End Source File
# End Target
# End Project
