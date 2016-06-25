"""
graphHandler.py
This module was written to interface with my road data shapefile and convert
it to a graph. It also handles interacting with that graph and providing
routes and information about those routes.

This class also provides methods for the analysis and querying of a network.
You should already have a network generated, perhaps from a database?
How fancy am I?

Louis Fernandes, 2016 06 15
"""

from osgeo import ogr
import more_itertools as mtool
import networkx as nx
import scipy.spatial.distance as distance
import scipy.spatial as spatial
import numpy as np
import time


class NetworkGenerator:
    """
    This class provides support for generating and managing a graph.
    loadGraph populates a network, reading in a shapefile and assigning nodes
    and edges as appropriate.
    """

    def __init__(self):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.net = None

    def loadGraph(self, filepath, fields, simplify=True):
        """

        :param filepath: file or string. File, directory, or filename to read.
        :param fields: list. A list of fields to pass on to the graph edges.
        :param simplify: bool.
            If ``True``, simplify line geometries to start and end coordinates.
            If ``False``, and line feature geometry has multiple segments, the
            non-geometric attributes for that feature will be repeated for each
            edge comprising that feature.
        :return:
        """
        self.net = NetworkGenerator.read_shp2(
            filepath, fields, simplify=simplify)

    def read_shp2(path, fields, simplify=True):
        """Generates a networkx.Graph from shapefiles. Point geometries are
        translated into nodes, lines into edges. Coordinate tuples are used as
        keys. Attributes are preserved, line geometries are simplified into start
        and end coordinates. Accepts a single shapefile or directory of many
        shapefiles.

        "The Esri Shapefile or simply a shapefile is a popular geospatial vector
        data format for geographic information systems software [1]_."

        This function is basically copy/pasted from the NetworkX package, with
        a couple modifications to handle error cases/make an undirected graph.


        Parameters
        ----------
        path : file or string
           File, directory, or filename to read.

        fields: list
           A list of fields to pass on to the graph edges.

        simplify:  bool
            If ``True``, simplify line geometries to start and end coordinates.
            If ``False``, and line feature geometry has multiple segments, the
            non-geometric attributes for that feature will be repeated for each
            edge comprising that feature.

        Returns
        -------
        G : NetworkX graph

        Examples
        --------
        >>> G=nx.read_shp('test.shp') # doctest: +SKIP

        References
        ----------
        .. [1] http://en.wikipedia.org/wiki/Shapefile
        read_shp, from the NetworkX module
        """

        net = nx.Graph()
        shp = ogr.Open(path)
        for lyr in shp:
            # fields = [x.GetName() for x in lyr.schema]
            nbad = 0
            ngood = 0
            for f in lyr:
                flddata = [f.GetField(f.GetFieldIndex(x)) for x in fields]
                g = f.geometry()
                if g is None:
                    nbad += 1
                    continue
                attributes = dict(zip(fields, flddata))
                attributes["ShpName"] = lyr.GetName()
                if g.GetGeometryType() == 1:  # point
                    net.add_node((g.GetPoint_2D(0)), attributes)
                if g.GetGeometryType() == 2:  # linestring
                    last = g.GetPointCount() - 1
                    if simplify:
                        attributes["Wkb"] = g.ExportToWkb()
                        attributes["Wkt"] = g.ExportToWkt()
                        attributes["Json"] = g.ExportToJson()
                        net.add_edge(g.GetPoint_2D(0), g.GetPoint_2D(last), attributes)
                    else:
                        # separate out each segment as individual edge
                        for i in range(last):
                            pt1 = g.GetPoint_2D(i)
                            pt2 = g.GetPoint_2D(i + 1)
                            segment = ogr.Geometry(ogr.wkbLineString)
                            segment.AddPoint_2D(pt1[0], pt1[1])
                            segment.AddPoint_2D(pt2[0], pt2[1])
                            attributes["Wkb"] = segment.ExportToWkb()
                            attributes["Wkt"] = segment.ExportToWkt()
                            attributes["Json"] = segment.ExportToJson()
                            del segment
                            net.add_edge(pt1, pt2, attributes)
                ngood += 1
            print('good = {0}, bad = {1}'.format(str(ngood), str(nbad)))
        return net


def generateKDTree(network):
    """
    This function takes in a network and computes the corresponding K-D Tree
    for it, using the cKDTree function from scipy. This lets me do blazingly
    fast nearest point searches, > 1000X faster than my naive implementation.
    :param network: A networkx graph.
    :return: tree: A K-D Tree of the networkx graph.
    """
    tree = spatial.cKDTree(np.asarray(network.nodes()))
    return tree


