#!/usr/bin/python

# -*- coding: utf-8 -*-

import click
import sys
import os
import time
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
@click.option(
    "-u",
    "--url",
    "url",
    required=False,
    default="http://localhost:41184",
    show_default=True,
    help="""Specify the Joplin web clipper URL.""",
)
def Main(path, destination, token, url):
    if not os.path.exists(path):
        print("Path does not exist")
        sys.exit(1)

    if token is not None:
        joplinapi.SetEndpoint(url, token)
    elif joplinapi.LoadEndpoint() == False:
    joplinapi.SetEndpoint(url, token)

    notebook_id = joplinapi.GetNotebookID(destination)

    if notebook_id == False:
        print("Notebook not found")
        sys.exit(1)

    WatchFolder(path, notebook_id)


def WatchFolder(path, notebook_id):
    files = dict()
    while 1:
        # Add files and process
        for file in os.listdir(path):
            if not file in files:
                print("Added: " + file)
                files[file] = os.path.getsize(os.path.join(path, file))
            elif os.path.getsize(os.path.join(path, file)) == files[file]:
                print("Upload to Joplin: " + file)
                if joplinapi.CreateNoteWithFile(os.path.join(path, file), notebook_id, {".md"}):
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
