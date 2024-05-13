import cv2
import sys
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from ultralytics import YOLO
import configparser


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    def __init__(self, capid, piesi, samochod, rowerzysta, leftb, rightb, modelpath):
        super().__init__()
        self.capid = capid
        self.piesi = piesi
        self.samochod = samochod
        self.rowerzysta = rowerzysta
        self.leftb = leftb
        self.rightb = rightb

        self.model = YOLO(modelpath)
    def run(self):
        cap = cv2.VideoCapture(self.capid)
        while True:
            ret, frame = cap.read()
            if ret:
                # Perform object detection on the frame
                results = self.detect_objects(frame)

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
                self.changePixmap.emit(p)

        # Function to perform object detection on a single frame
    def detect_objects(self, frame):
        # Perform object detection
        results = self.model(frame)
        print(results)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle("Video Processor")
        # create a label
        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)

        self.confread()
        th = Thread(self.cameraId, self.piesi, self.samochod, self.rowerzysta, self.leftBorderBox, self.rightBorderBox, self.modelPath)
        th.changePixmap.connect(self.setImage)
        th.start()

        self.show()

    def confread(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        try:
            self.piesi = True if config['Objects']['piesi'] == 'True' else False
            self.samochod = True if config['Objects']['samochod'] == 'True' else False
            self.rowerzysta = True if config['Objects']['rowerzysta'] == 'True' else False
            self.modelPath = config['Model']['path']
            self.leftBorderBox = int(config['Zone']['left'])
            self.rightBorderBox = int(config['Zone']['right'])
            self.cameraId = int(config['Camera']['id'])
        except:
            print("Config file not detected or malformed. Please use configurator first")
            self.label.setText("Config file not detected or malformed. Please use configurator first")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
