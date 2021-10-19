[Code]

var
  DragonIniPage: TInputDirWizardPage;
  DownloadPage: TDownloadWizardPage;

  CancelWithoutPrompt: Boolean;
  DragonVersion: String;

procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  Confirm := not CancelWithoutPrompt;
end;

function BestGuessDragonIniDir(): String;
var
  TestDir: String;
begin
  Result := '';
  TestDir := ExpandConstant('{commonappdata}\Nuance\NaturallySpeaking15');
  if DirExists(TestDir) then
  begin
    Result := TestDir;
    DragonVersion := '15';
    exit;
  end;
  TestDir := ExpandConstant('{commonappdata}\Nuance\NaturallySpeaking14');
  if DirExists(TestDir) then
  begin
    Result := TestDir;
    DragonVersion := '13';
    exit;
  end;
  TestDir := ExpandConstant('{commonappdata}\Nuance\NaturallySpeaking13');
  if DirExists(TestDir) then
  begin
    Result := TestDir;
    DragonVersion := '13';
    exit;
  end;
end;

function GetDragonVersion(Param: String): String;
begin
  Result := DragonVersion;
end;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

function CorrectPythonFound(): Boolean;
begin
  Result := RegKeyExists(HKLM, '{#PythonInstallKey}') or
            RegKeyExists(HKCU, '{#PythonInstallKey}')
end;

function DoDownloadPage(): Boolean;
var
  ResultCode : Integer;
  command: String;
begin
    // the installation "failed" - at most we get Python
    // installed
    Result := False;
    DownloadPage.Clear;
    DownloadPage.Add('{#PythonInstallURL}', '{#PythonInstallExe}', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download; //  download to {tmp}
      except
        if DownloadPage.AbortedByUser then
          Log('Aborted by user.')
        else
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
          exit;
      end;
      command := ExpandConstant(
          '/C start /wait {tmp}\{#PythonInstallExe} /install /passive InstallAllUsers=1 Shortcuts=0');
      Result := Exec(ExpandConstant('{cmd}'), command, '', SW_SHOW, ewWaitUntilTerminated, ResultCode); 
      if not Result then
        MsgBox(ExpandConstant('{cmd} ') + command + 'resulted in: ' + 
                              SysErrorMessage(ResultCode), mbInformation, MB_OK );
    finally
      DownloadPage.Hide;
      exit;
    end;
end;

procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Font.Style := [fsBold];
  DragonIniPage := CreateInputDirPage(wpSelectDir, 'Select Dragon Ini Directory',
    'Where are the Dragon .ini files nsapps.ini and nssystem.ini stored? '+
    'Natlink must modify them to register Natlink as a compatibility module.',
    'To continue, click Next. If you would like to select a different folder, ' +
    'click Browse.', False, '');
  DragonIniPage.Add('');
  DragonIniPage.Values[0] := BestGuessDragonIniDir();
  
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing),
                                     SetupMessage(msgPreparingDesc),
                                     @OnDownloadProgress);

end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = wpWelcome then
  begin
    if not CorrectPythonFound() then
      try
        if MsgBox('Do you want to install Python? Press No to abort installer.' + #13 +
                '[We could not find key {#PythonInstallKey} in registry.]',
                mbCriticalError, MB_YESNO) = IDYES then
          Result := DoDownloadPage()
        else
          Result := False;
      finally
        if not Result then
        begin
          CancelWithoutPrompt := True;
          Result := False;
          WizardForm.Close;
          exit;
        end;
      end;
  end;

  if CurPageID = wpSelectDir then
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

function GetPythonInstallPath(Param: String): String;
// precondition: CorrectPythonFound()
begin
  if RegKeyExists(HKLM, '{#PythonInstallKey}') then
    RegQueryStringValue(HKLM, '{#PythonInstallKey}', '', Result)
  else
    RegQueryStringValue(HKCU, '{#PythonInstallKey}', '', Result)
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  CancelWithoutPrompt := False;
  DragonVersion := 'XXX'; 
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
