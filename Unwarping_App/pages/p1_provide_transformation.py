from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout,  QHBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import pyqtSignal, Qt, QPoint

from Unwarping_App.components.common import TagInformationSection, UnwarpComparison
from Unwarping_App.components.utils import processUpload, verifyTransformation, addAllWidgets


''' This page handles any existing transformations the user provides'''
class ProvideTransformation(QWidget):
    next = pyqtSignal()

    def __init__(self):
        super().__init__()
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

        # LEFT COLUMN
        component_unwarpComparison = UnwarpComparison()


        # RIGHT COLUMN
        right = QWidget()
        right_layout = QVBoxLayout(right)

        label = QLabel("Provide a Transformation", objectName="page_title")

        # Selection box
        select_box = FileSelection()

        # Tag inputs
        component_tagInfo = TagInformationSection()
        component_tagInfo.label_msg.show()

        button_next = QPushButton("Next", objectName="blue")
        button_next.clicked.connect(self.next.emit)

        right_layout.addStretch()
        right_layout.addWidget(label, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(select_box, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(component_tagInfo, alignment=Qt.AlignLeft | Qt.AlignTop)
        right_layout.addStretch()
        right_layout.addWidget(button_next, alignment=Qt.AlignRight)

        # FULL PAGE
        layout.addWidget(component_unwarpComparison)
        layout.addWidget(right)


class FileSelection(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        select_box_layout = QVBoxLayout(container)

        folder_path = QLabel("", objectName="path_label")
        folder_select_btn = QPushButton("Select file", objectName="blue")
        
        self.label_error = QLabel("", objectName="light_blue_box")
        self.label_error.hide()

        select_box_layout.addWidget(folder_path)
        select_box_layout.addWidget(folder_select_btn, alignment=Qt.AlignCenter)
        select_box_layout.addWidget(self.label_error, alignment=Qt.AlignCenter)

        container.setFixedWidth(475)

        layout.addWidget(container)
