from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog

from .ConfigUi import Ui_ConfigDialog
from .ForwardUi import Ui_GeocodingForm

from time import sleep

from PyQt5.QtCore import QObject, QThread, pyqtSignal

API_KEY_SETTINGS_NAME = 'GeoapifyGeocoding/apiKey'
OUTPUT_LAYER_NAME = 'GeoapifyGeocoding/outputLayer'

# Step 1: Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, int)

    def run(self):
        self.progress.emit(0, 5)

        for i in range(5):
            sleep(1)
            self.progress.emit(i + 1, 5)

            if QThread.currentThread().isInterruptionRequested():
                break

        self.finished.emit()

class ConfigDialog(QDialog, Ui_ConfigDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        settings = QSettings()
        current_key = settings.value(API_KEY_SETTINGS_NAME, '<your-api-key>')
        self.apiKey.setText(current_key)

        current_layer_name = settings.value(OUTPUT_LAYER_NAME, 'Geoapify Geocoding Results')
        self.outputLayer.setText(current_layer_name)


class ForwardDialog(QDialog, Ui_GeocodingForm):
    geocodingThread = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.updateListPlaceholder()

    def updateListPlaceholder(self): 
        if self.inputType.currentIndex() == 0:
            print("address")
            self.addressList.setPlaceholderText('Here are examples of free-form addresses:\n\n1234 Elm Street, Anytown, CA 12345, USA\n5678 Oak Avenue, Nowhereville, TX 67890\n9012 Maple Lane, Imaginary City, NY 11111\n3456 Pine Road, Springfield, FL 98765')
        elif self.inputType.currentIndex() == 1:
            print("lat/lon")
            self.addressList.setPlaceholderText('Here are example of latitude/longitude (WGS 84 Web Mercator) pairs:\n\n48.8611,2.3354\n51.5194,-0.1269\n43.7679,11.2553\n52.3600,4.8852')
        else: 
            print("lon/lat")
            self.addressList.setPlaceholderText('Here are examples of longitude/latitude (WGS 84 Web Mercator) pairs:\n\n2.3354,48.8611\n-0.1269,51.5194\n11.2553,43.7679\n4.8852,52.3600')

    def addressListChanged(self):
        text = self.addressList.toPlainText()

        count = 0

        for line in text.split("\n"):
            word = line.strip()
            print(word)
            if word:
                print(word)
                count += 1

        self.stepLabel.setText(f"{count} lines to process")
        self.progressBar.setValue(0)


    def toggleProcessing(self):
        if self.geocodingThread and self.geocodingThread.isRunning():
            print(self.geocodingThread)
            self.geocodingThread.requestInterruption()
        else:
            self.runGeocoding()

    def reportProgress(self, n, count):
        if n == count:
            self.stepLabel.setText(f"{count} lines processed")
            self.progressBar.setValue(100)
        else:
            self.stepLabel.setText(f"{n} from {count} processed")
            self.progressBar.setValue(round((n / count) * 100))

    def runGeocoding(self):
        # Step 2: Create a QThread object
        self.geocodingThread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.geocodingThread)
        # Step 5: Connect signals and slots
        self.geocodingThread.started.connect(self.worker.run)
        self.worker.finished.connect(self.geocodingThread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.geocodingThread.finished.connect(self.geocodingThread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.geocodingThread.start()

        # Final resets
        self.makeUIRunning()

        self.geocodingThread.finished.connect(
            lambda: self.makeUIStopped()
        )

        self.geocodingThread.finished.connect(
            lambda: self.cleanUp()
        )

    def makeUIRunning(self):
        self.closeButton.setEnabled(False)
        self.inputType.setEnabled(False)
        self.addressList.setEnabled(False)
        self.runButton.setText("Stop")

    def makeUIStopped(self):
        self.closeButton.setEnabled(True)
        self.inputType.setEnabled(True)
        self.addressList.setEnabled(True)
        self.runButton.setText("Run")

    def cleanUp(self):
        self.geocodingThread = None