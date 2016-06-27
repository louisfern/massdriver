from webapp import app
import pickle
from flask import make_response, json, render_template, jsonify, request
import sys
import graphHandler as gH
from matplotlib import pyplot as plt
from shapely.geometry import LineString
import numpy as np
import json
import networkx as nx
from cgi import parse_header

import tempfile
sys.path.append('/home/ubuntu/massdriver/webapp')

# Doing a memory and speed optimization hack.
graph = nx.read_gpickle('/home/ubuntu/filled_reduced_needs_risk.pickle')
print('Graph loaded successfully')

@app.route('/')
def root():
    return render_template('massdriver.html')

@app.route('/index')
def index():
    return render_template('massdriver.html')


@app.route('/algorithm')
def algorithm():
    return render_template("algorithm.html")


@app.route('/about')
def about():
    return render_template("about.html")
    

@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('lat1', 0, type=float)
    print(a)
    b = request.args.get('lat2', 0, type=float)
    c = request.args.get('lng1', 0, type=float)
    d = request.args.get('lng2', 0, type=float)
    return jsonify(result=a+b+c+d)


@app.route('/getdirections')
def getdirections():
    lat1 = request.args.get('lat1', 0, type=float)
    lat2 = request.args.get('lat2', 0, type=float)
    lng1 = request.args.get('lng1', 0, type=float)
    lng2 = request.args.get('lng2', 0, type=float)
    print(lat1)
    print(lat2)
    print(lng1)
    print(lng2)
    weight = request.args.get('weight', None, type=str)
    if weight == 'NaN':
        print("weight is nan")
        weight = None
    #graph = gH.NetworkGenerator()
    path = gH.pathingSolution(graph, lat1, lng1, lat2, lng2, weight)
    print(path)
    rpath = np.asarray(path)
    print(rpath)
    rpath = np.reshape(rpath.flatten(), (len(rpath), 2))
    print(rpath)
    return make_response(json.dumps(rpath.tolist()))
