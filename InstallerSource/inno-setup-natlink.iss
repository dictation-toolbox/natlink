#define MyAppName "Natlink"
#ifndef MyAppVersion
  #define MyAppVersion "4.2"
#endif
#ifndef PythonVersion
  #define PythonVersion "3.8-32"
#endif
#define MyGUID "{{dd990001-bb89-11d2-b031-0060088dc929}"
#define Bits "32bit"
#ifndef SourceRoot
  #define SourceRoot ".."
#endif
#ifndef BinaryRoot
  #define BinaryRoot "..\out\build\3.8-32"
#endif

#define SitePackagesDir "{app}\site-packages"
#define CoreDir "{app}\site-packages\natlink"

[Setup]
AppId={#MyGUID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile={#SourceRoot}\LICENSE
OutputDir={#BinaryRoot}\InstallerSource
OutputBaseFilename=natlink{#MyAppVersion}-py{#PythonVersion}-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourceRoot}\natlink\*.py"; DestDir: "{#CoreDir}"; Flags: ignoreversion
Source: "{#SourceRoot}\natlink\*.pyi"; DestDir: "{#CoreDir}"; Flags: ignoreversion
Source: "{#BinaryRoot}\NatlinkSource\_natlink_core.pyd"; DestDir: "{#CoreDir}"; Flags: ignoreversion regserver {#Bits}

[Icons]
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Code]
var
  DragonIniPage: TInputDirWizardPage;


function BestGuessDragonIniDir(): String;
var
  TestDir: String;
begin
  Result := '';
  TestDir := ExpandConstant('{commonappdata}\Nuance\NaturallySpeaking15');
  if DirExists(TestDir) then
  begin
    Result := TestDir;
    exit;
  end;
  TestDir := ExpandConstant('{commonappdata}\Nuance\NaturallySpeaking14');
  if DirExists(TestDir) then
  begin
    Result := TestDir;
    exit;
  end;
  TestDir := ExpandConstant('{commonappdata}\Nuance\NaturallySpeaking13');
  if DirExists(TestDir) then
  begin
    Result := TestDir;
    exit;
  end;
  TestDir := ExpandConstant('{commonappdata}\Nuance\NaturallySpeaking12');
  if DirExists(TestDir) then
  begin
    Result := TestDir;
    exit;
  end;
end;

procedure InitializeWizard();
begin
  DragonIniPage := CreateInputDirPage(wpSelectDir, 'Select Dragon Ini Directory',
    'Where are the Dragon .ini files nsapps.ini and nssystem.ini stored? '+
    'Natlink must modify them to register Natlink as a compatibility module.',
    'To continue, click Next. If you would like to select a different folder, ' +
    'click Browse.', False, '');
  DragonIniPage.Add('');
  DragonIniPage.Values[0] := BestGuessDragonIniDir();
end;



function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = wpSelectDir) then
  begin
    if not FileExists(DragonIniPage.Values[0]+'\nsapps.ini') then
    begin
      MsgBox('nsapps.ini not found in that directory', mbError, MB_OK);
      Result := False;
      exit;
    end;
    if not FileExists(DragonIniPage.Values[0]+'\nssystem.ini') then
    begin
      MsgBox('nssystem.ini not found in that directory', mbError, MB_OK);
      Result := False;
      exit;
    end;
  end;
end;

function IsAppRunning(const FileName : String): Boolean;
var
    FSWbemLocator: Variant;
    FWMIService   : Variant;
    FWbemObjectSet: Variant;
begin
    Result := False;
    FSWbemLocator := CreateOleObject('WBEMScripting.SWBEMLocator');
    FWMIService := FSWbemLocator.ConnectServer('', 'root\CIMV2', '', '');
    FWbemObjectSet :=
      FWMIService.ExecQuery(
        Format('SELECT Name FROM Win32_Process Where Name="%s"', [FileName]));
    Result := (FWbemObjectSet.Count > 0);
    FWbemObjectSet := Unassigned;
    FWMIService := Unassigned;
    FSWbemLocator := Unassigned;
end;

function IsDragonRunning(): Boolean;
begin
  Result := IsAppRunning('dragonbar.exe') or IsAppRunning('natspeak.exe')
end;

function CorrectPythonFound(): Boolean;
begin
  Result := RegKeyExists(HKLM, 'Software\Python\PythonCore\{#PythonVersion}')
end;

function InitializeSetup(): Boolean;
begin
  Result := True
  if not CorrectPythonFound() then
  begin
    MsgBox('Could not find Python {#PythonVersion}, aborting. '
    + 'Please install this Python then try again.', mbError, MB_OK );
    Result := False;
    exit;
  end;
  if IsDragonRunning() then
  begin
    MsgBox('Dragon is running, aborting. '
    + 'Please close dragonbar.exe and/or natspeak.exe then try again.', mbError, MB_OK );
    Result := False;
    exit;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True
  if IsDragonRunning() then
  begin
    MsgBox('Dragon is running, aborting. '
    + 'Please close dragonbar.exe and/or natspeak.exe then try again.', mbError, MB_OK );
    Result := False;
    exit;
  end;
end;

function GetDragonIniDir(Param: String): String;
begin
  Result := DragonIniPage.Values[0];
end;



[Registry]
Root: HKLM; Subkey: "Software\{#MyAppName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "installPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "coreDir"; ValueData: "{#CoreDir}"
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "sitePackagesDir"; ValueData: "{#SitePackagesDir}"
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "dragonIniDir"; ValueData: "{code:GetDragonIniDir}"
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "version"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "Software\Python\PythonCore\{#PythonVersion}\PythonPath\{#MyAppName}"; ValueType: string; ValueData: "{#SitePackagesDir}"; Flags: uninsdeletekey

[INI]                                                                                                                                                   
Filename: "{code:GetDragonIniDir}\nssystem.ini"; Section: "Global Clients"; Key: ".{#MyAppName}"; String: "Python Macro System"; Flags: uninsdeleteentry
Filename: "{code:GetDragonIniDir}\nsapps.ini"; Section: ".{#MyAppName}"; Key: "App Support GUID"; String: "{#MyGUID}"; Flags: uninsdeletesection