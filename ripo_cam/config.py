import configparser
import cv2
import sys
from PyQt6.QtWidgets import QApplication, QSlider, QDial, QLineEdit, QWidget, QPushButton, QCheckBox, QVBoxLayout, QLabel, QLineEdit, QFileDialog, \
    QSpinBox
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QIcon
import numpy as np

class QThreadPreview(QThread):
    changePixmap = pyqtSignal(QImage)
    def __init__(self):
        super().__init__()
        self.a1 = 0
        self.b1 = 0
        self.a2 = 0
        self.b2 = 0
        self.a3 = 0
        self.b3 = 0
        self.capid = 0



    def run(self):
        self.capture()
        while(True):
            self.preview()

    def capture(self):
        try:
            self.cap = cv2.VideoCapture(self.capid)
            ret, frame = self.cap.read()
            if ret:
                self.orgin_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            print("Error while reading frame")

    def refresh(self):
        ret, frame = self.cap.read()
        if ret:
            self.orgin_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def preview(self):
        rgbImage = np.copy(self.orgin_frame)

        h, w, ch = rgbImage.shape
        for i in range(0, rgbImage.shape[0]):
            for j in range(0, rgbImage.shape[1]):
                if self.inside(j, i, w, h):
                    rgbImage[i, j, 1] = 0
                    rgbImage[i, j, 2] = 0

        bytesPerLine = ch * w
        convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        p = convertToQtFormat.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        self.changePixmap.emit(p)

    def inside(self, x, y, w, h):
        x = int((float(x)/w) * 640)
        y = int((float(y)/h) * 480)
        if y > x * (-self.a2) + 480 - self.b2:
            if y > (x - self.b1) * (-self.a1) + 480:
                if y > (x - self.b3) * (-self.a3) + 480:
                    return True
        return False

    def setA1(self, t):
        try:
            tmp= float(t/10)
            self.a1 = -tmp
        except:
            print("Wrong format of a1")

    def setB1(self, t):
        try:
            tmp= float(t)
            self.b1 = tmp
        except:
            print("Wrong format of b1")

    def setA2(self, t):
        try:
            tmp= float(t/10) 
            self.a2 = tmp
        except:
            print("Wrong format of a2")

    def setB2(self, t):
        try:
            tmp= float(t)
            self.b2 = tmp
        except:
            print("Wrong format of b2")

    def setA3(self, t):
        try:
            tmp= float(t/10)
            self.a3 = -tmp
        except:
            print("Wrong format of a3")

    def setB3(self, t):
        try:
            tmp= float(t)
            self.b3 = tmp
        except:
            print("Wrong format of b3")

    def setCid(self, capid):
        self.capid = int(capid) if capid.isdecimal() else capid # Try parse as a camera id if not assume it is a video
        self.capture()


