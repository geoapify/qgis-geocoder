import os.path
from qgis.PyQt.QtCore import QSettings, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import (
    QgsPointXY, QgsVectorLayer, QgsProject, QgsField, QgsFeature, QgsGeometry, QgsPalLayerSettings,
    QgsVectorLayerSimpleLabeling
)
from qgis.gui import QgisInterface
from typing import Callable

from .common.click_tool import ClickTool
from .common.client import QgsGeoapifyClient
from .gui.dialogs import ConfigDialog, ForwardDialog, API_KEY_SETTINGS_NAME


class GeoapifyGeocoder:

    def __init__(self, iface: QgisInterface):
        """Geoapify Geocoder - QGIS plugin.

        """
        self.iface = iface
        self.actions = []
        self.menu = None

        self._dir_icons = os.path.dirname(__file__) + '/gui/img/'
        self._data_layer_name = 'Geoapify Results'

    def initGui(self):
        """Add the plugin's menu to the QGIS GUI.

        The menu consists of multiple entries, one entry per "action":
        - Forward Geocoding: a dialog with a free text search creating points on map.
        - Reverse Geocoding: a cursor where clicks result in reverse geocoded points on map.
        - Settings: a persistent storage of your Geoapify API key.
        """
        # Main plugin menu:
        self.menu = QMenu('Geoapify Geocoding')
        self.menu.setIcon(QIcon(self._dir_icons + 'geoapify-logo.png'))

        # Add menu entries, called "actions":
        self._add_action(
            self._dir_icons + 'forward.png',
            name='Forward Geocoding',
            callback=self._show_forward_geocode_dialog)
        self._add_action(
            self._dir_icons + 'reverse.png',
            name='Reverse Geocoding',
            callback=self._init_cursor_for_reverse_geocoding)
        self._add_action(
            self._dir_icons + 'gear.png',
            name='Settings',
            callback=self._show_settings_dialog)

        self.menu.addActions(self.actions)

        self.iface.webMenu().addMenu(self.menu)

    def unload(self):
        """Remove menu from GUI.

        Unloading the plugin will only remove the menu. Any data created in a vector layer will persist.
        """
        self.iface.webMenu().removeAction(self.menu.menuAction())

    def _add_action(self, icon_path: str, name: str, callback: Callable):
        """Add a single action.

        :param icon_path: path to the icon used in the menu.
        :param name: name of the menu entry.
        :param callback: a callable triggered by selecting the menu entry of the action.
        """
        icon = QIcon(icon_path)
        action = QAction(icon, name, self.iface.mainWindow())
        action.triggered.connect(callback)
        action.setEnabled(True)

        self.actions.append(action)

    def _show_forward_geocode_dialog(self):
        """Dialog for forward geocoding.

        Show the dialog for free text address search, forward geocode, and add point feature to layer.
        """
        diag = ForwardDialog()
        diag.show()
        ok_pressed = diag.exec()

        if ok_pressed:
            search_input = diag.address.text()

            settings = QSettings()
            client = QgsGeoapifyClient(api_key=settings.value(API_KEY_SETTINGS_NAME))

            res = client.geocode(text=search_input)
            point = QgsPointXY(res['properties']['lon'], res['properties']['lat'])
            label = res['properties']['formatted']
            self._add_point_to_layer(point=point, label=label)

    def _add_point_to_layer(self, point: QgsPointXY, label: str) -> None:
        """Adds a point feature to the layer called "Geoapify".

        This point layer will display labels on the map by default. You can disable labels in the GUI. We also
        store that label as the only attribute. You can add as many attributes as you like which are then added
        as columns to the "Attribute table".

        :param point: QgsPointXY instance in (lon, lat) coordinates.
        :param label: label displayed on the map.
        """
        if not QgsProject.instance().mapLayersByName(layerName=self._data_layer_name):
            # Create new layer if not exists:
            vl = QgsVectorLayer('Point', self._data_layer_name, 'memory')

            # Show labels on map by default:
            label_settings = QgsPalLayerSettings()
            label_settings.fieldName = "Address"
            vl.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
            vl.setLabelsEnabled(True)

            # We can store any number of properties - below we just store our label as the "Address" attribute
            pr = vl.dataProvider()
            # Enter editing mode
            vl.startEditing()
            # add fields
            pr.addAttributes([QgsField("Address", QVariant.String)])
            QgsProject.instance().addMapLayer(vl)
        else:
            # Use existing layer:
            vl = QgsProject.instance().mapLayersByName(layerName=self._data_layer_name)[0]

        # Add point feature to layer - including the label as its only attribute:
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPointXY(point))
        fet.setAttributes([label])
        pr = vl.dataProvider()
        pr.addFeatures([fet])

        vl.commitChanges()

    def _init_cursor_for_reverse_geocoding(self) -> None:
        """Initialize the cursor for reverse geocoding.

        The ClickTool instance tracks clicks on the map and responds with reverse geocoding of corresponding
        coordinates.
        """
        canvas = self.iface.mapCanvas()
        point_tool = ClickTool(iface=self.iface, callback=self._reverse_geocode_and_add_to_layer)
        canvas.setMapTool(point_tool)

    def _reverse_geocode_and_add_to_layer(self, point: QgsPointXY) -> None:
        """Callback used in the ClickTool for reverse geocoding.

        Reverse geocode coordinates coming from the ClickTool instance and add point feature to layer.

        :param point: QgsPointXY instance in (lon, lat) coordinates.
        """
        settings = QSettings()
        client = QgsGeoapifyClient(api_key=settings.value(API_KEY_SETTINGS_NAME))

        res = client.reverse_geocode(longitude=point.x(), latitude=point.y())
        point = QgsPointXY(res['properties']['lon'], res['properties']['lat'])
        label = res['properties']['formatted']
        self._add_point_to_layer(point=point, label=label)

    @staticmethod
    def _show_settings_dialog() -> None:
        """Dialog for setting the Geoapify API key.

        """
        diag = ConfigDialog()
        diag.show()
        ok_pressed = diag.exec()

        if ok_pressed:
            settings = QSettings()
            new_val = diag.apiKey.text()
            settings.setValue(API_KEY_SETTINGS_NAME, new_val)
