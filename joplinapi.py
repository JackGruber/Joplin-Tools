import requests
import mimetypes
import os
import json
import base64
import sys
import mimetypes

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
    """ Find the ID of the destination folder 
    adapted logic from jhf2442 on Joplin forum
    https://discourse.joplin.cozic.net/t/import-txt-files/692
    """
    notebook_id = ""
    joplin = GetEndpoint()

    try:
        res = requests.get(joplin['endpoint'] +
                           "/folders?token=" + joplin['token'])
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


def CreateNoteWithFile(file, notebook_id, ext_as_text=None):
    joplin = GetEndpoint()

    datatype = mimetypes.guess_type(file)[0]

    if datatype is None:
        datatype = "None"

    if datatype == "text/plain" or (ext_as_text is not None and os.path.splitext(os.path.basename(file))[1] in ext_as_text):
        with open(file, "r") as txt:
            text = txt.read()
        values = CreateJsonForNote(os.path.basename(file), notebook_id, text)
    elif datatype[:5] == "image":
        data = EncodeResourceFile(file, datatype)
        values = CreateJsonForNote(
            os.path.basename(file), notebook_id, "", data)
    else:
        resource = CreateResource(file)
        if resource == False:
            print("Resource creation error")
            return False

        file_link = "[" + \
            os.path.basename(file) + "](:/" + resource['id'] + ")"
        values = CreateJsonForNote(
            os.path.basename(file), notebook_id, file_link)

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


def GetTags():
    joplin = GetEndpoint()
    global JOPLIN_TAGS
    if(JOPLIN_TAGS is None):
        response = requests.get(joplin['endpoint'] +
                                "/tags?token=" + joplin['token'])
        if response.status_code != 200:
            print("Tag load ERROR")
            return False
        else:
            JOPLIN_TAGS = response.json()
    return JOPLIN_TAGS


def GetTagID(search_tag):
    tags = GetTags()
    search_tag = search_tag.strip()

    if tags == False:
        return False
    for tag in tags:
        if tag['title'].lower() == search_tag.lower():
            return tag['id']

    return False


def AddTagToNote(tag, note_id):
    joplin = GetEndpoint()
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
