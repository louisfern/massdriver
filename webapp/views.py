from flask import render_template
from webapp import app
from sqlalchemy import create_engine
import pickle
import psycopg2
from flask import request
import sys
import matplotlib
from matplotlib import pyplot as plt
from flask import send_file
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from io import BytesIO
from shapely.geometry import LineString



import tempfile
sys.path.append('/home/louisf/Documents/Insight/massdriver/webapp')
import numpy as np

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
        ax.plot(x, y, color='GRAY', linewidth=3, solid_capstyle='round', zorder=1)

    fig = plt.figure(1, figsize=(10, 5), dpi=180)
    ax = fig.add_subplot(111)

    for i in range(0, round(percent / 100 * len(itemlist))):
        line = LineString(itemlist[i][1]['line'])
        plot_line(ax, line)
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')
"""
    f = tempfile.NamedTemporaryFile(
        dir='static/temp',
        suffix='.png', delete=False
    )
    hpath = '/home/louisf/Documents/Insight/massdriver/webapp/static/temp/A.png'
    plt.savefig(hpath, bbox_inches='tight')
    plt.savefig(f, bbox_inches='tight')
    f.close()
    plotPng = f.name.split('/')[-1]
    plotPng = 'static/temp/A.png'
    return render_template('massdriver.html', plotPng = plotPng)
"""
