from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QIntValidator, QDoubleValidator
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect

import cv2

from Unwarping_App.components.common import ClickableImage
from Unwarping_App.services import sampling_service

class PrerunConfig(QWidget):
    next = pyqtSignal()

    def __init__(self, sampling):
        super().__init__()

        self.sampling = sampling

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

        # PARAMETER INPUTS  ------------------------------------
        self.component_samplingParams = SamplingParameters(self.photo, self.sampling)
        
        # SPEED INPUTS ----------------------------------------
        self.component_speed = SamplingSpeeds(self.sampling)

        button_startRun = QPushButton("Start sampling run", objectName="blue")
        

        # RIGHT COLUMN ----------------------------------------
        layout_right.addStretch()
        layout_right.addWidget(label_prerun, alignment=Qt.AlignLeft)
        layout_right.addWidget(component_samplingMode)
        layout_right.addWidget(self.component_samplingParams)
        layout_right.addWidget(self.component_speed)
        layout_right.addStretch()
        layout_right.addWidget(button_startRun)
        layout_right.addStretch()

        layout_right.setContentsMargins(0,0,0,0)
        layout_right.setSpacing(10)

        self.component_samplingParams.setFixedWidth(component_samplingMode.sizeHint().width() + 10)

        # COMPOSE ----------------------------------------
        layout.addWidget(self.photo)
        layout.addWidget(right, alignment=Qt.AlignCenter)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)   


        # FUNCTIONS ----------------------------------------
        button_startRun.clicked.connect(self.next.emit)
        button_startRun.clicked.connect(lambda: sampling_service.getSampling(self.sampling))
        button_startRun.clicked.connect(lambda: sampling_service.createCSV())

        component_samplingMode.button_constantZ.clicked.connect(lambda: self.handleSamplingType("constant"))
        component_samplingMode.button_conductive.clicked.connect(lambda: self.handleSamplingType("conductive"))

        self.component_samplingParams.button_dragSampling.clicked.connect(lambda: self.handleSamplingType("drag"))


    # Function to handle the sampling type
    def handleSamplingType(self, type=None, drag=False):
        params = self.component_samplingParams

        # Show all on default
        params.row_1.show()
        params.row_2.show()
        params.row_3.show()
        params.row_4.show()
        params.row_5.show()
        params.row_6.show()
        params.row_7.show()

        # Constant Z
        if type == "constant" or type == "drag":
            # If drag sampling toggled, hide spatial res and dwell time
            if params.button_dragSampling.isChecked():
                params.row_1.hide()
                params.row_2.hide()
                params.row_3.hide() 

                # Reset hidden rows
                params.input_spatialRes_X.clear()
                params.input_spatialRes_Y.clear()
                params.input_dwell.clear()
                params.input_sampleTime.clear()         

        # Conductive
        elif type == "conductive":
            params.row_5.hide()
            params.row_6.hide()

            # Reset all inputs if drag sampling button is checked (makes it slightly nicer to look at on change)
            if params.button_dragSampling.isChecked():
                self.clearInputs()

            # Reset hidden rows
            params.input_sampleHeight.clear()
            params.button_dragSampling.setChecked(False)

        self.sampling.mode = type
        self.photo.update()

        
    # Function to clear all sampling parameter inputs
    def clearInputs(self):
        params = self.component_samplingParams

        # Spatial res inputs
        params.input_spatialRes_X.clear()
        params.input_spatialRes_Y.clear()

        # Time inputs
        params.input_dwell.clear()
        params.input_sampleTime.clear()

        # Height inputs
        params.input_transit.clear()
        params.input_sampleHeight.clear()


