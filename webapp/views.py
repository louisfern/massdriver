from webapp import app
from sqlalchemy import create_engine
import pickle
import psycopg2
from flask import make_response, json, render_template, jsonify, request
import sys
import graphHandler as gH
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from shapely.geometry import LineString
import numpy as np
import json
import networkx as nx
from cgi import parse_header

import tempfile
sys.path.append('/home/louisf/Documents/Insight/massdriver/webapp')

user = 'louisf'
dbname = 'birth_db'
host = 'localhost'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
#db = create_engine('postgresql://%s:%s@localhost/%s'%(user,password,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)


@app.route('/index')
def index():
    return render_template('massdriver.html')


@app.route('/algorithm')
def algorithm():
    return render_template("algorithm.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/massdriver')
def massdriver():
    hackdb = '/home/louisf/Documents/Insight/massdriver/webapp/static/hackdb.pl'
    itemlist = pickle.load(open(hackdb, 'rb'))
    percent = float(request.args.get('ratio'))

    def plot_line(ax, ob):
        x, y = ob.xy
        ax.plot(x, y, color='GRAY', linewidth=2, zorder=1)

    fig = plt.figure(1, figsize=(10, 5), dpi=180)
    ax = fig.add_subplot(111)
    fig.suptitle("Top {} percent of accident-prone roads, predicted".
                 format(str(percent))
                 )
    for i in range(0, round(percent / 100 * len(itemlist))):
        line = LineString(itemlist[i][1]['line'])
        plot_line(ax, line)
    canvas = FigureCanvas(fig)
    f = tempfile.NamedTemporaryFile(
        dir='/home/louisf/Documents/Insight/massdriver/webapp/static/temp',
        suffix='.png', delete=False
    )
    plt.savefig(f, bbox_inches='tight')
    f.close()
    plotPng = f.name.split('/')[-1]

    """
        img = BytesIO()
        fig.savefig(img)
        img.seek(0)
        return send_file(img, mimetype='image/png')
    """

    return render_template('massdriver.html', plotPng = plotPng)


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
    graph = gH.NetworkGenerator()
    #with open('/home/louisf/Documents/Insight/massdriver/graph.pickle', 'rb') as f:
    #    graph = pickle.load(f)
    graph = nx.read_gpickle('/home/louisf/Documents/Insight/massdriver/notebooks/graph_with_risk2.pickle')
    #path = gH.pathingSolution(graph.net, lat1, lng1, lat2, lng2, weight)
    path = gH.pathingSolution(graph, lat1, lng1, lat2, lng2, weight)
    print(path)
    rpath = np.asarray(path)
    rpath = np.reshape(rpath.flatten(), (len(rpath), 2))
    print(rpath)
    #rpath = np.array([[lng1, lat1], [lng2, lat2]])
    #return jsonify(result=rpath)
    #return jsonify(result=lat1)
    return make_response(json.dumps(rpath.tolist()))
