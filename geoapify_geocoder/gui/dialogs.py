from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog

from .ConfigUi import Ui_ConfigDialog
from .ForwardUi import Ui_GeoCoding

API_KEY_SETTINGS_NAME = 'GeoapifyGeocoding/apiKey'


class ConfigDialog(QDialog, Ui_ConfigDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        settings = QSettings()
        current_key = settings.value(API_KEY_SETTINGS_NAME, '<your-api-key>')
        self.apiKey.setText(current_key)


class ForwardDialog(QDialog, Ui_GeoCoding):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
