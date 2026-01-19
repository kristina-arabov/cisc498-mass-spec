from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect

import cv2

from Unwarping_App.components.common import CamFeed, ClickableImage,InputField
from Unwarping_App.components.utils import generateProbeAcquisition, updatePixelOverlay, sendLocations

class SamplingComplete(QWidget):
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

        
        layout = QVBoxLayout(self)

        label_finished = QLabel("Sampling run finished", objectName="page_title")

        button_align = QPushButton("Align timestamps now", objectName="blue")
        button_align.setEnabled(False)
        label_align = QLabel("Abundance-time file from MS computer required")

        button_save = QPushButton("Save timestamp file for later", objectName="headerBlue")

        layout.addStretch()
        layout.addWidget(label_finished, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(button_align, alignment=Qt.AlignCenter)
        layout.addWidget(label_align, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(button_save, alignment=Qt.AlignCenter)
        layout.addStretch()
