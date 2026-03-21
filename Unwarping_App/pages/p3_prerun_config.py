from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit,QComboBox, QLabel, QVBoxLayout, QGridLayout, QFrame, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup, QScrollArea, QSizePolicy
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

        # PARAMETER INPUTS  -----------------------------------
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

        self.component_samplingParams.setFixedWidth(component_samplingMode.sizeHint().width())

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
        component_samplingMode.button_drag.clicked.connect(lambda: self.handleSamplingType("drag"))


    # Function to handle the sampling type
    def handleSamplingType(self, type=None, drag=False):
        params = self.component_samplingParams

        # Show all on default except step size
        params.row_1.show()
        params.label_X.show()
        params.input_X.show()
        
        params.row_2.show()
        params.row_3.show()
        params.row_4.show()
        params.row_5.show()
        params.row_6.hide()

        # Conductive mode
        if type == "conductive":
            # Hide sample height
            params.row_5.hide()
            
            # Show Z step size
            params.row_6.show()

        # Drag mode
        elif type == "drag":
            # Hide X resolution, show Y resolution ("step size")
            params.label_X.hide()
            params.input_X.hide()

            # Hide dwell and sample time
            # params.row_2.hide()
            # params.row_3.hide()

        # Constant Z mode
        else:
            pass   

        # Adjust height of scroll area
        params.scroll_area.setMaximumHeight(params.container.sizeHint().height())  

        self.sampling.mode = type
        self.photo.update()
        self.clearInputs()

        
    # Function to clear all sampling parameter inputs
    def clearInputs(self):
        params = self.component_samplingParams

        # Spatial res inputs
        params.input_X.clear()
        params.input_Y.clear()

        # Time inputs
        params.input_dwell.clear()
        params.input_sampleTime.clear()

        # Height inputs
        params.input_transit.clear()
        params.input_sampleHeight.clear()

        # Step size inputs
        params.input_ZstepSize.clear()


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
        self.button_drag = QRadioButton("Drag")

        mode_group = QButtonGroup()
        mode_group.addButton(self.button_constantZ, 0)
        mode_group.addButton(self.button_conductive, 1)
        mode_group.addButton(self.button_drag, 2)

        self.button_constantZ.setChecked(True)

        layout_container.addWidget(label_mode)
        layout_container.addWidget(self.button_constantZ)
        layout_container.addWidget(self.button_conductive)
        layout_container.addWidget(self.button_drag)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("background-color: #C8D3F1;")


