from flask import render_template
from webapp import app
from sqlalchemy import create_engine
import pickle
import psycopg2
from flask import Response, json, render_template, jsonify
import sys
import graphHandler as gH
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from shapely.geometry import LineString
import numpy as np
import json

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


@app.route('/getdirections', methods=['GET', 'POST'])
#def getdirections(lat1, long1, lat2, long2, weight=None):
def getdirections():
    data_json = request.body
    graph = gH.NetworkGenerator()
    filepath = '/home/louisf/Documents/Insight/massdriver/data/raw/shapefile/RI_converted.shp'
    graph.loadGraph(filepath=filepath, fields=['RoadSegmen', 'AssignedLe'], simplify=True)
    path = gH.pathingSolution(graph.net, lat1, long1, lat2, long2, weight)
    rpath = np.asarray(path)
    rpath = np.reshape(rpath.flatten(), (len(rpath), 2))
    return rpath