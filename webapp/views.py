from webapp import app
import pickle
from flask import make_response, json, render_template, jsonify, request
import sys
import graphHandler as gH
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from shapely.geometry import LineString
import numpy as np
import json
import networkx as nx
import re
from cgi import parse_header

sys.path.append('/home/louisf/Documents/Insight/massdriver/webapp')


# Doing a memory and speed optimization hack.
#graph = nx.read_gpickle('/home/louisf/Documents/Insight/massdriver/notebooks/graph_with_risk.pickle')
graph = nx.read_gpickle('/home/louisf/Documents/Insight/massdriver/data/filled_reduced_needs_risk.pickle')
tree = gH.generateKDTree(graph)
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
    rpath = np.asarray(path)
    rpath = np.reshape(rpath.flatten(), (len(rpath), 2))
    print(rpath)
    return make_response(json.dumps(rpath.tolist()))

@app.route('/getWeightOnPath')
def getWeightOnPath():
    wordlist = json.loads(request.args.get('wordlist'))
    points = parseJsonInput(wordlist)
    weight = gH.getWeight(graph, points, True)

    print(weight)
    return jsonify(result=weight)
    #return make_response(json.dumps('okay'))


@app.route('/getWeightOffPath')
def getWeightOffPath():
    wordlist = json.loads(request.args.get('wordlist'))
    points = parseJsonInput(wordlist)
    print('off-ath points incoming')
    print(points)
    weight = gH.getWeight(graph, points, False)
    return jsonify(result=weight)
    #return make_response(json.dumps('okay'))

def parseJsonInput(input):
    """
    Helper function to go from unformatted JSON string to array.
    :param input: The raw string output from JSON request.
    :return: points: A list of (long, lat) tuples
    """
    points = []
    for i in range(0, len(input)):
        points.append(input[i])

    return points

