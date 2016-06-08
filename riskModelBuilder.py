"""
riskModelBuilder.py
This module queries my Postgres DB, does some data re-arrangement,
and performs a linear regression on the data.

Contents:

Required packages:
pandas
psycopg2
sqlacademy

Acknowledgements: For a list of acknowledgements, see the information at
INSERT WEBSITE HERE.

Louis Fernandes, 2016 06 08
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import types
import numpy as np
import pandas as pd


class Alldata():
    """
    This class retrieves data stored in a Postgres database and contains
    methods for manipulating said data.

    Properties:
        dbinfo: A dict of database connection parameters.
        table: A numpy array of the data pulled from the database.

    Methods:
        __init__(self, dbname, table, dbuser='louisf')
        dbname: String name of database to connect to.
        table: String name of the table to pull from the database.
        dbuser: String user name for the database. Default 'louisf'

    Example:

    """

    def __init__(self, dbname, table, dbuser='louisf'):
        """
        Iniitalize an instance of the class.
        :param dbname: String name of database to connect to.
        :param table: String name of the table to pull from the database.
        :param dbuser: String user name for the database. Default 'louisf'
        """
        self.dbinfo = {'dbname': dbname, 'table': table, 'dbuser': dbuser}
        self.table = None

    def getData(self):
        """
        Pull all data from 'table' in the database 'dbname' as user 'dbuser'.
        Sets self.table to a numpy array.
        :return:
        """
        try:
            con = None
            con = psycopg2.connect(database=self.dbinfo['dbname'],
                                   user=self.dbinfo['dbuser'])
        except psycopg2.DatabaseError as e:
            print("I cannot connect to the database " + self.dbinfo['dbname'])
            print(e)
            return 0

        query = """SELECT * FROM {0}""".format(self.dbinfo['table'])
        self.table = pd.read_sql_query(query, con)
        con.close()

