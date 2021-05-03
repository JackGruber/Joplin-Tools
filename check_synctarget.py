import sqlite3
import os
import click
import glob
import re

DB_CONNECTION = None

@click.command()
@click.option(
    "-d",
    "--db",
    "db",
    required=True,
)
@click.option(
    "-s",
    "--synctarget",
    "synctarget",
    required=True,
)

def Main(db, synctarget):
    dbConnection = DBConnect(db)

    CheckFilesVsDB(dbConnection, synctarget, "*.md", True)
    print("")
    
    CheckFilesVsDB(dbConnection, synctarget + ".resource", "*", False)

    DBClose(dbConnection)

def ReadInfo(file, info):
    f = open(file,'r', encoding='utf-8')
    for lines in range(500):
        line = f.readline()
        if re.match(info, line):
            return line
    return "n/a"

def CheckFilesVsDB(dbConnection, path, pattern, checkType):
    print("Check " + path)
    files = glob.glob(path + "\\" + pattern)
    check = []
    for f in files:
        check.append( os.path.basename(f).replace(".md","") )
        if(len(check) >= 10):
            ids = CheckIDsInDB(dbConnection, check)
            prinType(ids, path, checkType)
            check = []

    ids = CheckIDsInDB(dbConnection, check)
    prinType(ids, path, checkType)

def prinType(ids, path, checkType):
    if ids:
        for id in ids:
            if checkType == True:
                type = ReadInfo(path + "\\" + id + ".md", "^type_:")
                time = ReadInfo(path + "\\" + id + ".md", "^updated_time:")
                print(id + " " + type + " " + time)
            else:
                print(id)
    
def DBConnect(dbFile):
    print("Database: " + dbFile)
    dbConnection = sqlite3.connect(dbFile)
    dbConnection.row_factory = sqlite3.Row

    return dbConnection

def DBClose(dbConnection):
    dbConnection.close()

def CheckIDsInDB(dbConnection, ids):
    org = len(ids)
    ids = notInTable(dbConnection, "notes", ids)
    if(len(ids) == 0):
        return

    ids = notInTable(dbConnection, "resources", ids)
    if(len(ids) == 0):
        return

    ids = notInTable(dbConnection, "folders", ids)
    if(len(ids) == 0):
        return

    ids = notInTable(dbConnection, "tags", ids)
    if(len(ids) == 0):
        return

    ids = notInTable(dbConnection, "master_keys", ids)
    if(len(ids) == 0):
        return

    ids = notInTable(dbConnection, "note_tags", ids)
    if(len(ids) == 0):
        return

    ids = notInTable(dbConnection, "revisions", ids)
    if(len(ids) == 0):
        return

    return ids

def notInTable(dbConnection, table, ids):
    query = 'SELECT id FROM ' + table + ' WHERE id IN ("' + '","'.join(ids) + '")'
    cursor = dbConnection.cursor()
    records = cursor.execute(query).fetchall()
    notIncluded = []
    if records == None:
        return ids
    else:
        for row in records:
            try:
                ids.pop(ids.index(row['id']))
            except Exception as e:
                continue
        return ids

if __name__ == "__main__":
    Main()