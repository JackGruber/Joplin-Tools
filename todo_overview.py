#!/usr/bin/python

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
    default="ToDo overview",
    help="""Note Title for the overview note""",
)
@click.option(
    "--as-todo / --as-note",
    "as_todo",
    required=False,
    help="""Create note as ToDo.""",
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
def Main(notebook, title, token, url, add_tag, as_todo):
    if token is not None:
        joplinapi.SetEndpoint(url, token)
    elif joplinapi.LoadEndpoint() == False:
        joplinapi.SetEndpoint(url, token)

    while joplinapi.Ping() == False:
        print("Joplin not running")
        sys.exit(1)

    if add_tag is not None:
        add_tag = add_tag.replace(", ", ",")
        add_tag = add_tag.split(",")

    note = joplinapi.Search(query='title:"' + title + '"', type="note", fields="id,title,is_todo,body")

    if len(note['items']) == 1:
        note_id = note['items'][0]['id']
        body_org = note['items'][0]['body']
    elif len(note) > 1:
        print("Error multiple matching notes found")
        sys.exit(1)
    else:
        note_id = None
        body_org = ""

    if note_id is None and notebook is not None:
        notebook_id = joplinapi.GetNotebookID(notebook)
        if notebook_id == False:
            print("Notebook not found")
            sys.exit(1)
    elif note_id is None:
        print("No notebook defined and no note with title '" + title + "' found.")
        sys.exit(1)

    body = "| Date | Title |\n"
    body += "| --- | --- |\n"
    page = 1
    while True:
        todos = joplinapi.Search(query="type:todo iscompleted:0",
                                type="note", fields="id,title,todo_due,todo_completed",
                                order_by="todo_due", order_dir="ASC", page=page)
        for todo in todos['items']:
            if note_id != todo['id']:
                epoch = int(todo['todo_due'] / 1000)
                date = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')
                if epoch < int(time.time()):
                    date += " \U00002757"
                body += "|" + date + \
                    "|[" + todo['title'] + "](:/" + todo['id'] + ")|\n"

        page += 1
        if todos['has_more'] == False:
            break

    if note_id is None:
        note_id = joplinapi.CreateNote(title, body, notebook_id)
    else:
        if body != body_org:
            data = {}
            data['body'] = body
            joplinapi.UpdateNote(note_id, json.dumps(data))

    if body != body_org:
        if as_todo == True:
            data = {}
            data['is_todo'] = 1
            data['todo_due'] = 0
            data['todo_completed'] = 0
            joplinapi.UpdateNote(note_id, json.dumps(data))

        if add_tag is not None:
            for tag in add_tag:
                joplinapi.AddTagToNote(tag, note_id, True)


if __name__ == "__main__":
    Main()
