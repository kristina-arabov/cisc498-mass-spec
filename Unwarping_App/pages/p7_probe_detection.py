from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QToolButton, QSlider, QComboBox, QApplication
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

import cv2

from Unwarping_App.components.common import CamFeed, LightingDropdown, TagOverlay, TagInformationSection
from Unwarping_App.components.utils import addAllWidgets, updateFrame, unwarpPhoto, getPrinterPosition, setBrightness, updateDropdownIndex
from Unwarping_App.services import device_service, calibration_service

class ProbeDetection(QWidget):
    next = pyqtSignal()
    offsetAvailable = pyqtSignal()

    def __init__(self, camera, lights, printer, transformation):
        super().__init__()
        self.camera = camera
        self.lights = lights
        self.printer = printer

        self.transformation = transformation

        self.initUI()

    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)

        # LEFT COLUMN ----------------------------------------
        left = QWidget()
        layout_left = QVBoxLayout(left)


        
        self.component_tag = TagInstructions(self.camera, self.printer, self.transformation)

        val = self.compute_scale()
        component_cameraFeed = CamFeed(scale=val)


        layout_left.addWidget(component_cameraFeed)
        layout_left.addWidget(self.component_tag)

        layout_left.setContentsMargins(0, 0, 0, 0)
        layout_left.setSpacing(0)


        # RIGHT COLUMN ----------------------------------------
        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_probeDetection = QLabel("Probe Detection", objectName="page_title")

        # Lighting control
        component_lightControl = LightingDropdown()

        # Tag information
        self.component_tagInformation = TagInformationSection()
        self.component_tagInformation.setFixedWidth(component_lightControl.sizeHint().width())

        button_next = QPushButton("Next", objectName="blue")
        button_next.clicked.connect(self.next.emit)
        button_next.setEnabled(False)
        self.button_next = button_next

        layout_right.addStretch()
        layout_right.addWidget(label_probeDetection, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(component_lightControl, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(self.component_tagInformation, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addStretch()
        layout_right.addWidget(button_next, alignment=Qt.AlignCenter | Qt.AlignRight)
        layout_right.addStretch()

        layout_right.setContentsMargins(10, 0, 0, 0)
        layout_right.setSpacing(10)

        # COMPOSE ----------------------------------------
        layout.addWidget(left)
        layout.addWidget(right, alignment=Qt.AlignCenter)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0) 

        # FUNCTIONS --------------------------------------
        self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(component_cameraFeed, frame, crosshair=True))
        component_lightControl.slider.valueChanged.connect(lambda: device_service.set_brightness(component_lightControl.slider.value(), self.lights))

        # Update X coordinate
        self.component_tagInformation.input_bottomLeftX.textChanged.connect(lambda: calibration_service.updateTag(self.transformation, 
                                                                                                                  self.component_tagInformation.input_bottomLeftX.text(), 
                                                                                                                  "X"))
        
        # Update Y coordinate
        self.component_tagInformation.input_bottomLeftY.textChanged.connect(lambda: calibration_service.updateTag(self.transformation, 
                                                                                                                  self.component_tagInformation.input_bottomLeftY.text(), 
                                                                                                                  "Y"))
        
        # Update tag size
        self.component_tagInformation.input_tagSize.textChanged.connect(lambda: calibration_service.updateTag(self.transformation, 
                                                                                                              self.component_tagInformation.input_tagSize.text(), 
                                                                                                              "size"))
        

        # Check ability to calculate offset
        self.component_tagInformation.input_bottomLeftX.textChanged.connect(lambda: self.checkOffset())
        self.component_tagInformation.input_bottomLeftY.textChanged.connect(lambda: self.checkOffset())
        self.component_tagInformation.input_tagSize.textChanged.connect(lambda: self.checkOffset())

        self.component_tag.checkOffset.connect(lambda: self.checkOffset())
    

    # Function to check if offset can be calculated
    def checkOffset(self):
        # All inputs and corners must not be None/False
        x_coord = self.component_tagInformation.input_bottomLeftX.text()
        y_coord = self.component_tagInformation.input_bottomLeftY.text()
        tag_size = self.component_tagInformation.input_tagSize.text()

        # Permit page transition if all corners mapped
        if x_coord and y_coord and tag_size and not False in self.component_tag.corners_imaged:
            self.offsetAvailable.emit()
            self.button_next.setEnabled(True)
        else:
            self.button_next.setEnabled(False)



    # Function to reset front-end
    def clearAll(self):
        # Reset tag diagram and progress bar
        self.component_tag.corners_imaged = [False, False, False, False]
        self.component_tag.idx = 0
        self.component_tag.setProbedColors()

        self.component_tag.button_nextCorner.setEnabled(True)
        self.component_tag.button_previousCorner.setEnabled(False)
        self.component_tag.component_tagOverlay.corner_colours[0] = QColor("#212D99")
        self.component_tag.label_instructions.setText("Please manually align the highlighted blue corner with the crosshair.")
        

        self.component_tag.line_progressBar.setValue(0)
        self.component_tag.update()

        # Reset tag inputs
        self.component_tagInformation.input_bottomLeftX.clear()
        self.component_tagInformation.input_bottomLeftY.clear()
        self.component_tagInformation.input_tagSize.clear()



    # Function to handle scaling of image feed
    def compute_scale(self):
        screen = QApplication.instance().primaryScreen()
        available = screen.size().height()

        base_screen_height = 1117
        tag_component_height = self.component_tag.sizeHint().height()

        available = available - tag_component_height

        base_scale = 0.7

        scale = base_scale * (available / base_screen_height)
        scale = min(scale, base_scale)

        return scale


class TagInstructions(QWidget):
    checkOffset = pyqtSignal()

    def __init__(self, camera, printer, transformation):
        super().__init__()

        self.camera = camera
        self.printer = printer
        self.transformation = transformation

        self.idx = 0
        self.corners_imaged = [False, False, False, False]

        layout = QHBoxLayout(self)

        self.component_tagOverlay = TagOverlay()
        self.component_tagOverlay.corner_colours[self.idx] = QColor("#212D99")

        # COLUMN 1 --------------------------------------
        column_1 = QWidget()
        layout_column_1 = QVBoxLayout(column_1)

        self.label_instructions = QLabel("Please manually align the highlighted blue corner with the crosshair.")
        self.label_instructions.setWordWrap(True)
        self.label_instructions.adjustSize()

        self.line_progressBar = QProgressBar()
        self.line_progressBar.setRange(0, 100)
        self.line_progressBar.setFormat("%p %") 
        self.line_progressBar.setTextVisible(True)
        self.line_progressBar.setFixedWidth(self.label_instructions.width())

        layout_column_1.addWidget(self.label_instructions, alignment=Qt.AlignLeft)
        layout_column_1.addWidget(self.line_progressBar, alignment=Qt.AlignLeft)


        # COLUMN 2 --------------------------------------
        column_2 = QWidget()
        layout_column_2 = QVBoxLayout(column_2)

        self.button_nextCorner = QPushButton("Next corner", objectName="headerBlue")
        self.button_previousCorner = QPushButton("Previous corner", objectName="clear")
        self.button_previousCorner.setEnabled(False)

        self.button_probeLocation = QPushButton("Corner at crosshair", objectName="blue")

        layout_column_2.addStretch()
        layout_column_2.addWidget(self.button_nextCorner)
        layout_column_2.addWidget(self.button_previousCorner)
        layout_column_2.addWidget(self.button_probeLocation)
        layout_column_2.addStretch()

        layout_column_2.setContentsMargins(0,0,0,0)
        layout_column_2.setSpacing(5)


        # COMPOSE --------------------------------------
        layout.addWidget(self.component_tagOverlay)
        layout.addWidget(column_1)
        layout.addWidget(column_2)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)



        # FUNCTIONS --------------------------------------
        self.button_nextCorner.clicked.connect(lambda: self.handleCorners("next"))
        self.button_previousCorner.clicked.connect(lambda: self.handleCorners("back"))
        self.button_probeLocation.clicked.connect(lambda: self.handleCornerConfirm())


    # Function to properly colour the corners of the tag diagram
    def handleCorners(self, type):
        # Move to next corner
        if type == "next":
            if (self.idx + 1) >= 3:
                self.button_nextCorner.setEnabled(False)    # Disable the button if the next increment will be the last corner
            
            self.idx += 1
            if self.idx >= 1:
                self.button_previousCorner.setEnabled(True)
        
        # Move to previous corner
        elif type == "back":
            if (self.idx - 1) == 0:
                self.button_previousCorner.setEnabled(False) # Disable the button if the next increment will be the first corner

            self.idx -= 1
            
            if self.idx < 3:
                self.button_nextCorner.setEnabled(True)
        
        self.setProbedColors()
        self.component_tagOverlay.corner_colours[self.idx] = QColor("#212D99")

        if self.corners_imaged[self.idx]:
            self.label_instructions.setText("Corner aligned!")
        else:
            self.label_instructions.setText("Please manually align the highlighted blue corner with the crosshair.")

        self.update()


    # Function to acquire the probe's position in alignment with a specific tag corner
    def handleCornerConfirm(self):
        # Obtain values for location
        img = self.camera.frame.copy()
        img = calibration_service.unwarpPhoto(img, self.transformation)

        position = device_service.getPrinterPosition(self.printer)

        # Enforce same printer height
        if position[2] != self.transformation.height:
            self.label_instructions.setText(f"Cannot image corner. Ensure the printer height is set to Z={self.transformation.height} for all crosshair alignments.")
            return

        setattr(self.transformation, f"loc{self.idx}", position)
        setattr(self.transformation, f"img{self.idx}", img)

        # Update front-end
        self.label_instructions.setText("Corner aligned!")
        self.corners_imaged[self.idx] = True

        # Progress bar status
        corners_probed = int(((self.corners_imaged.count(True))/ len(self.corners_imaged)) * 100)

        self.line_progressBar.setValue(corners_probed)

        # Send signal to calculate probe-to-camera offset with available values
        if not False in self.corners_imaged:
            self.checkOffset.emit()


    # Function to set colours to probed or not probed corners
    def setProbedColors(self):
        for i in range(4):
            self.component_tagOverlay.corner_colours[i] = QColor("#4FC46E") if self.corners_imaged[i] else QColor("#C5C5C5")

    