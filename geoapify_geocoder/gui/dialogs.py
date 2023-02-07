from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog

from .ConfigUi import Ui_ConfigDialog
from .ForwardUi import Ui_GeoCoding

API_KEY_SETTINGS_NAME = 'GeoapifyGeocoding/apiKey'
OUTPUT_LAYER_NAME = 'GeoapifyGeocoding/outputLayer'


class ConfigDialog(QDialog, Ui_ConfigDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        settings = QSettings()
        current_key = settings.value(API_KEY_SETTINGS_NAME, '<your-api-key>')
        self.apiKey.setText(current_key)

        current_layer_name = settings.value(OUTPUT_LAYER_NAME, 'Geoapify Results')
        self.outputLayer.setText(current_layer_name)


class ForwardDialog(QDialog, Ui_GeoCoding):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
