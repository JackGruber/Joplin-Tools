import requests
import mimetypes
import os
import json
import base64
import sys
import mimetypes

def SetEndpoint(endpoint, token):
    global JOPLINAPI_ENDPOINT
    global JOPLINAPI_TOKEN
    JOPLINAPI_ENDPOINT = endpoint
    JOPLINAPI_TOKEN = token

def GetEndpoint():
    endpoint = {"endpoint":JOPLINAPI_ENDPOINT, "token": JOPLINAPI_TOKEN}
    return endpoint

def GetNotebookID(notebook_name):
    """ Find the ID of the destination folder 
    adapted logic from jhf2442 on Joplin forum
    https://discourse.joplin.cozic.net/t/import-txt-files/692
    """
    notebook_id = ""
    joplin = GetEndpoint()

    try:
        res = requests.get(joplin['endpoint'] + "/folders?token=" + joplin['token'])
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

    if notebook_id == "" or notebook_id == "err":
        return False
    else:
        return notebook_id

def CreateNoteWithFile(file, notebook_id, ext_as_text = None):
    joplin = GetEndpoint()

    datatype = mimetypes.guess_type(file)[0]

    if datatype is None:
        datatype = "None"

    if datatype == "text/plain" or os.path.splitext(os.path.basename(file))[1] in ext_as_text:
        with open(file, "r") as txt:
            text = txt.read()
        values = CreateJsonForNote(os.path.basename(file), notebook_id, text)
    elif datatype[:5] == "image":
        data = EncodeResourceFile(file, datatype)
        values = CreateJsonForNote(os.path.basename(file), notebook_id, "", data)
    else:
        resource = CreateResource(file)
        if resource == False:
            print("Resource creation error")
            return False
        
        file_link = "[" + os.path.basename(file) + "](:/" + resource['id'] + ")"
        values = CreateJsonForNote(os.path.basename(file), notebook_id, file_link)
    
    requests_return = requests.post(
        joplin['endpoint'] + "/notes?token=" + joplin['token'] , data=values)
    if requests_return.status_code == 200:
        return True
    else:
        #print(requests_return.text)
        print("Note creation ERROR")
        return False

def CreateResource(file):
    joplin = GetEndpoint()

    filename = os.path.basename(file)
    title = os.path.splitext(os.path.basename(file))[0]
    f = open(file, "rb") 
    files = {
        "data": (json.dumps(file), f),
        "props": (None, f'{{"title":"{title}", "filename":"{filename}"}}'),
    }
    response = requests.post(joplin['endpoint'] + "/resources?token=" + joplin['token'], files=files)
    f.close()
    if response.status_code != 200:
        return False
    else:
        return response.json()

def CreateJsonForNote(title, notebook_id, body, file=None):
    if file is None:
        return '{{ "title": {}, "parent_id": "{}", "body": {} }}'.format(
            json.dumps(title), notebook_id, json.dumps(body)
        )
    else:
        return '{{ "title": "{}", "parent_id": "{}", "body": {}, "image_data_url": "{}" }}'.format(
            title, notebook_id, json.dumps(body), file
        )

def EncodeResourceFile(filename, datatype):
    file = open(filename, "rb") 
    encoded = base64.b64encode(file.read())
    file.close()
    img = f"data:{datatype};base64,{encoded.decode()}"
    return img