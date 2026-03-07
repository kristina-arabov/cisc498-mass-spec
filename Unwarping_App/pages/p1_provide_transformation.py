from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout,  QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import pyqtSignal, Qt, QPoint

from Unwarping_App.components.common import FolderSelect, CheckItem, UnwarpComparison, TagInformationSection
from Unwarping_App.components.utils import processUpload, verifyTransformation, addAllWidgets, updateFrame
from Unwarping_App.services import calibration_service, sampling_service


''' This page handles any existing transformations the user provides'''
class ProvideTransformation(QWidget):
    next = pyqtSignal()
    resultAvailable = pyqtSignal(object)

    def __init__(self, camera, lights, transformation):
        super().__init__()
        self.camera = camera
        self.lights = lights
        self.transformation = transformation

        self.initUI()
        
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)

        ''' LEFT COLUMN '''
        self.component_unwarpComparison = UnwarpComparison()

        ''' RIGHT COLUMN '''
        right = QWidget()
        right_layout = QVBoxLayout(right)

        label = QLabel("Provide a Transformation", objectName="page_title")

        # Selection box
        self.file_box = FileSelection()

        # Tag inputs
        component_tagInfo = TagInformationSection()
        component_tagInfo.label_msg.show()

        button_next = QPushButton("Next", objectName="blue")
        button_next.clicked.connect(self.next.emit)

        right_layout.addStretch()
        right_layout.addWidget(label, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(self.file_box, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(component_tagInfo, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addStretch()
        right_layout.addWidget(button_next, alignment=Qt.AlignRight)

        ''' COMPOSE '''
        layout.addWidget(self.component_unwarpComparison)
        layout.addWidget(right)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        ''' FUNCTIONS '''
        self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(self.component_unwarpComparison.feed, frame))
        self.component_unwarpComparison.arrow.button.clicked.connect(lambda: self.applyTransformation())
        
        self.file_box.btn_select.clicked.connect(lambda: self.selectFile())

    def selectFile(self):
        path, _ = QFileDialog.getOpenFileName(caption="Select Transformation File", filter="JSON Files (*.json)")
        self.file_box.path.setText(path)

        # Update transformation vars  
        sampling_service.setTransformation(self.transformation, path)


    def applyTransformation(self):
        img = self.camera.frame.copy()
        unwarped = calibration_service.unwarpPhoto(img, self.transformation)

        # Show unwarped img in result container
        calibration_service.updateResult(unwarped, self.component_unwarpComparison.result)

        # Send signal to other pages in sampling workflow
        self.resultAvailable.emit(unwarped)


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

        container.setFixedWidth(475)

        layout.addWidget(container)
