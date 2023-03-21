import os
import sqlite3

import simimg.utils.handyfunctions as HF


def createConnection(db_file):
    "Create a connection to the DataBase"

    dirName = os.path.dirname(db_file)
    if not os.path.isdir(dirName):
        try:
            os.mkdir(dirName)
        except OSError:
            return None

    try:
        db_connection = sqlite3.connect(db_file)
        return db_connection
    except sqlite3.Error:
        return None


def createTables(db_connection, clear=None):
    "Create or empty the required tables in the DataBase"

    sql_delete_table = " DROP TABLE IF EXISTS HashValueTable "
    sql_create_table = (
        "CREATE TABLE IF NOT EXISTS HashValueTable "
        "("
        "id integer PRIMARY KEY,"
        "FileHash text NOT NULL,"
        "HashMethod text NOT NULL,"
        "ImageHashValue text NOT NULL"
        ")"
    )

    try:
        db_cursor = db_connection.cursor()
        if clear:
            db_cursor.execute(sql_delete_table)
            db_connection.execute("VACUUM")
        db_cursor.execute(sql_create_table)

        db_cursor.close()
        db_connection.commit()
        return True
    except sqlite3.Error:
        return False


def closeConnection(db_connection):
    try:
        db_connection.commit()
        db_connection.execute("VACUUM")
        db_connection.close()
    except sqlite3.Error:
        return


def getHash(checksum, hashname, db_connection=None):
    try:
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT ImageHashValue FROM HashValueTable WHERE FileHash=? AND HashMethod=?",
            (checksum, hashname)
        )
        hashvalue = db_cursor.fetchone()
        db_cursor.close()
        if hashvalue:
            # return convDict[hashname](hashvalue[0])
            return HF.hexstring2array(hashvalue[0])
    except sqlite3.Error:
        db_cursor.close()
    return None


def setHash(checksumHashTuples, hashname, db_connection=None):

    if not checksumHashTuples:
        return

    tupled_data = [
        (checksum, hashname, HF.array2hexstring(imagehashvalue))
        for checksum, imagehashvalue in checksumHashTuples
    ]

    db_cursor = db_connection.cursor()
    db_cursor.executemany(
        "INSERT INTO HashValueTable (FileHash, HashMethod, ImageHashValue) VALUES(?, ?, ?)",
        tupled_data
    )
    db_cursor.close()
    db_connection.commit()