class ConfWindow(QWidget):


    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))


    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.config = configparser.ConfigParser()
        # Create a checkbox
        self.piesi = QCheckBox('Piesi', self)
        self.samochod = QCheckBox('Samochód w pasie ruchu', self)
        self.rowerzysta = QCheckBox('Rowerzysta', self)


        # Create a model file path module
        self.modelPathLabel = QLabel(self)
        self.modelPathLabel.setText("Ścieżka pliku z modelem")
        self.modelPathEdit = QLineEdit(self)
        self.modelPathEdit.setPlaceholderText("File path")
        self.modelPathEdit.setReadOnly(True)
        self.modelSelectButton = QPushButton('Select File', self)
        self.modelSelectButton.clicked.connect(self.onSelectButtonClick)


        self.th = QThreadPreview()
        self.th.changePixmap.connect(self.setImage)

        # TODO: Zrobić to mądrzej
        # Lewa i prawa linia
        self.a1BBLabel = QLabel("Lewe ograniczenie (a):")
        self.a1BorderBox = QDial(self)
        self.a1BorderBox.setMinimum(-60)
        self.a1BorderBox.setMaximum(0)
        self.a1BorderBox.valueChanged.connect(self.th.setA1);
        self.b1BBLabel = QLabel("Lewe ograniczenie (b):")
        self.b1BorderBox = QSlider(Qt.Orientation.Horizontal)
        self.b1BorderBox.setMinimum(-100)
        self.b1BorderBox.setMaximum(640)
        self.b1BorderBox.valueChanged.connect(self.th.setB1);
        # Górna linia
        
        self.a2BBLabel = QLabel("Lewe ograniczenie (a):")
        self.a2BorderBox = QDial(self)
        self.a2BorderBox.setMinimum(-10)
        self.a2BorderBox.setMaximum(10)
        self.a2BorderBox.valueChanged.connect(self.th.setA2);
        self.b2BBLabel = QLabel("Lewe ograniczenie (b):")
        self.b2BorderBox = QSlider(Qt.Orientation.Horizontal)
        self.b2BorderBox.setMinimum(-100)
        self.b2BorderBox.setMaximum(640)
        self.b2BorderBox.valueChanged.connect(self.th.setB2);        
        
        # Prawa linia
        
        self.a3BBLabel = QLabel("Lewe ograniczenie (a):")
        self.a3BorderBox = QDial(self)
        self.a3BorderBox.setMinimum(0)
        self.a3BorderBox.setMaximum(60)
        self.a3BorderBox.valueChanged.connect(self.th.setA3);
        self.b3BBLabel = QLabel("Lewe ograniczenie (b):")
        self.b3BorderBox = QSlider(Qt.Orientation.Horizontal)
        self.b3BorderBox.setMinimum(-100)
        self.b3BorderBox.setMaximum(640)
        self.b3BorderBox.valueChanged.connect(self.th.setB3);        
        
        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)

        # Refresh button
        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.th.refresh)



        self.cameraIdLabel = QLabel("Camera ID:")
        self.cameraId = QLineEdit()
        self.cameraId.textChanged.connect(self.th.setCid);

        # Create a save button
        self.saveButton = QPushButton('Save', self)
        self.saveButton.clicked.connect(self.confwrite)

        self.confread()

        # Set Layout
        layout = QVBoxLayout()

        layout.addWidget(self.piesi)
        layout.addWidget(self.samochod)
        layout.addWidget(self.rowerzysta)
        layout.addWidget(self.modelPathLabel)
        layout.addWidget(self.modelPathEdit)
        layout.addWidget(self.modelSelectButton)

        layout.addWidget(self.a1BBLabel)
        layout.addWidget(self.a1BorderBox)
        layout.addWidget(self.b1BBLabel)
        layout.addWidget(self.b1BorderBox)

        layout.addWidget(self.a2BBLabel)
        layout.addWidget(self.a2BorderBox)
        layout.addWidget(self.b2BBLabel)
        layout.addWidget(self.b2BorderBox)


        layout.addWidget(self.a3BBLabel)
        layout.addWidget(self.a3BorderBox)
        layout.addWidget(self.b3BBLabel)
        layout.addWidget(self.b3BorderBox)

        layout.addWidget(self.label)

        layout.addWidget(self.refreshButton)

        layout.addWidget(self.cameraIdLabel)
        layout.addWidget(self.cameraId)
        layout.addWidget(self.saveButton)
        self.setLayout(layout)

        self.setWindowTitle('Konfigurator')
        self.th.start()
        self.show()

    #Choosing a file dialog
    def onSelectButtonClick(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Model", "", "Model (*.pt)")
        self.modelPathEdit.setText(filepath)

    #Write to config file
    def confwrite(self):
        self.config['Objects'] = {'piesi' : "True" if self.piesi.isChecked() else "False",
                             'samochod' : "True" if self.samochod.isChecked() else "False",
                             'rowerzysta' : "True" if self.rowerzysta.isChecked() else "False"}
        self.config['Model'] = {'path' : self.modelPathEdit.text()}
        self.config['Camera'] = {'id' : self.th.capid}

        self.config['DangerZone'] = {'a1' : self.th.a1,
                                     'b1' : self.th.b1,
                                     'a2' : self.th.a2,
                                     'b2' : self.th.b2,
                                     'a3' : self.th.a3,
                                     'b3' : self.th.b3}

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    #Read from config file (preset default)
    def confread(self):
        self.config.read('config.ini')
        try:
            self.piesi.setCheckState(
                Qt.CheckState.Checked if self.config['Objects']['piesi'] == "True" else Qt.CheckState.Unchecked)
            self.samochod.setCheckState(
                Qt.CheckState.Checked if self.config['Objects']['samochod'] == "True" else Qt.CheckState.Unchecked)
            self.rowerzysta.setCheckState(
                Qt.CheckState.Checked if self.config['Objects']['rowerzysta'] == "True" else Qt.CheckState.Unchecked)
            self.modelPathEdit.setText(self.config['Model']['path'])
            self.cameraId.setText(self.config['Camera']['id'])


            self.a1BorderBox.setValue(-int(10*float(self.config['DangerZone']['a1'])))
            self.b1BorderBox.setValue(int(self.config['DangerZone']['b1']))

            self.a2BorderBox.setValue(int(10*float(self.config['DangerZone']['a2'])))
            self.b2BorderBox.setValue(int(self.config['DangerZone']['b2']))

            self.a3BorderBox.setValue(-int(10*float(self.config['DangerZone']['a3'])))
            self.b3BorderBox.setValue(int(self.config['DangerZone']['b3']))

        except:
            print("Problems with reading config file, default not set")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfWindow()
    sys.exit(app.exec())
