from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QIntValidator, QDoubleValidator
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect

import cv2

from Unwarping_App.components.common import CamFeed, ClickableImage,InputField
from Unwarping_App.components.utils import generateProbeAcquisition, updatePixelOverlay, sendLocations

class PrerunConfig(QWidget):
    next = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())


        layout = QHBoxLayout(self)
        self.photo = ClickableImage()

        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_prerun = QLabel("Pre-run Config", objectName="page_title")

        # SAMPLING MODE SELECTION -----------------------------
        component_samplingMode = ModeSelection()

        # PARAMETER INPUTS  -----------------------------------
        self.component_samplingParams = SamplingParameters(self.photo)

        button_startRun = QPushButton("Start sampling run", objectName="blue")
        button_startRun.clicked.connect(self.next.emit)

        # RIGHT COLUMN ----------------------------------------
        layout_right.addStretch()
        layout_right.addWidget(label_prerun, alignment=Qt.AlignLeft)
        layout_right.addWidget(component_samplingMode)
        layout_right.addWidget(self.component_samplingParams)
        layout_right.addStretch()
        layout_right.addWidget(button_startRun)
        layout_right.addStretch()

        layout_right.setContentsMargins(0,0,0,0)
        layout_right.setSpacing(15)

        self.component_samplingParams.setFixedWidth(component_samplingMode.sizeHint().width() + 10)

        # COMPOSE ----------------------------------------
        layout.addWidget(self.photo)
        layout.addWidget(right, alignment=Qt.AlignCenter)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)   


        # FUNCTIONS ----------------------------------------
        component_samplingMode.button_constantZ.clicked.connect(lambda: self.handleSamplingType("constant"))
        component_samplingMode.button_conductive.clicked.connect(lambda: self.handleSamplingType("conductive"))

        self.component_samplingParams.button_dragSampling.clicked.connect(lambda: self.handleSamplingType("constant"))


    # Function to handle the sampling type
    def handleSamplingType(self, type=None, drag=False):
        # Show all on default
        self.component_samplingParams.row_1.show()
        self.component_samplingParams.row_2.show()
        self.component_samplingParams.row_3.show()
        self.component_samplingParams.row_4.show()

        # Constant Z
        if type == "constant":
            # If drag sampling toggled, hide spatial res and dwell time
            if self.component_samplingParams.button_dragSampling.isChecked():
                self.component_samplingParams.row_1.hide()
                self.component_samplingParams.row_2.hide()

        # Conductive
        elif type == "conductive":
            self.component_samplingParams.row_3.hide()
            self.component_samplingParams.row_4.hide()

    def clearInputs(self):
        self.component_samplingParams.input_spatialRes.clear()
        self.component_samplingParams.input_dwell.clear()
        self.component_samplingParams.input_transfer.clear()


class ModeSelection(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QHBoxLayout(container)

        label_mode = QLabel("Sampling mode: ", objectName="larger")
        label_mode.setStyleSheet("font-weight: bold;")

        self.button_constantZ = QRadioButton("Constant-Z")
        self.button_conductive = QRadioButton("Conductive")

        mode_group = QButtonGroup()
        mode_group.addButton(self.button_constantZ, 0)
        mode_group.addButton(self.button_conductive, 1)

        self.button_constantZ.setChecked(True)

        layout_container.addWidget(label_mode)
        layout_container.addWidget(self.button_constantZ)
        layout_container.addWidget(self.button_conductive)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("background-color: #C8D3F1;")


class SamplingParameters(QWidget):
    def __init__(self, photo):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)


        label_samplingParameters = QLabel("Sampling parameters: ", objectName="larger")
        label_samplingParameters.setStyleSheet("font-weight: bold;")

        # ROW 1 ----------------------------------------
        self.row_1 = QWidget()
        layout_row_1 = QHBoxLayout(self.row_1)

        label_spatialRes = QLabel("Spatial resolution (mm): ")

        self.input_spatialRes = QLineEdit()
        self.input_spatialRes.setValidator(QDoubleValidator())

        layout_row_1.addWidget(label_spatialRes, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(self.input_spatialRes, alignment=Qt.AlignRight)  
        layout_row_1.setContentsMargins(0, 5, 0,0)


        # ROW 2 ----------------------------------------
        self.row_2 = QWidget()
        layout_row_2 = QHBoxLayout(self.row_2)

        label_dwell = QLabel("Dwell time (s): ")
        
        self.input_dwell = QLineEdit()

        layout_row_2.addWidget(label_dwell, alignment=Qt.AlignLeft)
        layout_row_2.addWidget(self.input_dwell, alignment=Qt.AlignRight)
        layout_row_2.setContentsMargins(0, 5, 0, 0)


        # ROW 3 ----------------------------------------
        self.row_3 = QWidget()
        layout_row_3 = QHBoxLayout(self.row_3)

        label_transfer = QLabel("Transfer height (mm): ")
        
        self.input_transfer = QLineEdit()

        layout_row_3.addWidget(label_transfer, alignment=Qt.AlignLeft)
        layout_row_3.addWidget(self.input_transfer, alignment=Qt.AlignRight)
        layout_row_3.setContentsMargins(0, 5, 0, 0)


        # ROW 4 ----------------------------------------
        self.row_4 = QWidget()
        layout_row_4 = QHBoxLayout(self.row_4)

        self.button_dragSampling = QRadioButton("Drag sampling")

        layout_row_4.addWidget(self.button_dragSampling, alignment=Qt.AlignLeft)
        layout_row_4.setContentsMargins(0, 5, 0, 0)


        # ROW 5 ----------------------------------------
        self.row_5 = QWidget()
        layout_row_5 = QHBoxLayout(self.row_5)

        more_options = QLabel("More sampling options available in \"Legacy\" mode.")
        more_options.setWordWrap(True)
        more_options.setStyleSheet("font-weight: bold;")

        layout_row_5.addWidget(more_options)
        layout_row_5.setContentsMargins(0, 15, 0, 0)


        # COMPOSE ----------------------------------------
        layout_container.addWidget(label_samplingParameters)
        layout_container.addWidget(self.row_1)
        layout_container.addWidget(self.row_2)
        layout_container.addWidget(self.row_3)
        layout_container.addWidget(self.row_4)
        layout_container.addStretch()
        layout_container.addWidget(self.row_5)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit { background-color: white; }
        """)

        # FUNCTIONS ----------------------------------------
        self.input_spatialRes.textChanged.connect(lambda: photo.updateOverlay(self.input_spatialRes.text()))

