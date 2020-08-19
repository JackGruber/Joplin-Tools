# Joplin Hotfolder for fileupload

Python Hotfolder script to add files to Joplin over the Joplin API.

## Info

Images and text (Mimetype `text/plain`) are inserted directly into the note, other Files are added as attachment. The files are deleted after processing.

If no token is specified, the script will ask for it and then store it in the script's directory for later use when called without the `-t` option.

If you want to insert additional files directly as text, define them with the `--as-plain` switch.

## Additional modules

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF)

```console
pip install PyMuPDF
```


## Example

```python
python hotfolder.py -d "Import" -p "C:\JoplinImport"
```

## Parameters

- `-d` Specify the notebook in which to place newly created notes. Default: `Import`
- `-t` Joplin Authorisation token. Default: `Ask for token and store token`
- `-p` Folder for monitoring
- `--as-plain` Specify file extensions comma separated for input as text. Example: `.md, .json`
- `-u` Joplin Web Clipper URL. Default `http://localhost:41184`
- `--tag` Specify of comma separated Tags which should be added to the note. Example: `scan, todo`
- `--preview` Create a preview of the first site from an PDF file.
