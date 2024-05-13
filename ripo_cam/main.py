import cv2
import sys
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from ultralytics import YOLO
import simpleaudio
import configparser
import numpy


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
        self.alert_sound = simpleaudio.WaveObject.from_wave_file('alert.wav')
        
        self.a1 = 1
        self.b1 = 1
        self.a2 = 0
        self.b2 = 600
        self.a3 = -1
        self.b3 = 1080

        self.model = YOLO(modelpath)
        self.danger_zone = self.create_danger_zone()
    def run(self):
        cap = cv2.VideoCapture(self.capid)
        while True:
            ret, frame = cap.read()
            if ret:
                # Perform object detection on the frame
                results = self.detect_objects(frame)

                annotated_frame = results[0].plot()
                print(len(results[0].boxes))
                self.detect_in_danger_zone(results[0].boxes)

                rgbImage = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

                for i in range(0, rgbImage.shape[0]):
                    for j in range(0, rgbImage.shape[1]):
                        if self.inside(j, i):
                            rgbImage[i, j, 1] = 0
                            rgbImage[i, j, 2] = 0

                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
                self.changePixmap.emit(p)

        # Function to perform object detection on a single frame
    def detect_objects(self, frame):
        # Perform object detection
        results = self.model(frame)
        # print(results)
        return results
    def detect_in_danger_zone(self, boxes):
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy.numpy().ravel()
            
            print(str(x1) + " - " + str(x2) + "\n" + str(y1) + "\n|\n" + str(y2) + "\n")
            if self.inside(x1, y1) or self.inside(x1, y2) or self.inside(x2, y1) or self.inside(x2, y2):
                play_object = self.alert_sound.play()
                play_object.wait_done()
                print("Inside danger zone!!!")

    def inside(self, x, y):
        if y > x * self.a2 + self.b2:
            if x < y * self.a1 + self.b1:
                if x > y * self.a3 + self.b3:
                    return True
        return False

    def create_danger_zone(self):
        zone = numpy.zeros((1080, 1920, 3))
        for i in range(0, 1920):
            for j in range(0, 1080):
                if self.inside(j, i):
                    zone[j, i, 0] = 1.0
        print(zone)
        return zone

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
