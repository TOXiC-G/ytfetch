; ytfetch Inno Setup Script
; Generates standard Windows installer with Start Menu and Desktop shortcuts

#define MyAppName "ytfetch"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TOXiC-G"
#define MyAppURL "https://github.com/TOXiC-G/ytfetch"
#define MyAppExeName "ytfetch.exe"
#define MyAppId "{{A123FE89-7711-4E6D-981D-FF903E78241A}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
DefaultGroupName={#MyAppName}
OutputDir=..\dist\installer
OutputBaseFilename=ytfetch-Setup-x64
SetupIconFile=ytfetch.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "ytfetch.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\ytfetch.ico"; AppUserModelID: "TOXiC-G.ytfetch.Desktop.1.0"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\ytfetch.ico"; AppUserModelID: "TOXiC-G.ytfetch.Desktop.1.0"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
