from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QMovie
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect, QSize

import cv2

from Unwarping_App.components.common import CamFeed, ClickableImage,InputField
from Unwarping_App.components.utils import generateProbeAcquisition, updatePixelOverlay, sendLocations

class SamplingProgress(QWidget):
    next = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
    # def __init__(self, printer, json_path):
    #     super().__init__()
    #     self.printer = printer
    #     self.json_path = json_path
    #     self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)
        gif = QMovie("Unwarping_App\components\images\Loading.gif")

        self.photo = ClickableImage()

        right = QWidget()
        layout_right = QVBoxLayout(right)

        img_loadingCircle = QLabel()
        img_loadingCircle.setMovie(gif)
        gif.start()
        gif.setScaledSize(QSize(100, 100))

        label_points = QLabel("___ points sampled")
        label_estimatedTime = QLabel("Estimated time left: ___")

        button_stop = QPushButton("Stop", objectName="red")

        button_temp = QPushButton("Temporary next button", objectName="headerBlue")
        button_temp.clicked.connect(self.next.emit)

        layout_right.addStretch()
        layout_right.addWidget(img_loadingCircle, alignment=Qt.AlignCenter)
        layout_right.addStretch()
        layout_right.addWidget(label_points, alignment=Qt.AlignCenter)
        layout_right.addWidget(label_estimatedTime,alignment=Qt.AlignCenter)
        layout_right.addStretch()
        layout_right.addWidget(button_stop, alignment=Qt.AlignCenter)
        layout_right.addWidget(button_temp, alignment=Qt.AlignCenter)
        layout_right.addStretch()


        layout.addWidget(self.photo)
        layout.addWidget(right)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        