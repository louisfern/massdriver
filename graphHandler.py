"""
graphHandler.py
This module was written to interface with my road data shapefile and convert
it to a graph. It also handles interacting with that graph and providing
routes and information about those routes.

Louis Fernandes, 2016 06 15
"""

from osgeo import ogr, osr
import networkx as nx
from matplotlib import pyplot as plt


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
        try:
            from osgeo import ogr
        except ImportError:
            raise ImportError("read_shp requires OGR: http://www.gdal.org/")

        if not isinstance(path, str):
            return

        net = nx.Graph()
        shp = ogr.Open(path)
        for lyr in shp:
            # fields = [x.GetName() for x in lyr.schema]
            layerit = 0
            nbad = 0
            ngood = 0
            for f in lyr:
                layerit += 1
                flddata = [f.GetField(f.GetFieldIndex(x)) for x in fields]
                g = f.geometry()
                if g is None:
                    print('g is None, layer iteration: {0}'.format(str(layerit)))
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


class NetworkAnalyzer:
    """
    This class provides methods for the analysis and querying of a network.
    You should already have a network generated, perhaps from 
    """