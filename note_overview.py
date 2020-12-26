# -*- coding: utf-8 -*-

import click
from joplin import joplinapi
import time
import sys
import json
from datetime import datetime


@click.command()
@click.option(
    "-n",
    "--notebook",
    "notebook",
    required=False,
    help="""Specify the notebook in which to place newly created overview."""
    """ Specified notebook must exist or program will exit.""",
)
@click.option(
    "--title",
    "title",
    required=True,
    default="Note overview",
    help="""Note Title for the overview note""",
)
@click.option(
    "--tag",
    "add_tag",
    required=False,
    help="""Specify Tags to add to the note. Comma separated for multiple tags.""",
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
@click.option(
    "-q",
    "--query",
    "query",
    required=True,
    help="""Specify the search query.""",
)
@click.option(
    "--order_by",
    "order_by",
    required=False,
    default='user_updated_time',
    help="""Specify the Joplin field for the note ordering.""",
)
@click.option(
    "--order_dir",
    "order_dir",
    required=False,
    type=click.Choice(['ASC', 'DESC'], case_sensitive=False),
    default="DESC",
    show_default=True
)
def Main(notebook, title, add_tag, token, url, query, order_by, order_dir):
    if token is not None:
        joplinapi.SetEndpoint(url, token)
    elif joplinapi.LoadEndpoint() == False:
        joplinapi.SetEndpoint(url, token)

    while joplinapi.Ping() == False:
        print("Joplin not running")
        sys.exit(1)

    new_note_query = "title:'" + title + "'"
    if notebook != None:
        new_note_query += ' notebook:"' + notebook + '"'

    # Find ID for overview note
    page = 1
    overview_id = None
    while True and overview_id == None:
        search = joplinapi.Search(new_note_query, 'note', limit=50, page=page, fields='id, title', order_by=order_by, order_dir=order_dir)
        for note in search['items']:
            if(note['title'] == title):
                overview_id = note['id']
        if search['has_more'] == False:
            break
        page += 1

    # Find notbook ID
    if overview_id is None and notebook is not None:
        notebook_id = joplinapi.GetNotebookID(notebook)
        if notebook_id == False:
            print("Notebook not found")
            sys.exit(1)
    elif overview_id is None:
        print("No notebook defined and no note with title '" + title + "' found!")
        sys.exit(1)

    if add_tag is not None:
        add_tag = add_tag.replace(", ", ",")
        add_tag = add_tag.split(",")

    # collect information
    body = "| created time | updated time | Title |\n"
    body += "| --- | --- | --- |\n"
    page = 1
    while True:
        search = joplinapi.Search(query, 'note', limit=50, page=page, fields='id, title, created_time, user_updated_time', order_by=order_by, order_dir=order_dir)
        for note in search['items']:
            if(note['id'] != overview_id):
                epoch = int(note['created_time'] / 1000)
                date_created = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')
                epoch = int(note['user_updated_time'] / 1000)
                date_updated = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')
                body += "|" + date_created + "|" + date_updated + "|[" + note['title'] + "](:/" + note['id'] + ")|\n"
        if search['has_more'] == False:
            break
        page += 1

    if overview_id is None:        
        overview_id = joplinapi.CreateNote(title, body, notebook_id)
        if(overview_id != False):
            print("Create note '" + title + "' in notebook '" + notebook + "'")
        else:
            print("Error on note create")
            sys.exit(1)
    else:
        org_note = joplinapi.GetNotes(overview_id, "body")
        if (org_note['body'] != body):
            data = {}
            data['body'] = body
            if( joplinapi.UpdateNote(overview_id, json.dumps(data)) ):
                print("Note '" + title + " updated")
            else:
                print("Error on note create")
                sys.exit(1)
        else:
            print("No new information")

    if add_tag is not None:
                for tag in add_tag:
                    joplinapi.AddTagToNote(tag, overview_id, True)

if __name__ == "__main__":
    Main()
