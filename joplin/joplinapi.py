import requests
import mimetypes
import os
import json
import base64
import sys
import mimetypes
from joplin import joplintools

JOPLIN_TAGS = None


def SetEndpoint(endpoint, token):
    global JOPLINAPI_ENDPOINT
    global JOPLINAPI_TOKEN

    JOPLINAPI_ENDPOINT = endpoint
    JOPLINAPI_TOKEN = token

    if token is None:
        JOPLINAPI_TOKEN = input("Please enter your Joplin API Token: ").strip()
        SaveEndpoint()


def SaveEndpoint(file=None):
    if file is None:
        file = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "joplin.json")
    joplin = json.dumps(GetEndpoint())
    f = open(file, 'w')
    f.write(joplin)
    f.close()


def LoadEndpoint(file=None):
    if file is None:
        file = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "joplin.json")

    if not os.path.exists(file):
        return False

    f = open(file, 'r')
    joplin = f.read()
    f.close()
    joplin = json.loads(joplin)
    SetEndpoint(joplin['endpoint'], joplin['token'])
    return True


def GetEndpoint():
    endpoint = {"endpoint": JOPLINAPI_ENDPOINT, "token": JOPLINAPI_TOKEN}
    return endpoint


def GetNotebookID(notebook_name):
    notebook_id = ""
    joplin = GetEndpoint()

    page = 1
    while True:
        res = requests.get(joplin['endpoint'] + "/folders?token=" + joplin['token'] + "fields=id,title,parent_id&limit=100&page=" + str(page))
        folders = res.json()
            
        for folder in folders['items']:
            if folder["title"] == notebook_name:
                notebook_id = folder["id"]
                break

        page += 1

        if folders.get('has_more') == None or folders.get('has_more') == False:
            break

    if notebook_id == "":
        return False
    else:
        return notebook_id


def CreateNote(title, body, notebook_id):
    joplin = GetEndpoint()

    values = CreateJsonForNote(title, notebook_id, body, None)

    requests_return = requests.post(
        joplin['endpoint'] + "/notes?token=" + joplin['token'], data=values)
    if requests_return.status_code == 200:
        json_response = requests_return.json()
        return json_response['id']
    else:
        print("CreateNote ERROR")
        return False


def CreateNoteWithFile(file, notebook_id, ext_as_text=None, preview=False):
    joplin = GetEndpoint()

    datatype = mimetypes.guess_type(file)[0]
    if datatype is None:
        datatype = "None"

    if datatype == "text/plain" or (ext_as_text is not None and os.path.splitext(os.path.basename(file))[1] in ext_as_text):
        with open(file, "r") as txt:
            text = txt.read()
        values = CreateJsonForNote(os.path.basename(file), notebook_id, text)
    elif datatype[:5] == "image":
        img = EncodeResourceFile(file, datatype)
        values = CreateJsonForNote(
            os.path.basename(file), notebook_id, "", img)
    else:
        body = ""
        img_link = ""
        file_link = ""

        resource = CreateResource(file)
        if resource == False:
            print("Resource creation error")
            return False

        file_link = "[" + \
            os.path.basename(file) + "](:/" + resource['id'] + ")"

        img = None
        if preview == True and datatype == "application/pdf":
            png = file + ".png"
            joplintools.CreatePDFPreview(file, png, 1)
            img = CreateResource(png)
            if resource != False:
                img_link = "![](:/" + img['id'] + ")\n"
                os.remove(png)

        body = img_link + file_link
        values = CreateJsonForNote(
            os.path.basename(file), notebook_id, body, None)

    requests_return = requests.post(
        joplin['endpoint'] + "/notes?token=" + joplin['token'], data=values)
    if requests_return.status_code == 200:
        json_response = requests_return.json()
        return json_response['id']
    else:
        # print(requests_return.text)
        print("Note creation ERROR")
        return False


def CreateResource(file):
    joplin = GetEndpoint()

    filename = os.path.basename(file)
    title = filename
    f = open(file, "rb")
    files = {
        "data": (json.dumps(file), f),
        "props": (None, f'{{"title":"{title}", "filename":"{filename}"}}'),
    }
    response = requests.post(
        joplin['endpoint'] + "/resources?token=" + joplin['token'], files=files)
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

