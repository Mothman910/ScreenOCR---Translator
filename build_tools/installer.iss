#define MyAppName "ScreenOCR & Translator"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ScreenOCR & Translator Team"
#define MyAppURL ""
#define MyAppExeName "ScreenOCR_Translator.exe"

[Setup]
; Unikalne identyfikatory aplikacji
AppId={{AD15B7A5-D1C2-4FC0-987F-63B9612AC810}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Ustawienia instalatora
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=Setup_ScreenOCR_Translator
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Uprawnienia i warunki instalacji
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0.22000

; Ustawienia graficzne instalatora
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "Utwórz ikonę na pulpicie"; GroupDescription: "Dodatkowe ikony:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Utwórz ikonę na pasku szybkiego uruchamiania"; GroupDescription: "Dodatkowe ikony:"; Flags: unchecked
Name: "startupicon"; Description: "Uruchamiaj automatycznie po starcie systemu"; GroupDescription: "Autostart:"; Flags: unchecked

[Files]
; Pliki aplikacji
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

; Dołączenie biblioteki Tesseract OCR i danych językowych
Source: "..\external\Tesseract-OCR\*"; DestDir: "{app}\Tesseract-OCR"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: not IsTesseractInstalled

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon
Name: "{commonstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
; Uruchomienie aplikacji po zakończeniu instalacji
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Rejestracja aplikacji w autostarcie
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon

[Code]
function IsTesseractInstalled: Boolean;
var
  UninstallKey, DisplayName: String;
  Success: Boolean;
begin
  Result := False;
  // Sprawdzenie, czy Tesseract jest już zainstalowany
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\';
  Success := RegQueryStringValue(HKLM, UninstallKey + '{F4850DF3-DC3E-4842-9B96-E353A5E2A0F4}_is1', 'DisplayName', DisplayName);
  if Success and (Pos('Tesseract', DisplayName) > 0) then
  begin
    Result := True;
  end;
  
  // Sprawdzenie, czy Tesseract znajduje się w ścieżce systemowej
  if not Result then
  begin
    if DirExists('C:\Program Files\Tesseract-OCR') or DirExists('C:\Program Files (x86)\Tesseract-OCR') then
    begin
      Result := True;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Prośba o uprawnienia administracyjne dla aplikacji
    ShellExec('runas', 'cmd.exe', '/c icacls "' + ExpandConstant('{app}\{#MyAppExeName}') + 
              '" /grant *S-1-1-0:(RX)', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;