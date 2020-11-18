import click
from joplin import joplinapi
from joplin import joplintools
import time
import sys

@click.command()
@click.option(
    "-n",
    "--notebook",
    "notebook",
    required=False,
    help="""Specify the notebook for the search.""",
)
@click.option(
    "-t",
    "--token",
    "token",
    required=False,
    help="""Specify the Joplin API token.""",
)
@click.option(
    "-u",
    "--url",
    "url",
    required=False,
    default="http://localhost:41184",
    show_default=True,
    help="""Specify the Joplin web clipper URL.""",
)
def Main(notebook, token, url):
    if token is not None:
        joplinapi.SetEndpoint(url, token)
    elif joplinapi.LoadEndpoint() == False:
        joplinapi.SetEndpoint(url, token)

    while joplinapi.Ping() == False:
        print("Wait for Joplin")
        time.sleep(10)

    query = "resource:application/pdf"
    if notebook is not None:
        query += ' notebook:"' + notebook + '"'
    
    page = 1
    while True:
        note_ids = joplinapi.Search(query=query,type="note", fields="id", limit=2, page=page)
        count = 1
        for note in note_ids['items']:
            if count % 10 == 0:
                    print("Process 1 of " + str(len(note_ids['items'])) + " notes from batch " + str(page))
            joplintools.AddPDFPreviewToNote(note['id'])
            count += 1
        
        page += page
        if note_ids['has_more'] == False:
            break;

if __name__ == "__main__":
    Main()
