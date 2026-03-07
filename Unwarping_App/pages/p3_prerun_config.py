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
        self.photo = ClickableImage()

        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_prerun = QLabel("Pre-run Config", objectName="page_title")
        # TODO logo?

        ''' SAMPLING MODE SELECTION '''
        component_samplingMode = ModeSelection()

        ''' PARAMETER INPUTS '''
        self.component_samplingParams = SamplingParameters(self.photo)

        button_startRun = QPushButton("Start sampling run", objectName="blue")
        button_startRun.clicked.connect(self.next.emit)

        ''' ASSEMBLE RIGHT COLUMN '''
        layout_right.addStretch()
        layout_right.addWidget(label_prerun, alignment=Qt.AlignLeft)
        layout_right.addWidget(component_samplingMode, alignment=Qt.AlignLeft)
        layout_right.addWidget(self.component_samplingParams, alignment=Qt.AlignLeft)
        layout_right.addStretch()
        layout_right.addWidget(button_startRun, alignment=Qt.AlignLeft)
        layout_right.addStretch()

        ''' COMPOSE ALL '''
        layout.addWidget(self.photo)
        layout.addWidget(right)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)   

        ''' FUNCTIONS '''   
        component_samplingMode.button_constantZ.clicked.connect(lambda: self.handleSamplingType("constant"))
        component_samplingMode.button_conductive.clicked.connect(lambda: self.handleSamplingType("conductive"))

        self.component_samplingParams.button_dragSampling.clicked.connect(lambda: self.handleSamplingType("constant"))


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

        ''' ROW 1 '''
        self.row_1 = QWidget()
        layout_row_1 = QHBoxLayout(self.row_1)

        label_spatialRes = QLabel("Spatial resolution (mm): ")
        self.input_spatialRes = QLineEdit()
        self.input_spatialRes.setValidator(QDoubleValidator())

        layout_row_1.addWidget(label_spatialRes)
        layout_row_1.addWidget(self.input_spatialRes)   


        ''' ROW 2 '''
        self.row_2 = QWidget()
        layout_row_2 = QHBoxLayout(self.row_2)

        label_dwell = QLabel("Dwell time (s): ")
        self.input_dwell = QLineEdit()

        layout_row_2.addWidget(label_dwell)
        layout_row_2.addWidget(self.input_dwell)


        ''' ROW 3 '''
        self.row_3 = QWidget()
        layout_row_3 = QHBoxLayout(self.row_3)

        label_transfer = QLabel("Transfer height (mm): ")
        self.input_transfer = QLineEdit()

        layout_row_3.addWidget(label_transfer)
        layout_row_3.addWidget(self.input_transfer)

        ''' ROW 4 '''
        self.row_4 = QWidget()
        layout_row_4 = QHBoxLayout(self.row_4)

        self.button_dragSampling = QRadioButton("Drag sampling")

        layout_row_4.addWidget(self.button_dragSampling)


        ''' ROW 5 '''
        self.row_5 = QWidget()
        layout_row_5 = QHBoxLayout(self.row_5)

        more_options = QLabel("Specific sampling options available in \"Legacy\" mode")
        more_options.setStyleSheet("font-weight: bold;")

        layout_row_5.addWidget(more_options)

        layout_container.addWidget(label_samplingParameters)
        layout_container.addWidget(self.row_1)
        layout_container.addWidget(self.row_2)
        layout_container.addWidget(self.row_3)
        layout_container.addWidget(self.row_4)
        layout_container.addWidget(self.row_5)

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit { background-color: white; }
        """)

        ''' FUNCTIONS '''
        self.input_spatialRes.textChanged.connect(lambda: photo.updateOverlay(self.input_spatialRes.text()))


    #     widgets = []
    #     layout = QGridLayout()

    #     self.result = ClickableImage()

    #     control_col = QWidget()
    #     layout_col = QVBoxLayout()

    #     # Inputs for printer movement
    #     transfer_height = InputField("Transfer height (mm): ")
    #     spatial_resolution = InputField("Spatial resolution:  ")
    #     spatial_resolution.input.textChanged.connect(lambda: updatePixelOverlay(self.result, spatial_resolution.input.text(), self.json_path["json"]))

    #     dwell_time = InputField("Dwell time (s):   ")

    #     tag_corner = InputField("Tag bottom-left corner: ")

    #     # Selection buttons for sharpie and ROI
    #     selection_box = QWidget(objectName="light_blue_box")
    #     selection_box.setStyleSheet("QWidget { background-color: #C8D3F1; }")
    #     selection_box_layout = QHBoxLayout()

    #     selection_label = QLabel("Selection type: ", objectName="larger")

    #     dot_select = QRadioButton("Dot")
    #     dot_select.clicked.connect(lambda: self.handle_selection(dot_select))
    #     dot_select.setChecked(True) # selected on default

    #     rectangle_select = QRadioButton("Rectangle")
    #     rectangle_select.clicked.connect(lambda: self.handle_selection(rectangle_select))

    #     button_group = QButtonGroup()
    #     button_group.addButton(dot_select)
    #     button_group.addButton(rectangle_select)

    #     selection_box_layout.addWidget(selection_label)
    #     selection_box_layout.addWidget(dot_select)
    #     selection_box_layout.addWidget(rectangle_select)

    #     selection_box.setLayout(selection_box_layout)

    #     # Errors in unwarping (TODO)
    #     error_box = QWidget(objectName="light_blue_box")
    #     error_box.setStyleSheet("QWidget { background-color: #C8D3F1; }")
    #     error_box_layout = QVBoxLayout()

    #     reprojection_error = QLabel("Reprojection error: ", objectName="larger")
    #     rms_error = QLabel("RMS error: ", objectName="larger")

    #     error_box_layout.addWidget(reprojection_error)
    #     error_box_layout.addWidget(rms_error)

    #     error_box.setLayout(error_box_layout)

    #     generate_button = QPushButton("Generate location for regions", objectName="clear")
    #     generate_button.clicked.connect(lambda: generateProbeAcquisition(self.result.dot, self.result.rectangle, self.json_path["json"], self.printer, self.result, tag_corner))

    #     send_button = QPushButton("Send to printer", objectName="dark_blue")
    #     send_button.clicked.connect(lambda: sendLocations(self.result.real_points, dwell_time.input.text(), transfer_height.input.text()))

    #     # Set layout
    #     layout.addWidget(self.result, 0, 0, 12, 3, alignment=Qt.AlignLeft)
    #     layout.addWidget(dwell_time, 2, 4)
    #     layout.addWidget(transfer_height, 3, 4)
    #     layout.addWidget(spatial_resolution, 4, 4)
    #     layout.addWidget(tag_corner, 5, 4)
    #     layout.addWidget(selection_box, 6, 4, 1, 2)
    #     layout.addWidget(error_box, 7, 4, 1, 2)
    #     layout.addWidget(generate_button, 8, 4, 1, 2)
    #     layout.addWidget(send_button, 9 , 4, 1, 2)

    #     self.setLayout(layout)

    # def handle_selection(self, button):
    #     self.result.type = button.text()

    # def receiveResult(self, img):
    #     self.result.setNewPixmap(img)
