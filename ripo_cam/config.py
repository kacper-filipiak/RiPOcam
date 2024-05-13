import configparser
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QCheckBox, QVBoxLayout, QLabel, QLineEdit, QFileDialog, \
    QSpinBox
from PyQt6.QtCore import Qt

class ConfWindow(QWidget):


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

        # TODO: Zrobić to mądrzej
        # Lewa i prawa linia
        self.leftBBLabel = QLabel("Lewa linia (px):")
        self.leftBorderBox = QSpinBox(self)
        self.leftBorderBox.setMaximum(5000)
        self.rightBBLabel = QLabel("Prawa linia (px):")
        self.rightBorderBox = QSpinBox(self)
        self.rightBorderBox.setMaximum(5000)

        self.cameraIdLabel = QLabel("Camera ID:")
        self.cameraId = QSpinBox(self)

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
        layout.addWidget(self.leftBBLabel)
        layout.addWidget(self.leftBorderBox)
        layout.addWidget(self.rightBBLabel)
        layout.addWidget(self.rightBorderBox)
        layout.addWidget(self.cameraIdLabel)
        layout.addWidget(self.cameraId)
        layout.addWidget(self.saveButton)
        self.setLayout(layout)

        self.setWindowTitle('Konfigurator')
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
        self.config['Zone'] = {'left' : self.leftBorderBox.text(),
                               'right' : self.rightBorderBox.text()}
        self.config['Camera'] = {'id' : self.cameraId.text()}

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
            self.leftBorderBox.setValue(int(self.config['Zone']['left']))
            self.rightBorderBox.setValue(int(self.config['Zone']['right']))
            self.cameraId.setValue(int(self.config['Camera']['id']))
        except:
            print("Problems with reading config file, default not set")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfWindow()
    sys.exit(app.exec())