class SamplingParameters(QWidget):
    def __init__(self, photo, sampling_item):
        super().__init__()
        
        layout = QVBoxLayout(self)

        self.container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(self.container)


        label_samplingParameters = QLabel("Parameters: ", objectName="larger")
        label_samplingParameters.setStyleSheet("font-weight: bold;")

        # ROW 1 ----------------------------------------
        self.row_1 = QWidget()
        layout_row_1 = QHBoxLayout(self.row_1)

        selections = QComboBox()
        selections.addItem("Sampling spots (#)")
        selections.addItem("Resolution (mm)")

        self.label_X = QLabel("X: ")

        self.input_X = QLineEdit()
        self.input_X.setValidator(QDoubleValidator(0, 150, 2)) # Set limit 
        self.input_X.setMaxLength(3)

        self.label_Y = QLabel("Y: ")

        self.input_Y = QLineEdit()
        self.input_Y.setValidator(QDoubleValidator(0, 150, 2)) # Set limit
        self.input_Y.setMaxLength(3)

        layout_row_1.addWidget(selections, alignment=Qt.AlignLeft)

        layout_row_1.addWidget(self.label_X, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(self.input_X, alignment=Qt.AlignRight)

        layout_row_1.addWidget(self.label_Y, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(self.input_Y, alignment=Qt.AlignLeft)
        layout_row_1.setContentsMargins(0, 5, 0,0)


        # ROW 2 ----------------------------------------
        self.row_2 = QWidget()
        layout_row_2 = QHBoxLayout(self.row_2)

        label_dwell = QLabel("Dwell time (s): ")
        self.input_dwell = QLineEdit()
        self.input_dwell.setValidator(QDoubleValidator(0, 250, 2))
        self.input_dwell.setMaxLength(3)

        layout_row_2.addWidget(label_dwell, alignment=Qt.AlignLeft)
        layout_row_2.addWidget(self.input_dwell, alignment=Qt.AlignRight)
        layout_row_2.setContentsMargins(0, 5, 0, 0)


        # ROW 3 ----------------------------------------
        self.row_3 = QWidget()
        layout_row_3 = QHBoxLayout(self.row_3)

        label_sampleTime = QLabel("Sample time (s): ")
        self.input_sampleTime = QLineEdit()
        self.input_sampleTime.setValidator(QDoubleValidator(0, 250, 2))
        self.input_sampleTime.setMaxLength(3)

        layout_row_3.addWidget(label_sampleTime, alignment=Qt.AlignLeft)
        layout_row_3.addWidget(self.input_sampleTime, alignment=Qt.AlignRight)
        layout_row_3.setContentsMargins(0, 5, 0, 0)


        # ROW 4 ----------------------------------------
        self.row_4 = QWidget()
        layout_row_4 = QHBoxLayout(self.row_4)

        label_transit = QLabel("Transit height (mm): ")
        self.input_transit = QLineEdit()
        self.input_transit.setValidator(QDoubleValidator(-180, 180, 2))
        self.input_transit.setMaxLength(4)

        layout_row_4.addWidget(label_transit, alignment=Qt.AlignLeft)
        layout_row_4.addWidget(self.input_transit, alignment=Qt.AlignRight)
        layout_row_4.setContentsMargins(0, 5, 0, 0)


        # ROW 5 ----------------------------------------
        self.row_5 = QWidget()
        layout_row_5 = QHBoxLayout(self.row_5)

        label_sampleHeight = QLabel("Sample height (mm): ")
        self.input_sampleHeight = QLineEdit()
        self.input_sampleHeight.setValidator(QDoubleValidator(-180, 180, 2))
        self.input_sampleHeight.setMaxLength(4)

        layout_row_5.addWidget(label_sampleHeight, alignment=Qt.AlignLeft)
        layout_row_5.addWidget(self.input_sampleHeight, alignment=Qt.AlignRight)
        layout_row_5.setContentsMargins(0, 5, 0, 0)

        # ROW 6 ----------------------------------------
        self.row_6 = QWidget()
        layout_row_6 = QHBoxLayout(self.row_6)

        label_ZstepSize = QLabel("Z Step Size (mm): ")
        self.input_ZstepSize = QLineEdit()
        self.input_ZstepSize.setValidator(QDoubleValidator(0, 5, 3))
        self.input_ZstepSize.setMaxLength(5)

        layout_row_6.addWidget(label_ZstepSize, alignment=Qt.AlignLeft)
        layout_row_6.addWidget(self.input_ZstepSize, alignment=Qt.AlignRight)
        layout_row_6.setContentsMargins(0, 5, 0, 0)

        self.row_6.hide()
        

        # ROW 7 ----------------------------------------
        # self.row_7 = QWidget()
        # layout_row_7 = QHBoxLayout(self.row_7)

        # label_YstepSize = QLabel("Y Step Size (mm): ")
        # self.input_YstepSize = QLineEdit()

        # layout_row_7.addWidget(label_YstepSize, alignment=Qt.AlignLeft)
        # layout_row_7.addWidget(self.input_YstepSize, alignment=Qt.AlignRight)
        # layout_row_7.setContentsMargins(0, 5, 0, 0)

        # self.row_7.hide()




        # COMPOSE ----------------------------------------
        layout_container.addWidget(label_samplingParameters)
        layout_container.addWidget(self.row_1)
        layout_container.addWidget(self.row_2)
        layout_container.addWidget(self.row_3)
        layout_container.addWidget(self.row_4)
        layout_container.addWidget(self.row_5)
        layout_container.addWidget(self.row_6)
        # layout_container.addWidget(self.row_7)

        self.container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Allow for scrolling if needed on the user's monitor size
        self.scroll_area = QScrollArea(objectName="light_blue_box")
        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame) 

        self.scroll_area.setViewportMargins(0, 0, 0, 0)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.scroll_area)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  


        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit, QComboBox { background-color: white; }
        """)

        # FUNCTIONS ----------------------------------------
        
        # Resolution / Sampling spots
        self.input_X.textChanged.connect(lambda: self.limitValue(self.input_X, "space"))
        self.input_Y.textChanged.connect(lambda: self.limitValue(self.input_Y, "space"))

        self.input_X.textChanged.connect(lambda: self.overlayHandle(photo, sampling_item, self.input_X.text(), self.input_Y.text(), selections.currentIndex()))
        self.input_Y.textChanged.connect(lambda: self.overlayHandle(photo, sampling_item, self.input_X.text(), self.input_Y.text(), selections.currentIndex()))
        selections.currentIndexChanged.connect(lambda: self.overlayHandle(photo, sampling_item, self.input_X.text(), self.input_Y.text(), selections.currentIndex()))


        # Time
        self.input_dwell.textChanged.connect(lambda: self.limitValue(self.input_dwell, "time"))
        self.input_dwell.textChanged.connect(lambda: self.setVars(sampling_item, self.input_dwell.text(), "dwell_time"))
        
        self.input_sampleTime.textChanged.connect(lambda: self.limitValue(self.input_sampleTime, "time"))
        self.input_sampleTime.textChanged.connect(lambda: self.setVars(sampling_item, self.input_sampleTime.text(), "sample_time"))
        

        # Height
        self.input_transit.textChanged.connect(lambda: self.limitValue(self.input_transit, "height"))
        self.input_transit.textChanged.connect(lambda: self.setVars(sampling_item, self.input_transit.text(), "transit_height"))
        
        self.input_sampleHeight.textChanged.connect(lambda: self.limitValue(self.input_sampleHeight, "height"))
        self.input_sampleHeight.textChanged.connect(lambda: self.setVars(sampling_item, self.input_sampleHeight.text(), "sample_height"))


        # Step Size
        self.input_ZstepSize.textChanged.connect(lambda: self.limitValue(self.input_ZstepSize, "ZStep"))
        self.input_ZstepSize.textChanged.connect(lambda: self.setVars(sampling_item, self.input_ZstepSize.text(), "Zstep_size"))
        

    
    # Function to limit the input value of the parameters, for safety
    def limitValue(self, input, type):
        if not input.text():
            return
    
        try:
            value = float(input.text())
            # Enforce spatial limit
            if type == "space" and value > 150:
                input.setText("150")
            
            # Enfore time limit
            elif type == "time" and value > 250:
                input.setText("250")

            # Enforce height limit
            elif type == "height":
                if value < -180:
                    input.setText("-180")
                elif value > 180:
                    input.setText("180")

            # Enforce Z step limit
            elif type == "ZStep" and value > 5:
                input.setText("5")
                

        except ValueError:
            pass
        



    # Function to update the grid overlay
    def overlayHandle(self, photo, sampling, x, y, type):

        if sampling.mode == "drag":
            photo.rowsOnly = True
            photo.updateOverlayRows(y, type, sampling)

        else:
            photo.rowsOnly = False
            photo.updateOverlay(x, y, type, sampling)




    # Function to set the sampling variables
    def setVars(self, sampling, val, type):
        i = float(val)

        # Time
        if type == "dwell_time":
            sampling.dwellTime = i

        elif type == "sample_time":
            sampling.sampleTime = i

        # Height
        elif type == "transit_height":
            sampling.transitHeight = i

        elif type == "sample_height":
            sampling.sampleHeight = i

        # Step size:
        elif type == "Zstep_size":
            sampling.stepSize = i
    
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
        self.input_XYSpeed.setValidator(QIntValidator(0, 1000))
        self.input_XYSpeed.setMaxLength(4)
        self.input_XYSpeed.setText("500")

        layout_row_1.addWidget(label_XYSpeed, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(self.input_XYSpeed, alignment=Qt.AlignRight)
        layout_row_1.setContentsMargins(0, 5, 0, 0)


        # ROW 2 ----------------------------------------
        self.row_2 = QWidget()
        layout_row_2 = QHBoxLayout(self.row_2)

        label_ZUpSpeed = QLabel("Z Up Speed: ")
        self.input_ZUpSpeed = QLineEdit()
        self.input_ZUpSpeed.setValidator(QIntValidator(0, 1000))
        self.input_ZUpSpeed.setMaxLength(4)
        self.input_ZUpSpeed.setText("500")

        layout_row_2.addWidget(label_ZUpSpeed, alignment=Qt.AlignLeft)
        layout_row_2.addWidget(self.input_ZUpSpeed, alignment=Qt.AlignRight)
        layout_row_2.setContentsMargins(0, 5, 0, 0)

        # ROW 3 ----------------------------------------
        self.row_3 = QWidget()
        layout_row_3 = QHBoxLayout(self.row_3)

        label_ZDownSpeed = QLabel("Z Down Speed: ")
        self.input_ZDownSpeed = QLineEdit()
        self.input_ZDownSpeed.setValidator(QIntValidator(0, 1000))
        self.input_ZDownSpeed.setMaxLength(4)
        self.input_ZDownSpeed.setText("100")

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

        # FUNCTIONS ---------------------------------------
        # Speed
        self.input_XYSpeed.textChanged.connect(lambda: self.limitSpeed(self.input_XYSpeed))
        self.input_ZUpSpeed.textChanged.connect(lambda: self.limitSpeed(self.input_ZUpSpeed))
        self.input_ZDownSpeed.textChanged.connect(lambda: self.limitSpeed(self.input_ZDownSpeed))

        self.input_XYSpeed.textChanged.connect(lambda: self.setSpeed(sampling_item, self.input_XYSpeed.text(), "XY"))
        self.input_ZUpSpeed.textChanged.connect(lambda: self.setSpeed(sampling_item, self.input_ZUpSpeed.text(), "ZUp"))
        self.input_ZDownSpeed.textChanged.connect(lambda: self.setSpeed(sampling_item, self.input_ZDownSpeed.text(), "ZDown"))


        # Value initialization
        sampling_item.xy_speed = float(self.input_XYSpeed.text())
        sampling_item.z_up_speed = float(self.input_ZUpSpeed.text())
        sampling_item.z_down_speed = float(self.input_ZDownSpeed.text())


    # Function to set the speed of the printer 
    def setSpeed(self, sampling, val, type):
        # Speed changes
        if type == "XY":
            sampling.xy_speed = float(val)

        elif type == "ZUp":
            sampling.z_up_speed = float(val)

        elif type == "ZDown":
            sampling.z_down_speed = float(val)
    
        else:
            pass

    # Function to limit the input speed 
    def limitSpeed(self, input):
        if not input.text():
            return
    
        try:
            value = float(input.text())
            if value > 1000:
                input.setText("1000")

            elif value < 0:
                input.setText("0")

        except ValueError:
            pass