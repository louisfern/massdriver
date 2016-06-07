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
        self.entries = list()
        self.parsedLines = 0
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
        self.tester = dict()


    def parseGeoJson(self, pathToFile):
        """
        :param pathToFile: The path to the GeoJSON file.
        :return: 1 for success, 0 elsewise
        """
        if (os.path.isfile(pathToFile) != True):
            print("path to file is incorrect.")
            return 0

        def is_json(myjson):
            try:
                json_object = json.loads(myjson)
            except ValueError:
                return False
            return True

        def checkelems(d, l):
            for elem in l:
                if (elem in d)!=True:
                    return False
            return True

        def shrinkdict(d, l):
            nd = dict()
            for elem in l:
                nd[elem] = d[elem]
            return nd

        f = open(pathToFile, 'r')
        it = 0
        for lines in f.readlines():
            it += 1
            tline = lines[:-2]
            if is_json(tline):
                self.parsedLines += 1
                js = json.loads(tline)
                d = dict(
                    (k.lower() if isinstance(k, str) else k, v.lower() if
                     isinstance(v, str) else v) for k, v in js['properties'].items()
                         )
                ret = checkelems(d, self.keys)
                if ret != True:
                    print("Property mismatch in iteration " + str(it))
                    continue
                nd = shrinkdict(d, self.keys)
                self.entries.append(nd)
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

    cur = con.cursor()

    try:
        l = list(entry.keys())
        l2 = ', '.join(l)
        cols = tuple(l)
        dispcols = l2
        vals = [entry[x] for x in cols]
        vals_str_list = ["%s"] * len(vals)
        vals_str = ", ".join(vals_str_list)

        statement = "INSERT INTO " + table + " ({dispcols}) VALUES ({vals_str})".format(
            dispcols=dispcols, vals_str=vals_str)
        cur.execute(statement, vals)
        con.commit()
    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()
        print("Error in writing to the database.")
        print(e)
        return 0
    return 1

