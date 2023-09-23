;debugging tip
;Run the setup.exe program with /LOG.  See inno setup docs.

#define MyGUID "{{dd990001-bb89-11d2-b031-0060088dc929}"
#define Bits "32bit"
#define SitePackagesDir "{app}\site-packages"
#define CoreDir "{app}\site-packages\natlink"
#define DistDir "{app}\dist"
#define WheelPath "{#DistDir}\{#PythonWheelName}"

;a well known SID for all users on a system.
;on an english system, (Get-LocalGroup users).SID will return this SID 
#define AllowedUsersSid "S-1-5-32-545"   

; It's important to look in the InstallPath subkey to check for installation
#define PythonInstallKey "Software\Python\PythonCore\" + PythonVersion + \
                          "-32\InstallPath" 
#define PythonPathMyAppNameKey "Software\Python\PythonCore\" + PythonVersion + \
                          "-32\PythonPath\" + MyAppName 
[Dirs]
;we would like all users to read and execute these folders.
;note pip replaces with what it thinks the permissions should be
;so we need an extra setp in [Run] to restore all users read and execute.
Name:  {#CoreDir}; Permissions: users-readexec
Name:  {#SitePackagesDir}; Permissions: users-readexec
Name: {#DistDir}; Permissions: users-readexec


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

#define NatlinkCorePyd "{code:GetGetPydName}"
#define PythonInstallPath "{code:GetPythonInstallPath}"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel2=Welcome to {#MyAppName} {#MyAppVersion} for%n%nDragon/NaturallySpeaking 13, 14, 15 or 16.

;[Code]
#include "inno-code.iss"

[Files]
; Just a wheel file for natlink.
Source: "{#PythonWheelPath}"; DestDir: "{#DistDir}"; \
  Flags: ignoreversion

;how registration was working before.  but it renamed the pyd and this created
;problems when developing.  
;Source: "{#CoreDir}\{#NatlinkCorePyd}"; DestDir: "{#CoreDir}"; DestName: "_natlink_core.pyd"; \
;  Flags: ignoreversion external regserver {#Bits}


[Icons]
Name: "{group}\Configure Natlink via GUI"; Filename: "{#PythonInstallPath}\\Scripts\\natlinkconfig_gui.exe"; WorkingDir: "{#PythonInstallPath}\\Scripts"
Name: "{group}\Configure Natlink via CLI"; Filename: "{#PythonInstallPath}\\Scripts\\natlinkconfig_cli.exe"; WorkingDir: "{#PythonInstallPath}\\Scripts"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\Natlink Python Environment"; Filename: "{app}\python_environment.bat"; WorkingDir: "{app}"

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

; Add a key for natlink COM server (_natlink_corexx.pyd) to find the Python installation
; If GetPythonInstallPath fails, then the error will be reported as per [Code] section
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "pythonInstallPath"; ValueData: "{#PythonInstallPath}"; Flags: uninsdeletekey

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
;debugging tip for this section:  Run the setup.exe program with /LOG.  See inno setup docs.

;register the pyd for corresponding version of Python
Filename: "{#PythonInstallPath}\\Scripts\\pip.exe"; Parameters: "-m pip install --upgrade pip"; StatusMsg: "Upgrade pip..."
Filename: "{#PythonInstallPath}\\Scripts\\pip.exe"; Parameters: "install --target ""{#SitePackagesDir}""  --upgrade ""{app}/dist/{#PythonWheelName}"" "; StatusMsg: "natlink {#PythonWheelName}"

;pip changes the permissions on files and folders, so we have to redo them.  icacls is a built in windows program to change permissions.
;users need read and execute  

Filename: "icacls.exe";  Parameters: " ""{#SitePackagesDir}"" /t /grant *{#AllowedUsersSid}:RX "; StatusMsg: "icacls.exe"; 
Filename: "regsvr32";  Parameters: "-s \""{#CoreDir}\{#NatlinkCorePyd}\""" ; StatusMsg: "regsvr32 {#NatlinkCorePyd}"
Filename: "{#PythonInstallPath}\\Scripts\\pip.exe"; Parameters: "install --upgrade natlinkcore"; StatusMsg: "natlinkcore"

Filename: "{#PythonInstallPath}\\Scripts\\natlinkconfig_gui.exe"; Parameters: ""; StatusMsg: "Configure Natlink…"

[UninstallRun]
Filename: "regsvr32";  Parameters: "-s \""{#CoreDir}\{#NatlinkCorePyd}\""" ; StatusMsg: "regsvr32 -u {#NatlinkCorePyd}"
Filename: "{#PythonInstallPath}\\Scripts\\pip.exe"; Parameters: "uninstall --yes  natlinkcore natlink"; StatusMsg: "uninstall natlink"

