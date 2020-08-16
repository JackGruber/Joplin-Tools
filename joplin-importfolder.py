#!/usr/bin/python

# -*- coding: utf-8 -*-

import time
import click
import sys
import os
import json
import time
import requests
import mimetypes
import base64
import joplinapi

@click.command()
@click.option(
    "-d",
    "--destination",
    "destination",
    default="Import",
    show_default=True,
    help="""Specify the notebook in which to place newly created notes."""
    """ Specified notebook must exist or program will exit.""",
)
@click.option(
    "-t",
    "--token",
    "token",
    required=True,
    help="""Specify the API token.""",
)
@click.option(
    "-p",
    "--path",
    "path",
    required=True,
    help="""Specify the folder for monitoring.""",
)
def Main(path, destination, token):
    if not os.path.exists(path):
        print("Path does not exist")
        sys.exit(1)

    global JOPLIN_NOTEBOOK_NAME
    global JOPLIN_NOTEBOOK_ID
    global JOPLIN_TOKEN
    global JOPLIN_ENDPOINT
    JOPLIN_ENDPOINT = "http://localhost:41184"
    JOPLIN_NOTEBOOK_NAME = destination
    JOPLIN_TOKEN = token
    JOPLIN_NOTEBOOK_ID = JoplinGetNotebookID(JOPLIN_NOTEBOOK_NAME)
    if JOPLIN_NOTEBOOK_ID == "" or JOPLIN_NOTEBOOK_ID == "err":
        print("Notebook not found")
        sys.exit(1)

    WatchFolder(path)

def WatchFolder(path):
    files = dict()
    while 1:
        # Add files and process
        for file in os.listdir(path):
            if not file in files:
                print("Added: " + file)
                files[file] = os.path.getsize(os.path.join(path, file))
            elif os.path.getsize(os.path.join(path, file)) == files[file]:
                print("Process: " + file)
                if JoplinUpload(os.path.join(path, file), JOPLIN_NOTEBOOK_ID):
                    try:
                        os.remove(os.path.join(path, file))
                        files.pop(file)
                    except:
                        print("File remove failed: " + file)
                        files[file] = -2
                else:
                    files[file] = -1
                print("")
            elif files[file] >= 0:
                files[file] = os.path.getsize(os.path.join(path, file))

        # Remove orphan entrys
        check = files.copy()
        for file in check:
            if not os.path.exists(os.path.join(path, file)):
                print("Removed orphan: " + file)
                files.pop(file)

        time.sleep(1)


def JoplinGetNotebookID(notebook_name):
    """ Find the ID of the destination folder 
    adapted logic from jhf2442 on Joplin forum
    https://discourse.joplin.cozic.net/t/import-txt-files/692
    """
    notebook_id = ""

    try:
        res = requests.get(JOPLIN_ENDPOINT + "/folders?token=" + JOPLIN_TOKEN)
        folders = res.json()

        for folder in folders:
            if folder.get("title") == notebook_name:
                notebook_id = folder.get("id")
        if notebook_id == "":
            for folder in folders:
                if "children" in folder:
                    for child in folder.get("children"):
                        if child.get("title") == notebook_name:
                            notebook_id = child.get("id")
    except requests.ConnectionError as e:
        print("Connection Error - Is Joplin Running?")
    except Exception as e:
        print("Error - on get joplin notebook id")

    return notebook_id

def JoplinEncodeFile(filename, datatype):
    file = open(filename, "rb") 
    encoded = base64.b64encode(file.read())
    file.close()
    img = f"data:{datatype};base64,{encoded.decode()}"
    return img

def JoplinUpload(file, notebook_id):
    print("Upload to Joplin: " + file)

    datatype = mimetypes.guess_type(file)[0]
    print(datatype)

    if datatype is None:
        datatype = "None"

    if datatype == "text/plain" or os.path.splitext(os.path.basename(file))[1] in {".md"}:
        with open(file, "r") as txt:
            text = txt.read()
        values = JoplinCreateJson(os.path.basename(file), notebook_id, text)
    elif datatype[:5] == "image":
        data = JoplinEncodeFile(file, datatype)
        values = JoplinCreateJson(os.path.basename(file), notebook_id, "", data)
    else:
        resource = JoplinCreateResource(file)
        if resource == False:
            print("Resource creation error")
            return False
        
        file_link = "[" + os.path.basename(file) + "](:/" + resource['id'] + ")"
        values = JoplinCreateJson(os.path.basename(file), notebook_id, file_link)
    
    requests_return = requests.post(
        JOPLIN_ENDPOINT + "/notes?token=" + JOPLIN_TOKEN, data=values)
    if requests_return.status_code == 200:
        print("Upload OK")
        return True
    else:
        print(requests_return.text)
        print("Upload ERROR")
        print("")
        print("")
        print(values)
        return False

def JoplinCreateResource(file):
    filename = os.path.basename(file)
    title = os.path.splitext(os.path.basename(file))[0]
    f = open(file, "rb") 
    files = {
        "data": (json.dumps(file), f),
        "props": (None, f'{{"title":"{title}", "filename":"{filename}"}}'),
    }
    response = requests.post(JOPLIN_ENDPOINT + "/resources?token=" + JOPLIN_TOKEN, files=files)
    f.close()
    if response.status_code != 200:
        return False
    else:
        return response.json()

def JoplinCreateJson(title, notebook_id, body, file=None):
    if file is None:
        return '{{ "title": {}, "parent_id": "{}", "body": {} }}'.format(
            json.dumps(title), notebook_id, json.dumps(body)
        )
    else:
        return '{{ "title": "{}", "parent_id": "{}", "body": {}, "image_data_url": "{}" }}'.format(
            title, notebook_id, json.dumps(body), file
        )

if __name__ == "__main__":
    Main()
