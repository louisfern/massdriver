from flask import render_template
from webapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flask import request
import sys
import os
sys.path.append('/home/louisf/Documents/Insight/massdriver/webapp')
from a_Model import ModelIt

user = 'louisf'
dbname = 'birth_db'
host = 'localhost'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
#db = create_engine('postgresql://%s:%s@localhost/%s'%(user,password,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')

@app.route('/index')
def index():
    return render_template('massdriver.html')

@app.route('/algorithm')
def algorithm():
    return render_template("algorithm.html")

@app.route('/about')
def about():
    return render_template("algorithm.html")
