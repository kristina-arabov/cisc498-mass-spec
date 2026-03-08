from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout,  QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import  QValidator
from PyQt5.QtCore import pyqtSignal, Qt, QPoint

from Unwarping_App.components.common import FolderSelect, CheckItem, UnwarpComparison, TagInformationSection
from Unwarping_App.components.utils import processUpload, verifyTransformation, addAllWidgets, updateFrame
from Unwarping_App.services import calibration_service, sampling_service, device_service


''' This page handles any existing transformations the user provides'''
class ProvideTransformation(QWidget):
    next = pyqtSignal()
    resultAvailable = pyqtSignal(object)

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
        self.valid_transformation = False

        # LEFT COLUMN ----------------------------------------
        self.component_unwarpComparison = UnwarpComparison()

        # RIGHT COLUMN ----------------------------------------
        right = QWidget()
        right_layout = QVBoxLayout(right)

        label = QLabel("Provide a Transformation", objectName="page_title")

        # Tag inputs
        self.component_tagInfo = TagInformationSection()

        # Selection box
        self.file_box = FileSelection()
        self.file_box.setFixedWidth(self.component_tagInfo.sizeHint().width())

        self.button_next = QPushButton("Next", objectName="blue")
        self.button_next.clicked.connect(self.next.emit)
        # TODO will uncomment after testing
        self.button_next.setEnabled(False) 

        right_layout.addStretch()
        right_layout.addWidget(label, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(self.file_box, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(self.component_tagInfo, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addStretch()
        right_layout.addWidget(self.button_next, alignment=Qt.AlignRight)

        # COMPOSE ----------------------------------------
        layout.addWidget(self.component_unwarpComparison)
        layout.addWidget(right)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # FUNCTIONS --------------------------------------
        self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(self.component_unwarpComparison.feed, frame))
        self.component_unwarpComparison.arrow.button.clicked.connect(lambda: self.applyTransformation())
        
        self.file_box.btn_select.clicked.connect(lambda: self.selectFile())


        # TODO will uncomment after testing
        self.component_tagInfo.input_bottomLeftX.textChanged.connect(lambda: self.checkAllowNext())
        self.component_tagInfo.input_bottomLeftY.textChanged.connect(lambda: self.checkAllowNext())
        self.component_tagInfo.input_tagSize.textChanged.connect(lambda: self.checkAllowNext())


    # Function to handle file selection
    def selectFile(self):
        path, _ = QFileDialog.getOpenFileName(caption="Select Transformation File", filter="JSON Files (*.json)")
        self.file_box.path.setText(path)

        # Update transformation vars  
        self.valid_transformation = sampling_service.setTransformation(self.transformation, path, self.valid_transformation)
        
        self.checkAllowNext()


    # Apply a selected transformation on the current camera frame
    def applyTransformation(self):
        try:
            img = self.camera.frame.copy()
            unwarped = calibration_service.unwarpPhoto(img, self.transformation)


            # TODO uncomment after testing
            # pos = device_service.getPrinterPosition(self.printer)

            # if pos[2] != self.transformation.height:
            #     print("height not same")
            #     return

            # Show unwarped img in result container
            calibration_service.updateResult(unwarped, self.component_unwarpComparison.result)

            # Send signal to other pages in sampling workflow
            self.resultAvailable.emit(unwarped)
            # self.checkAllowNext()
        except:
            print("doesnt run!")
            pass


    # TODO may be removed later
    # # Function to check if the user can unwarp a photo
    # def checkAllowUnwarp(self):
    #     # if file box not empty and cam + printer connected
    #     btn = self.component_unwarpComparison.arrow.button

    #     allow_unwarp = True
    #     btn.setEnabled(True)
       
    #     # Check if transformation file is valid
    #     if not self.valid_transformation:
    #         allow_unwarp = False
        
    #     # Check if camera is connected
    #     if not self.camera.running or not self.camera.capture.isOpened():
    #         allow_unwarp = False

        
    #     # Check if printer is connected and is at the same height as transformation
    #     pos = device_service.getPrinterPosition(self.printer)
    #     if not pos:
    #         allow_unwarp = False
    #     elif pos:
    #         if pos[2] != self.transformation.height:
    #             allow_unwarp = False


    #     if not allow_unwarp:
    #         btn.setEnabled(False)
        


    # Function to check if the user has provided the necessary information to proceed
    def checkAllowNext(self):
        allow_next = True
        self.button_next.setEnabled(True)
    

        img = self.component_unwarpComparison.result.image_label.pixmap()

        tag_X = self.component_tagInfo.input_bottomLeftX.text()
        tag_Y = self.component_tagInfo.input_bottomLeftY.text()
        tag_size = self.component_tagInfo.input_tagSize.text()

        # Check if image is not empty
        if img is None or img.isNull():
            allow_next = False

        # Check if transformation file is valid
        if not self.valid_transformation:
            allow_next = False

        # Check if tag inputs are valid
        try:
            tag_X = float(tag_X)
            tag_Y = float(tag_Y)
            tag_size = float(tag_size)

        except:
            allow_next = False

        # Disable next button if any issues
        if not allow_next:
            self.button_next.setEnabled(False)



# File selection component
class FileSelection(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        file_box_layout = QVBoxLayout(container)

        self.path = QLabel("", objectName="path_label")
        self.btn_select = QPushButton("Select file", objectName="blue")
        
        self.label_error = QLabel("", objectName="light_blue_box")
        self.label_error.hide()

        file_box_layout.addWidget(self.path)
        file_box_layout.addWidget(self.btn_select, alignment=Qt.AlignCenter)
        file_box_layout.addWidget(self.label_error, alignment=Qt.AlignCenter)

        layout.addWidget(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
