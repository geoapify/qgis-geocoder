# Geoapify Geocoder - QGIS plugin

## How to install this plugin from source

Your QGIS installation comes with a default directory tree of configuration files and more. In recent versions of QGIS
you can find this `default` directory by opening QGIS and navigating to `Settings > User Profiles > Open Active Profile Folder`.

This will open the `default` directory in your system's file explorer. Copying the entire
[geoapify_geocoder](geoapify_geocoder) directory to `default/python/plugins/` will make the plugin available after a
restart of QGIS.

## How to use this plugin

1. Add a tile layer to QGIS. E.g., you can configure and add an "XYZ Tile" in the `Browser` menu of QGIS. If you have
not already, right-click on "XYZ Tile", "New Connection...", and add the configuration details of your tiles provider.
If you chose Geoapify as your tile server, check out [Geoapify map tiles](https://apidocs.geoapify.com/docs/maps/map-tiles/#about).
Double-click on the newly created tile connection to add a tile layer.
2. Make sure you have activated the `Geoapify Geocoder` plugin by navigating to `Plugins > Manage and Install Plugins... > Installed`.
Add a check mark to our plugin. If you cannot find that plugin, you may need to review again the installation process
or simply restart QGIS.
3. Now our plugin menu should appear under menu `Web > Geoapify Geocoding`. Start with the `Settings` sub menu and add
your Geoapify API key - you can create a key for free at [geoapify.com](https://www.geoapify.com/).
4. Use the `Forward Geocoding` sub menu for a free text address search.
5. Use the `Reverse Geocoding` sub menu to change your cursor into a cross. Click with this new cursor somewhere on
the map tile to trigger reverse geocoding.
6. Check out the `Geoapify Results` vector layer containing entries for each forward and reverse geocoding. Right-click
on this layer and navigate to the `Export` menu to extract the data in any of the supported formats.


## Notes for plugin developers

### Development environment

The goal was to create a plugin which depends only on libraries shipped with a standard QGIS installation - QGIS
comes with a preinstalled Python environment, covering many common third party libraries including the `scipy` stack,
`PyQt5`, and `pyqgis`. Thus, it made sense to choose that same environment as the project interpreter instead of
creating a virtual environment. On my Mac, using QGIS 3.28, the Python executable is located at
`/Applications/QGIS.app/Contents/MacOS/bin/python3`.

You may still wish to add `PyQt5` to your standard Python environment (or a virtual environment) so that the `pyuic5`
CLI is covered by your Python path - or append the path to `bin` of your QGIS default Python environment to your PATH
variable.

### Creating the plugin's graphical user interface

The default QGIS Python environment comes with all the libraries we need to build the plugin. That also requires solid
familiarity with the `PyQt5` framework. That framework is used to code the graphical user
interface of the plugin (and everything else of QGIS). Instead, we chose to create
the GUI using [Qt Creator](https://www.qt.io/product/development-tools). This is how it works:

1. Open the Qt Creator desktop app and create a GUI (window, or "dialog") using the graphical toolbox. Save results as a
`<gui-file>.ui` file.
2. Assuming that the file is in the current working directory of your terminal, parse it with
```bash
pyuic5 -o <gui-file>.py <gui-file>.ui
```
3. Create a new Dialog class by inheriting the class from `<gui-file>.py` side by side with the `QDialog` class and add
functionality as needed.

Submodule [geoapify_geocoder/gui](geoapify_geocoder/gui) covers two such Dialog examples. The two
`.ui` files have been created with `Qt Creator` and parsed with `pyuic5` to the corresponding `.py` files. File
[dialogs.py](geoapify_geocoder/gui/dialogs.py) is the result of the last step.

### Other implementation details

#### The main plugin class

Module [geoapify_geocoder.py](geoapify_geocoder/geoapify_geocoder.py) is where you should start with when exploring
the implementation details. (Not all but most) QGIS plugins consist of such a main module, with methods
`initGui` and `unload` being mandatory. `initGui` is responsible for adding the plugin menu. Every "action" gets
its own sub menu entry. And we define what happens when an action is executed. This plugin comes with three actions:

- Forward Geocoding: initiates a dialog with a free text search. Entering a text triggers a forward geocoding
request. The top result is added as a point feature to the map.
- Reverse Geocoding: the mouse cursor changes into a cross, ready to accept clicks as input. Each click on the map
triggers are reverse geocoding request using the coordinates from the click event. The result is added as a point
feature to the map.
- Settings: initiates a dialog with a free text field. Here we can set our Geoapify API key which is then persistently
stored as a QGIS setting.

#### Else

Our plugin is using network requests for geocoding. Python developers prefer the `requests` library for such jobs.
In QGIS, however, this may result in errors. Instead, it is recommended to use `QgsBlockingNetworkRequest` and similar
`pyqgis` alternatives. Our example in module [client.py](geoapify_geocoder/common/client.py) demonstrates how to send
GET requests.

Our reverse geocoding action is using the input from a mouse click. To make this work, we have implemented a rather
generic [click_tool](geoapify_geocoder/common/click_tool.py).
