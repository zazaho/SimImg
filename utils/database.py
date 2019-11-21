import sqlite3

def CreateDBConnection(db_file):
    'Create a connection to the DataBase'
    try:
        db_connection = sqlite3.connect(db_file)
        return db_connection
    except sqlite3.Error as error:
        print(error)
        return None

def CreateDBTables(db_connection):
    'Create or empty the required tables in the DataBase'

    sql_delete_table = ' DROP TABLE IF EXISTS HashValueTable '
    sql_create_table = ' CREATE TABLE IF NOT EXISTS HashValueTable ( id integer PRIMARY KEY, FileHash text NOT NULL, HashMethod text NOT NULL, ImageHashValue text NOT NULL) '

    try:
        db_cursor = db_connection.cursor()
        #db_cursor.execute(sql_delete_table)
        db_cursor.execute(sql_create_table)

        db_cursor.close()
        db_connection.commit()
        return True
    except sqlite3.Error as error:
        print(error)
        return False

def GetHashValueFromDataBase(md5, hashname, db_connection=None):
    try:
        db_cursor = db_connection.cursor()
        db_cursor.execute(' SELECT ImageHashValue FROM HashValueTable WHERE FileHash=? AND HashMethod=? ' , (md5, hashname))
        hashvalue = db_cursor.fetchone()
        db_cursor.close()
        if hashvalue:
            return hashvalue[0]
        else:
            return None
    except sqlite3.Error as error:
        print(error)
        return None

def SetHashValues(Md5HashValueTuples,hashname, db_connection=None):

    if not Md5HashValueTuples:
        return

    tupled_data = [(md5, hashname, imagehashvalue) for md5, imagehashvalue in Md5HashValueTuples]
    
    db_cursor = db_connection.cursor()
    db_cursor.executemany(
        ' INSERT INTO HashValueTable (FileHash, HashMethod, ImageHashValue) VALUES(?, ?, ?) ' , tupled_data
    )
    db_cursor.close()
    db_connection.commit()

