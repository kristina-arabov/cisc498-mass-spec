from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QSlider, QComboBox, QFrame, QApplication, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect

from Unwarping_App.components.utils import processUpload, addAllWidgets, calculateOffset, generateTransformationFolder
from Unwarping_App.components.common import NewTransformationItem, CamFeed

from Unwarping_App.services import calibration_service

class TransformationReview(QWidget):
    def __init__(self, transformation):
        super().__init__()
        
        self.transformation = transformation

        self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label_review = QLabel("Review Transformation", objectName="page_title")
        label_estimate = QLabel("Estimated probe-to-camera offset:")
        self.label_offset = QLabel("Unavailable due to incorrect or missing data.")

        # component_unwarpResult = CamFeed()

        button_save = QPushButton("Save transformation", objectName="headerBlue")

        layout.addStretch()
        layout.addWidget(label_review, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(label_estimate, alignment=Qt.AlignCenter)
        layout.addWidget(self.label_offset, alignment=Qt.AlignCenter)
        layout.addStretch()
        # layout.addWidget(component_unwarpResult, alignment=Qt.AlignCenter)
        layout.addWidget(button_save, alignment=Qt.AlignCenter)
        layout.addStretch()

        ''' FUNCTIONS '''
        button_save.clicked.connect(lambda: calibration_service.createTransformationFile(self.transformation))


    def calculateOffset(self):
        msg = calibration_service.calculateOffset(self.transformation)
        self.label_offset.setText(msg)

    # Function to reset front-end
    def clearAll(self):
        self.label_offset.setText("Unavailable due to incorrect or missing data.")