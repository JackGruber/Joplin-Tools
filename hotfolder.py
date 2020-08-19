#!/usr/bin/python

# -*- coding: utf-8 -*-

import click
import sys
import os
import time
from joplin import joplinapi


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
    required=False,
    help="""Specify the Joplin API token.""",
)
@click.option(
    "--tag",
    "add_tag",
    required=False,
    help="""Specify Tags to add to the note. Comma separated for multiple tags.""",
)
@click.option(
    "-p",
    "--path",
    "path",
    required=True,
    help="""Specify the folder for monitoring.""",
)
@click.option(
    "--as-plain",
    "plain",
    required=False,
    help="""Specify additional file extensions comma separated for input as text.""",
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
    "--preview/--no-preview",
    "preview",
    required=False,
    default=False,
    show_default=True,
    help="""Create a preview of the first site from an PDF file.""",
)
def Main(path, destination, token, url, plain, add_tag, preview):
    if not os.path.exists(path):
        print("Path does not exist")
        sys.exit(1)

    if token is not None:
        joplinapi.SetEndpoint(url, token)
    elif joplinapi.LoadEndpoint() == False:
        joplinapi.SetEndpoint(url, token)

    while joplinapi.Ping() == False:
        print("Wait for Joplin")
        time.sleep(10)
    
    if plain is not None:
        plain = plain.replace(", ", ",")
        plain = plain.split(",")

    notebook_id = joplinapi.GetNotebookID(destination)

    if notebook_id == False:
        print("Notebook not found")
        sys.exit(1)

    if add_tag is not None:
        add_tag = add_tag.replace(", ", ",")
        add_tag = add_tag.split(",")

    WatchFolder(path, notebook_id, plain, add_tag, preview)


def WatchFolder(path, notebook_id, plain, add_tags, preview):
    files = dict()
    while 1:
        # Add files and process
        for file in os.listdir(path):
            if not file in files:
                print("Added: " + file)
                files[file] = os.path.getsize(os.path.join(path, file))
            elif os.path.getsize(os.path.join(path, file)) == files[file]:
                print("Upload to Joplin: " + file)
                note_id = joplinapi.CreateNoteWithFile(
                    os.path.join(path, file), notebook_id, plain, preview)
                if note_id != False:
                    if add_tags is not None:
                        for tag in add_tags:
                            joplinapi.AddTagToNote(tag, note_id, True)
                    print("Joplin upload completed")
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


if __name__ == "__main__":
    Main()
