#include <MsgBoxConstants.au3>
#include <WinAPIFiles.au3>

;Opt("WinTitleMatchMode", 4) ;1=start, 2=subStr, 3=exact, 4=advanced, -1 to -4=Nocase

$INI="JoplinWinBackup.ini"
$JOPLINEXE = IniRead($INI, "General", "joplin", "C:\Program Files\Joplin\Joplin.exe")

; Ask for backup start
if(IniRead($INI, "General", "ask_for_start", 1) = 1) Then
    if(MsgBox($MB_OKCANCEL + $MB_ICONQUESTION, "Joplin Backup", "Start Joplin Backup?") <> $IDOK) Then
        exit
    EndIf
EndIf

; Create backup directory
$BACKUPFOLDER = IniRead($INI, "General", "backup_folder", @ScriptDir & "\joplinbackup")
DirCreate ( $BACKUPFOLDER )
if(FileExists ($BACKUPFOLDER) = False) Then
    MsgBox($MB_OK + $MB_ICONERROR, "Joplin Backup", "Access Error on Backup directory '" & $BACKUPFOLDER & "'")
    exit
EndIf

; Activate Joplin window or start joplin
if (WinActivate("[REGEXPTITLE:^Joplin$; CLASS:Chrome_WidgetWin_1]","") = 0) Then
    run($JOPLINEXE)
EndIf
$hJOPLIN = WinWaitActive("[REGEXPTITLE:^Joplin$; CLASS:Chrome_WidgetWin_1]","", 10)

if( WinWaitActive("[REGEXPTITLE:^Joplin$; CLASS:Chrome_WidgetWin_1]","", 10) = 0) Then
    MsgBox($MB_OK + $MB_ICONERROR, "Joplin Backup", "Failed to start Joplin")
    exit
EndIf

; Send keys for export menue
$keyCombo = IniRead($INI, "General", "key_combo", "{ALT}{SPACE}ej")
Send ($keyCombo)
Sleep(100)

; Wait wor save dialog
$save_dialog = IniRead($INI, "General", "save_dialog", "Speichern unter")
$hSAVE = WinWaitActive("[TITLE:" & $save_dialog & "]","", 2)
if($hSAVE  = 0) Then
    MsgBox($MB_OK + $MB_ICONERROR, "Joplin Backup", "Failed to open export")
    exit
EndIf

; Generate backupfile name
$BACKUPFILE = IniRead($INI, "General", "backup_file_name", "joplin_backup.jex")
$BACKUPFILE = StringReplace($BACKUPFILE, ".jex", "")

if(IniRead($INI, "General", "backup_file_add_date", 1) = 1) Then
    if($BACKUPFILE <> "") Then
        $BACKUPFILE = $BACKUPFILE & "_"
    EndIf
    $BACKUPFILE = $BACKUPFILE & @YEAR & @MON & @MDAY
EndIf

if(IniRead($INI, "General", "backup_file_add_time", 1) = 1) Then
    if($BACKUPFILE <> "") Then
        $BACKUPFILE = $BACKUPFILE & "_"
    EndIf
    $BACKUPFILE = $BACKUPFILE & @HOUR & @MIN
EndIf

$BACKUPFILE = $BACKUPFILE & ".jex"

; Send filename and save
ControlSetText($hSAVE, "", "[CLASS:Edit]", $BACKUPFOLDER & "\" & $BACKUPFILE)
Sleep(50)
ControlClick($hSAVE, "", "[Class:Button;Instance:2]")
Sleep(500)

; Check for confirmation dialog
$hCONFIRM = WinGetHandle ( "[ACTIVE]", "" )
if(StringInStr(WinGetTitle($hCONFIRM,""), $save_dialog) = 0) Then
    $hCONFIRM = 0
EndIf

if ($hCONFIRM <> 0) Then
    if(IniRead($INI, "General", "overwrite_file", 0) = 1) Then
        ControlClick($hCONFIRM, "", "[Class:Button;Instance:1]")
    Else
        ControlClick($hCONFIRM, "", "[Class:Button;Instance:2]")
        Sleep(100)
        ControlClick($hSAVE, "", "[Class:Button;Instance:3]")

        MsgBox($MB_OK + $MB_ICONERROR, "Joplin Backup", "Backup file already exists!" )
    EndIf
EndIf