def findClosestNodeTree(tree, points):
    """
    This function uses a K-D Tree to find the closest points to the input
    points array. This is much MUCH faster than my least distance computation.
    :param tree: A K-D Tree generated with generateKDTree
    :param points: A list of lng, lat tuples
    :return: closestNodes: A numpy array of lng, lat that corresponds to the
    shortest path.
    """
    dist, indices = tree.query(points)
    closestNodes = points[indices]
    return closestNodes


def findClosestNode(network, lat, long):
    """
    This function returns the lat and long of the closest node to an input set
    of coordinates using cdist from numpy.distance.
    :param network: A graph.
    :param lat: Latitude of input.
    :param long: Longitude of input.
    :return: [long, lat] of closest point
    """
    a = np.array([[long, lat]])
    others = np.asarray(network.nodes())

    def closest_point(pt, others):
        distances = distance.cdist(pt, others)
        return distances.argmin()

    closest = closest_point(a, others)
    return others[closest, :]


def getShortestPath(network, start, end, weight=None):
    """
    This function returns a list of coordinates that define the shortest path.
    :param network: A graph.
    :param start: A (long, lat) tuple.
    :param end: A (long, lat) tuple.
    :param weight: The field to use as weights on the edges. Default none.
    :return:
    """
    path = nx.shortest_path(network, source=start, target=end, weight=weight)
    return path


def pathingSolution(network, lat1, long1, lat2, long2, weight=None):
    """"
    This is the top level script for generating paths.
    :param network: A graph.
    :param lat1: Latitude of the starting point.
    :param long1: Longitude of the starting point.
    :param lat2: Latitude of the starting point.
    :param long2: Longitude of the starting point.
    :param weight: The field to use as weights on the edges. Default none.
    :return path: A list of (long, lat) tuples.
    """
    start = findClosestNode(network, lat1, long1)
    end = findClosestNode(network, lat2, long2)
    path = getShortestPath(network, tuple(start), tuple(end), weight=weight)

    return path


def pathWeight(network, path, method="sum", weight='assignedle'):
    """
    This function returns risk along the edges defined by the nodes in path
    according to the methods outlined in method using weights. THIS FUNCTION
    ASSUMES A FRIENDLY ACTOR. PLEASE DON'T ABUSE IT. I AM DELIBERATELY SKIPPING
    INPUT VALIDATION HERE.
    :param network: A networkx graph object.
    :param path: A dict of nodes to traverse.
    :param method: A string desribing the accumulation method. The only valid
    input right now is "sum", but you could imagine placing "multiplicative" or
    some other method here. "sum" is default.
    :param weight: The weight to use when accumulating the edges. Defaults to
    'assignedle'. Valid options are any parameter that exists on all edges of
    the graph. If None, weight is set to "assignedle"
    :return: totalweight: The total weight from the edges.
    """

    if weight is None:
        weight = "assignedle"

    totalweight = 0
    if method == 'sum':
        it = 0
        for node in path:
            it += 1
            if it < len(path):
                totalweight += network[node][path[it]][weight]

    return totalweight


def getdirections(graph, lat1, lng1, lat2, lng2, weight=None):
    """
    This is a high-level function for doing pathing on a graph.
    :param graph: A networkx graph object, whose nodes are lat, long
    :param lat1: Latitude of start.
    :param lng1: Longitude of start.
    :param lat2: Latitude of destination.
    :param lng2: Longitude of destination.
    :param weight: Weight to use for pathing. Valid values are properties of
    the graph edges. Some defaults are set to "assignedle"
    :return: rpath, a list of tuples of long, lat coordinates.
    """
    if weight == 'NaN':
        print("weight is nan")
        weight = None
    path = pathingSolution(graph, lat1, lng1, lat2, lng2, weight)
    rpath = np.asarray(path)
    rpath = np.reshape(rpath.flatten(), (len(rpath), 2))
    print(rpath)
    return rpath.tolist()


def getWeight(graph, path, onGraph, method='sum', weight='assignedle'):
    """ This function returns the total weight of the route, using the
    accumulation method and weight specified.
    :param graph:
    :param path:
    :param onGraph:
    :param method='sum':
    :param weight='assignedle':
    """

    if onGraph:
        return pathWeight(graph, path, method, weight)
    else:
        modpath = pathAlign(graph, path)
        return pathWeight(graph, path, method, weight)


def pathAlign(graph, path):
    """
    This function takes in a list of (long, lat) tuples and returns an
    approximated path formed by matching the closest coordinates in the
    provided graph.
    :param graph: A networkx graph object.
    :param path: A list of long, lat tuples to re-align.
    :return: newPath: A list of re-computed long, lat tuples.
    """
    print('starting the path alignment')
    ti = time.time()

    tree = generateKDTree(graph)
    dist, indices = tree.query(path)
    t = np.asarray(graph.nodes())
    newPath = t[indices]
    t2 = time.time()-ti
    print("ending path alignment, {}".format(t2))

    return newPath
