#define MyGUID "{{dd990001-bb89-11d2-b031-0060088dc929}"
#define Bits "32bit"
#define SitePackagesDir "{app}\site-packages"
#define CoreDir "{app}\site-packages\natlink"
; It's important to look in the InstallPath subkey to check for installation
#define PythonInstallKey "Software\Python\PythonCore\" + PythonVersion + \
                          "-32\InstallPath" 
#define PythonPathMyAppNameKey "Software\Python\PythonCore\" + PythonVersion + \
                          "-32\PythonPath\" + MyAppName 

[Setup]
AppId={#MyGUID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableWelcomePage=no
LicenseFile={#SourceRoot}\LICENSE
OutputDir={#BinaryRoot}\InstallerSource
OutputBaseFilename=natlink{#MyAppVersion}-py{#PythonVersion}-32-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel2=Welcome to {#MyAppName} {#MyAppVersion} for%n%nDragon/NaturallySpeaking 13, 14 or 15.

;[Code]
#include "inno-code.iss"

[Files]
; No Python sources
; The _natlinkXX.pyd --- and programmatically choose the correct one for _natlink.pyd
Source: "{#BinaryRoot}\NatlinkSource\Debug\_natlink_core15.pyd"; DestDir: "{#CoreDir}"; \
  Flags: ignoreversion
Source: "{#BinaryRoot}\NatlinkSource\Debug\_natlink_core13.pyd"; DestDir: "{#CoreDir}"; \
  Flags: ignoreversion 
Source: "{#CoreDir}\_natlink_core{code:GetDragonVersion}.pyd"; DestDir: "{#CoreDir}"; DestName: "_natlink_core.pyd"; \
  Flags: ignoreversion external regserver {#Bits}

; Python dll: copy python3x.dll from Python installation to Natlink installation so it'll be
; dynamically linked at _natlink.pyd launch
Source: "{code:GetPythonInstallPath}\python{#PythonVersionNoDot}.dll"; DestDir: "{#CoreDir}"; \
  Flags: external ignoreversion; 
; Python sources
Source: "{#SourceRoot}\NatlinkSource\__init__.py"; DestDir: "{#CoreDir}"



[Icons]
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[INI]                                                    
Filename: "{code:GetDragonIniDir}\nssystem.ini"; Section: "Global Clients"; Key: ".{#MyAppName}"; \
  String: "Python Macro System"; Flags: uninsdeleteentry
Filename: "{code:GetDragonIniDir}\nsapps.ini"; Section: ".{#MyAppName}"; Key: "App Support GUID"; \
  String: "{#MyGUID}"; Flags: uninsdeletesection

[Registry]
Root: HKLM; Subkey: "Software\{#MyAppName}"; Flags: uninsdeletekey

Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "installPath"; ValueData: "{app}"

Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "coreDir"; ValueData: "{#CoreDir}"

Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "sitePackagesDir"; ValueData: "{#SitePackagesDir}"

; Register which Dragon software was found and where .ini files were changed
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "dragonIniDir"; ValueData: "{code:GetDragonIniDir}"

; Register 'natlink' version
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "version"; ValueData: "{#MyAppVersion}"

; Add a key for natlink COM server (_natlink_core.pyd) to find the Python installation
; If GetPythonInstallPath fails, then the error will be reported as per [Code] section
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "pythonInstallPath"; ValueData: "{code:GetPythonInstallPath}"; Flags: uninsdeletekey

; Register natlink with command line invocations of Python: the Natlink site packages directory
; is added as an additonal site package directory to sys.path during interpreter initialization.
; This code is a hack; we try to insert the key in both HKLM and HKCU -- at
; least one of them is going to fail. The problem is that the hive cannot
; be determined by a {code:...} construct.  Also, the "PrivilegesRequired"
; warning can be ignored: it pertains to the HKCU key. "Inno" is correct about complaining,
; because an installation for all-users don't make sense when only the Python install  of one user is 
; detected.
Root: HKLM; Subkey: "{#PythonPathMyAppNameKey}"; ValueType: string; ValueData: "{#SitePackagesDir}"; Flags: uninsdeletekey noerror
Root: HKCU; Subkey: "{#PythonPathMyAppNameKey}"; ValueType: string; ValueData: "{#SitePackagesDir}"; Flags: uninsdeletekey noerror

[Run]
Filename: "{code:GetPythonInstallPath}\\python.exe"; Parameters: "-m pip install --upgrade pip"; StatusMsg: "Upgrade pip..."
Filename: "{code:GetPythonInstallPath}\\Scripts\pip.exe"; Parameters: "install wxPython"; StatusMsg: "Installing wxPython..."
Filename: "{code:GetPythonInstallPath}\\python.exe"; Parameters: "{#SourceRoot}\NatlinkConfigure\natlinkconfigfunctions.py"; StatusMsg: "Configure Natlink..."
