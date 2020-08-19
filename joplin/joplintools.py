import fitz
import base64
import re
from joplin import joplinapi
import tempfile
import os
import json


def CreatePDFPreviev(pdffile, png, site):
    doc = fitz.open(pdffile)
    page = doc.loadPage(site - 1)
    pix = page.getPixmap()
    pix.writePNG(png)


def GetAllMimeResources(resources, mime):
    res = []
    for resource in resources:
        if resource['mime'] == mime:
            res.append(resource)

    if len(res) == 0:
        return False
    else:
        return res


def AddPDFPreviewToBody(body, pdf_id, preview_id):
    preview_link = "![" + pdf_id + "](:/" + preview_id + ")"
    result = re.sub(r"(\[.*\]\(:\/" + pdf_id + r"\))",
                    preview_link + r"\n\1", body)
    return result


def AddPDFPreviewToNote(note_id):
    print("AddPDFPreviewToNote: " + note_id, end=" ")
    res = joplinapi.GetNoteResources(note_id)
    if res is None or res == False:
        return True

    pdfs = GetAllMimeResources(res, "application/pdf")
    if pdfs == False:
        return True

    note = joplinapi.GetNotes(note_id, "body, title")
    body_new = note['body']

    print("\t" + note['title'])

    note_update = False
    for pdf in pdfs:
        print("\tResource: " + pdf['id'] + "\t" + pdf['title'])
        tmp = os.path.join(tempfile.gettempdir(), pdf['title'])
        png = tmp + ".png"

        if re.search(r"!\[" + pdf['id'] + r"\]", body_new) is not None:
            print("\talready present")
            continue

        if re.search(r"!\[.*\]\(:/[\da-z]+\)\n(\[.*\]\(:\/" + pdf['id'] + r"\))", body_new) is not None:
            print("\tpossible present")
            continue

        if joplinapi.GetResourcesFile(pdf['id'], tmp) == False:
            return False

        CreatePDFPreviev(tmp, png, 1)
        img_res = joplinapi.CreateResource(png)
        if img_res != False:
            body_new = AddPDFPreviewToBody(body_new, pdf['id'], img_res['id'])
            note_update = True

    if note_update == True:
        data = {}
        data['body'] = body_new
        json_data = json.dumps(data)
        joplinapi.UpdateNote(note_id, json_data)

    print("")
