"""
inventoryCleaner.py
This function takes in a GeoJSON-formatted list of roads from the Mass Road
Inventory 2014 and populates a table in a specified database.

Contents:

Required packages:
json
psycopg2

Acknowledgements: For a list of acknowledgements, see the information at
INSERT WEBSITE HERE.

Louis Fernandes, 2016 06 04
"""

import json
import psycopg2
import os.path

class Inventory():
    """A class to track the properties of the road inventory GeoJSON file
    provided. We use the database, table, and user provided to build a list
    of desired fields during init and then generate a big ol' dictionary to
    write to the database.
    """
    def __init__(self, dbname, table, dbuser='louisf'):
        """
        Iniitalize a new instance of Inventory.
            :param dbname: String name of the database.
            :param table: String name of the table.
            :param dbuser: String user name for the DB. Default 'louisf'
        """
        try:
            con = None
            con = psycopg2.connect(database=dbname, user=dbuser)
        except psycopg2.DatabaseError as e:
            print("I cannot connect to the database " + dbname)
            print(e)

        print("Connected to database " + dbname)
        cur = con.cursor()
        cur.execute("Select * FROM " + table)
        colnames = [desc[0] for desc in cur.description]
        con.close()
        self.keys = colnames
        self.entries = dict()

    def parseGeoJson(self, pathToFile):
        """
        :param pathToFile: The path to the GeoJSON file.
        :return: 1 for success, 0 elsewise
        """
        if (os.path.isfile(pathToFile) != True):
            print("path to file is incorrect.")
            return 0
        return 1


def insertIntoDB(dbname, table, entry, dbuser='louisf'):
    """
    :param dbname: String name of the database.
    :param table: String name of the table.
    :param entry: A dict of values to write in. Should have fields:
    'RoadInvent', 'CRN', 'StreetName', 'SpeedLimit', 'Terrain', 'Structural'
    :param dbuser: String user name for the DB. Default 'louisf'
    :return: 0 for failure, 1 for success
    """
    try:
        con = None
        con = psycopg2.connect(database=dbname, user=dbuser)
    except psycopg2.DatabaseError as e:
        print("I cannot connect to the database " + dbname)
        print(e)
        return 0

    print("Connected to database " + dbname)

    cur = con.cursor()

    try:
        cols = entry.keys()
        vals = [entry[x] for x in cols]
        vals_str_list = ["%s"] * len(vals)
        vals_str = ", ".join(vals_str_list)
        statement = "INSERT INTO {0} VALUES({1}, {2}, '{3}', {4}, {5}, {6})".format(
            table, entry["RoadInvent"], entry["CRN"], entry["StreetName"],
            entry["SpeedLimit"], entry["Terrain"], entry["Structural"]
        )
        print(statement)
        # cur.execute(statement)
        cur.execute("INSERT INTO " + table + "({cols}) VALUES({vals_str})".format(
            cols = cols, vals_str = vals_str), vals)
        con.commit()
    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()
        print("Error in writing to the database.")
        print(e)
        return 0
    return 1

