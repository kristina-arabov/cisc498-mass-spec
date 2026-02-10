from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout,  QHBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import pyqtSignal, Qt, QPoint

from Unwarping_App.components.common import FolderSelect, CheckItem, UnwarpComparison
from Unwarping_App.components.utils import processUpload, updateFrame, verifyTransformation, addAllWidgets


''' This page handles any existing transformations the user provides'''
class ProvideTransformation(QWidget):
    next = pyqtSignal()

    def __init__(self, camera, lights):
        super().__init__()
        self.camera = camera
        self.lights = lights

        self.initUI()
        
    # def __init__(self, json_path):
    #     super().__init__()
    #     self.json_path = json_path
    #     self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)

        ''' LEFT COLUMN '''
        component_unwarpComparison = UnwarpComparison()

        ''' RIGHT COLUMN '''
        right = QWidget()
        right_layout = QVBoxLayout(right)

        label = QLabel("Provide a Transformation", objectName="page_title")

        # Selection box
        select_box = QWidget(objectName="light_blue_box")
        select_box_layout = QVBoxLayout(select_box)

        folder_path = QLabel("<Path here>", objectName="path_label")
        folder_select_btn = QPushButton("Select file", objectName="blue")
        folder_error = QLabel("<Errors will go here>", objectName="light_blue_box")

        select_box_layout.addWidget(folder_path)
        select_box_layout.addWidget(folder_select_btn, alignment=Qt.AlignCenter)
        select_box_layout.addWidget(folder_error, alignment=Qt.AlignCenter)


        button_next = QPushButton("Next", objectName="blue")
        button_next.clicked.connect(self.next.emit)

        right_layout.addStretch()
        right_layout.addWidget(label)
        right_layout.addWidget(select_box)
        right_layout.addStretch()
        right_layout.addWidget(button_next, alignment=Qt.AlignRight)

        ''' COMPOSE '''
        layout.addWidget(component_unwarpComparison)
        layout.addWidget(right)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        ''' FUNCTIONS '''
        self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(component_unwarpComparison.feed, frame))