def GetTagID(search_tag):
    search_tag = search_tag.strip()
    tags = Search(search_tag, "tag", limit=10, page=1, fields="id")
    
    if len(tags['items']) == 1:
        return tags['items'][0]['id']
    else:
        return False

def AddTagToNote(tag, note_id, create_tag=False):
    joplin = GetEndpoint()
    tag_id = GetTagID(tag)

    if tag_id is False and create_tag == True:
        CreateTag(tag)
        tag_id = GetTagID(tag)

    if tag_id is not False:
        json = '{"id": "' + note_id + '"}'
        response = requests.post(joplin['endpoint'] +
                                 "/tags/" + tag_id + "/notes?token=" + joplin['token'], data=json)
        if response.status_code != 200:
            print("Tagging ERROR")
            return False
        else:
            return True


def CreateTag(tag):
    joplin = GetEndpoint()
    tag_id = GetTagID(tag)
    if tag_id is False:
        json = '{"title": "' + tag + '"}'
        response = requests.post(joplin['endpoint'] +
                                 "/tags?token=" + joplin['token'], data=json)
        if response.status_code != 200:
            print("Create TAG ERROR")
            return False
        else:
            json_response = response.json()
            return json_response['id']
    return True


def Ping():
    joplin = GetEndpoint()

    try:
        response = requests.get(joplin['endpoint'] + "/ping")
    except:
        return False

    if response.status_code != 200:
        return False
    else:
        if response.text != "JoplinClipperServer":
            return False
        return True


def GetNotes(note_id=None, fields=None):
    joplin = GetEndpoint()

    if fields is None and note_id is not None:
        fields = "id,title,body,is_todo,todo_completed,parent_id,updated_time,user_updated_time,user_created_time,encryption_applied"
    elif fields is None and note_id is None:
        fields = "id,title,is_todo,todo_completed,parent_id,updated_time,user_updated_time,user_created_time,encryption_applied"

    if note_id is not None:
        note_id = "/" + note_id
    else:
        note_id = ""

    response = requests.get(joplin['endpoint'] +
                            "/notes" + note_id + "?token=" + joplin['token'] + "&fields=" + fields)
    if response.status_code != 200:
        print("GetNotes ERROR")
        return False
    if response.text == "":
        return False
    else:
        return response.json()


def GetNoteResources(note_id):
    joplin = GetEndpoint()

    response = requests.get(joplin['endpoint'] +
                            "/notes/" + note_id + "/resources?token=" + joplin['token'])

    if response.status_code != 200:
        print("GetResources ERROR")
        return False
    else:
        if response.text == "":
            return None
        else:
            return response.json()


def GetResourcesFile(res_id, file):
    joplin = GetEndpoint()

    response = requests.get(joplin['endpoint'] +
                            "/resources/" + res_id + "/file?token=" + joplin['token'])

    if response.status_code != 200:
        print("GetResourcesFile ERROR")
        return False
    else:
        try:
            open(file, 'wb').write(response.content)
        except:
            return False
        return True


def UpdateNote(note_id, json_properties):
    joplin = GetEndpoint()

    response = requests.put(joplin['endpoint'] +
                            "/notes/" + note_id + "?token=" + joplin['token'], json_properties)

    if response.status_code != 200:
        print("GetResourcesFile ERROR")
        return False
    else:
        return True


def GetFolderNotes(folder_id):
    joplin = GetEndpoint()

    response = requests.get(joplin['endpoint'] +
                            "/folders/" + folder_id + "/notes?token=" + joplin['token'])
    if response.status_code != 200:
        print("GetFolderNotes ERROR")
        return False
    else:
        return response.json()


def Search(query, type, limit=10, page=1, fields=None, order_by="", order_dir="ASC"):
    joplin = GetEndpoint()

    if fields is None:
        fields = "id,title"

    if order_by != "":
        order_by = "&order_by=" + order_by
    response = requests.get(joplin['endpoint'] +
                            "/search?token=" + joplin['token'] + "&query=" + query + "&type=" + type + "&fields=" + fields + "&limit=" + str(limit) + "&page=" + str(page) + "&order_dir=" + order_dir + order_by)
    if response.status_code != 200:
        print("Search ERROR")
        return False
    else:
        return response.json()
