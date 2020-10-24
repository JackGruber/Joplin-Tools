# Joplin tools

Various Python and AutoIt tools for Joplin. 
Python use the Joplin API for communication.

## Additional python modules

Please einstall the following python modules:

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF)
- [Click](https://click.palletsprojects.com)
- Requests

```console
pip install click
pip install requests
pip install PyMuPDF
```

## Tools

- [hotfolder.py](#hotfolderpy)
- [add_pdf_previews.py](#add_pdf_previewspy)
- [todo_overview.py](#todo_overviewpy)
- [JoplinWinBackup.au3](#JoplinWinBackupau3)

### Parameters for all tools

- `-t` Joplin Authorisation token. Default: `Ask for token and store token`
- `-u` Joplin Web Clipper URL. Default `http://localhost:41184`

If no token is specified, the script will ask for it and then store it in the script's directory for later use when called without the `-t` option.

### hotfolder.py

---

Monitor a folder an add the Files to Joplin as a Note.

Images and text (Mimetype `text/plain`) are inserted directly into the note, other Files are added as attachment. The files are deleted after processing.

If you want to insert additional files directly as text, define them with the `--as-plain` switch.

**Example**

```python
python hotfolder.py -d "Import" -p "C:\JoplinImport"
```

**Parameters**

- `-d` Specify the notebook in which to place newly created notes. Default: `Import`
- `-p` Folder for monitoring
- `--as-plain` Specify file extensions comma separated for input as text. Example: `.md, .json`
- `--tag` Specify of comma separated Tags which should be added to the note. Example: `scan, todo`
- `--preview` Create a preview of the first site from an PDF file.

### add_pdf_previews.py

---

Search for notes with a PDF attachment an create a preview of the first PDF Site and add this Preview to Note.

<img src="img/pdf_preview.jpg">

**Parameters**

- `-n` Defines the notebook in which notes with PDF file should be searched. Default: `All notebooks`

**Example**

```python
python add_pdf_previews.py -n "Import"
```

### todo_overview.py

---

Creates or Updates a note with a list of all open ToDo's. All to-dos that have been exceeded are marked with a ❗.

<img src="img/todo_overview.jpg">

**Parameters**

- `-n` Defines the notebook in which the new Note should be created.
- `--title` Defines the title for the note to be updated or createt. Default `ToDo overview`
- `--as-todo` Create the note as a ToDo
- `--tag` Specify of comma separated Tags which should be added to the note. Example: `scan, todo`

**Example**

```python
python todo_overview.py --title "Open ToDo's" --as-todo --tag "importend"
```

### JoplinWinBackup.au3

---

Since there is no possibility for an automatic backup under windows, the required key combinations are sent to joplin via autoit to create a backup.

Rename the `JoplinWinBackup.ini.example` to `JoplinWinBackup.ini` and place it in the same folder es the `JoplinWinBackup.au3` or `JoplinWinBackup.exe`.

The latest JoplinWinBackup.exe can be downloaded from the [latest release](https://github.com/JackGruber/Joplin-Tools/releases/latest/download/JoplinWinBackup.exe).

Options from the JoplinWinBackup.ini

- `JoplinWinBackup` Defines the Path to Joplin exe. Default `C:\Program Files\Joplin\Joplin.exe`
- `backup_folder` Path to store the Backups. Default `C:\Backup`
- `key_combo` Key combo to get to the "JEX - Joplin export File" menue. Default `fej`
- `save_dialog` Dialog Title of the save/eport dialog. Default `Speichern unter`
- `ask_for_start` Ask if backup should be started. Default `1`, `0` = No, `1`= Yes
- `backup_file_add_date` Append date to the Backupfile. Default `1`, `0` = No, `1`= Yes
- `backup_file_add_time` Append time to the Backupfile. Default `1`, `0` = No, `1`= Yes
- `backup_file_name` Filename of the Backup. Default `joplin_backup.jex`
- `overwrite_file` Overwrite existing backup file. Default `0`, `0` = No, `1`= Yes