class ModeSelection(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QHBoxLayout(container)

        label_mode = QLabel("Mode: ", objectName="larger")
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
    def __init__(self, photo, sampling_item):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)


        label_samplingParameters = QLabel("Parameters: ", objectName="larger")
        label_samplingParameters.setStyleSheet("font-weight: bold;")

        # ROW 1 ----------------------------------------
        self.row_1 = QWidget()
        layout_row_1 = QHBoxLayout(self.row_1)

        label_spatialRes = QLabel("Resolution (mm) ")

        label_spatialRes_X = QLabel("X: ")

        self.input_spatialRes_X = QLineEdit()
        self.input_spatialRes_X.setValidator(QDoubleValidator())

        label_spatialRes_Y = QLabel("Y: ")

        self.input_spatialRes_Y = QLineEdit()
        self.input_spatialRes_Y.setValidator(QDoubleValidator())

        layout_row_1.addWidget(label_spatialRes, alignment=Qt.AlignLeft)

        layout_row_1.addWidget(label_spatialRes_X, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(self.input_spatialRes_X, alignment=Qt.AlignRight)

        layout_row_1.addWidget(label_spatialRes_Y, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(self.input_spatialRes_Y, alignment=Qt.AlignLeft)
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

        label_sampleTime = QLabel("Sample time (s): ")
        self.input_sampleTime = QLineEdit()

        layout_row_3.addWidget(label_sampleTime, alignment=Qt.AlignLeft)
        layout_row_3.addWidget(self.input_sampleTime, alignment=Qt.AlignRight)
        layout_row_3.setContentsMargins(0, 5, 0, 0)


        # ROW 4 ----------------------------------------
        self.row_4 = QWidget()
        layout_row_4 = QHBoxLayout(self.row_4)

        label_transit = QLabel("Transit height (mm): ")
        self.input_transit = QLineEdit()

        layout_row_4.addWidget(label_transit, alignment=Qt.AlignLeft)
        layout_row_4.addWidget(self.input_transit, alignment=Qt.AlignRight)
        layout_row_4.setContentsMargins(0, 5, 0, 0)


        # ROW 5 ----------------------------------------
        self.row_5 = QWidget()
        layout_row_5 = QHBoxLayout(self.row_5)

        label_sampleHeight = QLabel("Sample height (mm): ")
        self.input_sampleHeight = QLineEdit()

        layout_row_5.addWidget(label_sampleHeight, alignment=Qt.AlignLeft)
        layout_row_5.addWidget(self.input_sampleHeight, alignment=Qt.AlignRight)
        layout_row_5.setContentsMargins(0, 5, 0, 0)

        # ROW 6 ----------------------------------------
        self.row_6 = QWidget()
        layout_row_6 = QHBoxLayout(self.row_6)

        self.button_dragSampling = QRadioButton("Drag sampling")

        layout_row_6.addWidget(self.button_dragSampling, alignment=Qt.AlignLeft)
        layout_row_6.setContentsMargins(0, 5, 0, 0)
        

        # ROW 7 ----------------------------------------
        self.row_7 = QWidget()
        layout_row_7 = QHBoxLayout(self.row_7)

        more_options = QLabel("More options available in \"Legacy\" mode.")
        more_options.setWordWrap(True)
        more_options.setStyleSheet("font-weight: bold;")

        layout_row_7.addWidget(more_options)
        layout_row_7.setContentsMargins(0, 10, 0, 0)


        # COMPOSE ----------------------------------------
        layout_container.addWidget(label_samplingParameters)
        layout_container.addWidget(self.row_1)
        layout_container.addWidget(self.row_2)
        layout_container.addWidget(self.row_3)
        layout_container.addWidget(self.row_4)
        layout_container.addWidget(self.row_5)
        layout_container.addWidget(self.row_6)
        layout_container.addStretch()
        # layout_container.addWidget(self.row_7)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit { background-color: white; }
        """)

        # FUNCTIONS ----------------------------------------
        # Resolution (X and Y)
        self.input_spatialRes_X.textChanged.connect(lambda: photo.updateOverlay(self.input_spatialRes_X.text(), self.input_spatialRes_Y.text()))
        self.input_spatialRes_Y.textChanged.connect(lambda: photo.updateOverlay(self.input_spatialRes_X.text(), self.input_spatialRes_Y.text()))

        self.input_spatialRes_X.textChanged.connect(lambda: self.setVars(sampling_item, self.input_spatialRes_X.text(), "res_X"))
        self.input_spatialRes_Y.textChanged.connect(lambda: self.setVars(sampling_item, self.input_spatialRes_Y.text(), "res_Y"))

        # Time
        self.input_dwell.textChanged.connect(lambda: self.setVars(sampling_item, self.input_dwell.text(), "dwell_time"))
        self.input_sampleTime.textChanged.connect(lambda: self.setVars(sampling_item, self.input_sampleTime.text(), "sample_time"))

        # Height
        self.input_transit.textChanged.connect(lambda: self.setVars(sampling_item, self.input_transit.text(), "transit_height"))
        self.input_sampleHeight.textChanged.connect(lambda: self.setVars(sampling_item, self.input_sampleHeight.text(), "sample_height"))


    def setVars(self, sampling, val, type):
        # Resolution
        if type == "res_X":
            sampling.spatialRes_X = float(val)

        elif type == "res_Y":
            sampling.spatialRes_Y = float(val)

        # Time
        elif type == "dwell_time":
            sampling.dwellTime = float(val)

        elif type == "sample_time":
            sampling.sampleTime = float(val)

        # Height
        elif type == "transit_height":
            sampling.transitHeight = float(val)

        elif type == "sample_height":
            sampling.sampleHeight = float(val)
    
        else:
            pass


class SamplingSpeeds(QWidget):
    def __init__(self, sampling_item):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)

        label_speed = QLabel("Speed (mm/min): ", objectName="larger")
        label_speed.setStyleSheet("font-weight: bold;")


        # ROW 1 ----------------------------------------
        self.row_1 = QWidget()
        layout_row_1 = QHBoxLayout(self.row_1)

        label_XYSpeed = QLabel("XY Speed: ")
        self.input_XYSpeed = QLineEdit()
        self.input_XYSpeed.setValidator(QDoubleValidator())
        self.input_XYSpeed.setText("5000")

        layout_row_1.addWidget(label_XYSpeed, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(self.input_XYSpeed, alignment=Qt.AlignRight)
        layout_row_1.setContentsMargins(0, 5, 0, 0)


        # ROW 2 ----------------------------------------
        self.row_2 = QWidget()
        layout_row_2 = QHBoxLayout(self.row_2)

        label_ZUpSpeed = QLabel("Z Up Speed: ")
        self.input_ZUpSpeed = QLineEdit()
        self.input_ZUpSpeed.setValidator(QDoubleValidator())
        self.input_ZUpSpeed.setText("725")

        layout_row_2.addWidget(label_ZUpSpeed, alignment=Qt.AlignLeft)
        layout_row_2.addWidget(self.input_ZUpSpeed, alignment=Qt.AlignRight)
        layout_row_2.setContentsMargins(0, 5, 0, 0)

        # ROW 3 ----------------------------------------
        self.row_3 = QWidget()
        layout_row_3 = QHBoxLayout(self.row_3)

        label_ZDownSpeed = QLabel("Z Down Speed: ")
        self.input_ZDownSpeed = QLineEdit()
        self.input_ZDownSpeed.setValidator(QDoubleValidator())
        self.input_ZDownSpeed.setText("50")

        layout_row_3.addWidget(label_ZDownSpeed, alignment=Qt.AlignLeft)
        layout_row_3.addWidget(self.input_ZDownSpeed, alignment=Qt.AlignRight)
        layout_row_3.setContentsMargins(0, 5, 0, 0)

        # COMPOSE ----------------------------------------
        layout_container.addWidget(label_speed)
        layout_container.addWidget(self.row_1)
        layout_container.addWidget(self.row_2)
        layout_container.addWidget(self.row_3)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit { background-color: white; }
        """)