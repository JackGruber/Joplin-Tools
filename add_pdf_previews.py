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

    if notebook is not None:
        notebook_id = joplinapi.GetNotebookID(notebook)
        if notebook_id == False:
            print("Notebook not found")
            sys.exit(1)
        else:
            note_ids = joplinapi.GetFolderNotes(notebook_id)
    else:
        note_ids = joplinapi.GetNotes(None, "id")
    
    print("Process 1 of " + str(len(note_ids)) + " notes")
    count = 1
    for note in note_ids:
        if count % 10 == 0:
            print("Process " + str(count) + " of " + str(len(note_ids)) + " notes")
        joplintools.AddPDFPreviewToNote(note['id'])
        count += 1


if __name__ == "__main__":
    Main()
