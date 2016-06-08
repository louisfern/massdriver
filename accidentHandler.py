"""
accidentHandler.py
This function is my initial attempt at parsing and visualizing the accident
data present in the Mass DOT RMV data sets.
Current features:

Works in progress:

Contents:
findcsvlist: A function that returns a list of CSV files given an input
directory.



Acknowledgements:
The Insight Health Data Science program, for giving me the opportunity to work
in an entirely new field.

My girlfriend, for putting up with me.

Created by Louis Fernandes, 2016 06 02.
"""

import glob
import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd

def findcsvlist(path):
    """
    :param path: The path to the directory with the CSV files.
    :return: List of CSV files to be parsed.
    """
    if (os.path.isdir(path) != True):
        print("Path to directory is incorrect.")
        return []
    fullpath = path + '*.csv'
    csvlist = glob.glob(fullpath)
    return csvlist

class AccidentTable():
    """
    This class builds up a dataframe of accident reports. It has methods
    to write this dict of dicts into a database.
    """

    def __init__(self):
        self.accidents = pd.DataFrame()

    def gatherdata(self, csvlist):
        """
        This function takes in a list of CSV files and generates a single
        pandas dataframe out of them.
        :param csvlist:
        :return:
        """
        frame = pd.DataFrame()
        list_ = []
        for file_ in csvlist:
            df = pd.read_csv(file_, header=0, delimiter='^',
                             low_memory=False)
            list_.append(df)
        frame = pd.concat(list_)
        self.accidents = frame

    def cleanData(self):
        """
        This function cleans the dataframe.
        1) Removes rows without geocoding
        2) Removes white space and capital letters from column names
        :return:
        """
        before = len(self.accidents)
        self.accidents = self.accidents[self.accidents["Is Geocoded"] == "Yes"]
        after = len(self.accidents)
        print("Accidents before cleaning: " + str(before))
        print("Accidents after removing non-geocoded: " + str(after))
        colnames = list(self.accidents.columns.values)
        for i in range(0, len(colnames)):
            colnames[i] = colnames[i].replace(" ","").lower()
        self.accidents.columns = colnames

    def tablewrite(self, dbname, table, dbuser, pswd):
        """
        This function inserts the accident data into a table the DB.
        I THINK I'M DOING SOMETHING WRONG WITH THE PASSWORD ARGUMENT, BUT I AM
        NOT A SOFTWARE ENGINEER! THAT PROBABLY SHOULDN'T BE THERE! I SHOULD USE
        SOME OTHER FORM OF AUTHENTICATION.
        Also note that this looks for a database on the local host. This would
        have to change to be deployed to the real world.
        :param dbname: Name of the database to write into.
        :param table: Name of the table to write.
        :param dbuser: Username for the DB.
        :param pswd: Password for the user.
        :return:
        """
        engine = create_engine('postgresql://%s:%s@localhost/%s'
                                        % (dbuser, pswd, dbname))
        self.accidents.to_sql(table, engine, if_exists="append")

