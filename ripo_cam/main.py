import cv2
import sys
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QIcon
from ultralytics import YOLO
from nava import play, stop_all
#import simpleaudio
import configparser
import numpy

def playy():
    print("Inside danger zone!!!")
    play_object = self.alert_sound.play()
    play_object.wait_done()



class QThread(QThread):
    changePixmap = pyqtSignal(QImage)
    changeIcon = pyqtSignal(bool)
    def __init__(self, capid, piesi, samochod, rowerzysta, leftb, rightb, modelpath):
        super().__init__()
        self.capid = capid
        self.piesi = piesi
        self.samochod = samochod
        self.rowerzysta = rowerzysta
        self.leftb = leftb
        self.rightb = rightb
        
        self.a1 = 2
        self.b1 = 210
        self.a2 = 0
        self.b2 = 150
        self.a3 = -2.3
        self.b3 = 418

        self.model = YOLO(modelpath)
        self.sound_id = None
    def run(self):
        cap = cv2.VideoCapture(self.capid)
        while True:
            ret, frame = cap.read()
            if ret:
                # Perform object detection on the frame
                results = self.detect_objects(frame)

                annotated_frame = results[0].plot()

                rgbImage = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

                h, w, ch = rgbImage.shape
                self.detect_in_danger_zone(results[0].boxes, w, h)
                for i in range(0, rgbImage.shape[0]):
                    for j in range(0, rgbImage.shape[1]):
                        if self.inside(j, i, w, h):
                            rgbImage[i, j, 1] = 0
                            rgbImage[i, j, 2] = 0

                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
                self.changePixmap.emit(p)

        # Function to perform object detection on a single frame
    def detect_objects(self, frame):
        # Perform object detection
        results = self.model(frame, verbose=False)
        return results
    def detect_in_danger_zone(self, boxes, w, h):
        alert = False;
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy.numpy().ravel()
            
            if self.inside(x1, y1, w, h) or self.inside(x1, y2, w, h) or self.inside(x2, y1, w, h) or self.inside(x2, y2, w, h): 
                alert = True;
        if alert:
            self.changeIcon.emit(True)
            if self.sound_id == None:
                self.sound_id = play("alert.wav", async_mode=True, loop=True)
        else:
            self.changeIcon.emit(False)
            self.sound_id = None
            stop_all()
    def inside(self, x, y, w, h):
        x = int((float(x)/w) * 640)
        y = int((float(y)/h) * 480)
        if y > x * (-self.a2) + 480 - self.b2:
            if y > (x - self.b1) * (-self.a1) + 480:
                if y > (x - self.b3) * (-self.a3) + 480:
                    return True
        return False

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(bool)
    def setIcon(self, visible):
        self.label1.setVisible(visible)


    def initUI(self):
        self.setWindowTitle("Video Processor")
        # create a label
        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)

        self.label1 = QLabel(self)
        pixmap = QPixmap('Alert.png')
        self.label1.setPixmap(pixmap)
        self.label1.move(280, 120)

        self.confread()
        th = QThread(self.cameraId, self.piesi, self.samochod, self.rowerzysta, self.leftBorderBox, self.rightBorderBox, self.modelPath)
        th.changePixmap.connect(self.setImage)
        th.changeIcon.connect(self.setIcon)
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
            self.cameraId = int(config['Camera']['id']) if config['Camera']['id'].isdecimal() else config['Camera']['id'] # Try parse as a camera id if not assume it is a video
        except:
            print("Config file not detected or malformed. Please use configurator first")
            self.label.setText("Config file not detected or malformed. Please use configurator first")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
