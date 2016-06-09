"""
riskModelBuilder.py
This module queries my Postgres DB, does some data re-arrangement,
and performs a linear regression on the data.

Contents:

Required packages:
pandas
numpy
psycopg2
sqlacademy
sklearn

Acknowledgements: For a list of acknowledgements, see the information at
INSERT WEBSITE HERE.

Louis Fernandes, 2016 06 08
"""

import pandas as pd
import psycopg2
import numpy as np
from sklearn import preprocessing as skpre
from sklearn import linear_model
from sklearn.cross_validation import cross_val_predict
from sklearn.cross_validation import cross_val_score



class Alldata():
    """
    This class retrieves data stored in a Postgres database and contains
    methods for manipulating said data.

    Properties:
        dbinfo: A dict of database connection parameters.
        table: A numpy array of the data pulled from the database.
        traindata:

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
        self.traindata = None
        self.test = None
        self.t2 = None

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

    def cleanData(self, todrop=['adt', 'assignedle', 'naccidents']):
        """
        This function does a fair amount of data wrangling.
        - Computes the number of accidents per day per mile per average
        daily traffic, known here as 'acc_risk'.
        - Strips out the 'adt', 'assignedle', and 'naccidents' values
        from the data set.
        - Sets up a training data set for those segments that have a finite
        acc_risk
        - Removes strings from the training set
        - Converts the table to a numpy array for later machine learning.
        - Removes categorical variables.
        - Normalizes each row by setting to zero mean and unity variance

        :return:
        TO DO:
        Drop an arbitrary set of input columns
        """
        self.table['acc_risk'] = self.table['naccidents']\
            / self.table['assignedle'] /self.table['adt']
        if todrop:
            self.table.drop(todrop, axis=1, inplace=True)
        temp = self.table.copy()
        self.t2 = self.table.copy()
        temp2 = temp.loc[~pd.isnull(temp['acc_risk']), 'acc_risk']
        temp3 = temp2.replace([np.inf, -np.inf], np.nan).dropna(how="all")
        nonan = self.table.iloc[temp3.index]

        self.test = nonan

        x = nonan.select_dtypes(include=['int64', 'float64'])\
            .as_matrix()

        unique_values = [len(np.unique(x[:, i])) for i in range(x.shape[1])]
        enc = skpre.OneHotEncoder(categorical_features=
                                  np.array(unique_values) < 30)
        x_nocat = enc.fit_transform(x).toarray()
        self.test=x_nocat
        x_norm_nocat = (x_nocat-np.mean(x_nocat, axis=0)/np.std(x_nocat, axis=0))
        infinites = sum(np.isinf(x_norm_nocat))
        x_norm_nocat = x_norm_nocat[:,infinites == 0]
        drop_me = ~np.isnan(x_norm_nocat.sum(axis=0))
        self.traindata = x_norm_nocat[:, drop_me]


class Model():
    """
    This class uses a previously generated numpy array to regress a data set
    onto a given row.

    Properties:

    Methods:
        linear_crossval


    """

    def __init__(self):
        self.predicted = None
        self.scores = None

    def linear_crossval(self, x, y, folds):
        lr = linear_model.LinearRegression()
        predicted = cross_val_predict(lr, x, y, cv=folds)
        scores = cross_val_score(lr, x, y, cv=folds)
        self.predicted = predicted
        self.scores = scores


