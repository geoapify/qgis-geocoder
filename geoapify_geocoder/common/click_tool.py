"""Catch mouse click events and respond with a function call.

Reverse geocoding takes as input the point coordinates from a mouse click on the map. This is the corresponding
implementation to capture those mouse events. In the Qt framework, we implement such user interactions with the map
by inheriting from the QgsMapTool class and overwriting respective methods.

This simple ClickTool implementation is inspired by https://github.com/elpaso/qgis-geocoding/blob/master/Utils.py.
"""

from qgis.PyQt.QtGui import QMouseEvent
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY, QgsProject
from qgis.gui import QgsMapTool, QgisInterface
from typing import Callable


class ClickTool(QgsMapTool):
    def __init__(self, iface: QgisInterface, callback: Callable):
        """

        :param iface: interface instance where clicks are observed.
        :param callback: callable with a single argument of type QgsPointXY in EPSG:4326 coordinates.
        """
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.callback = callback
        self.canvas = iface.mapCanvas()

    def canvasReleaseEvent(self, event: QMouseEvent):
        # event.pos() is a QPoint; transform to QgsPontXY:
        point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())

        # Transform to (lon, lat) coordinates:
        dest_crs = QgsCoordinateReferenceSystem()
        dest_crs.createFromString('EPSG:4326')
        transformer = QgsCoordinateTransform(
            self.iface.mapCanvas().mapSettings().destinationCrs(), dest_crs, QgsProject.instance())
        point = transformer.transform(point)

        # Execute callback:
        self.callback(point)
