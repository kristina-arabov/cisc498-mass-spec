from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt

import Unwarping_App.components.utils as utils

class LandingPage(QWidget):
    provideTransformation = pyqtSignal()
    createTransformation = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())
        
        widgets = []
        
        page_title = QLabel("Fisheye Unwarping Application for Sampling", objectName="page_title")
        text_box = QLabel("Happy unwarping!", objectName="light_blue_box")

        button_row = QVBoxLayout()
        provide_transformation = QPushButton("Use a working transformation", objectName="blue")
        provide_transformation.clicked.connect(self.provideTransformation.emit)

        create_transformation = QPushButton("Create a new transformation", objectName="clear")
        create_transformation.clicked.connect(self.createTransformation.emit)

        button_row.addWidget(provide_transformation, alignment=Qt.AlignCenter)
        button_row.addWidget(create_transformation, alignment=Qt.AlignCenter)
        
        space = QLabel(" ")

        widgets.append(page_title)
        widgets.append(text_box)
        widgets.append(button_row)
        widgets.append(space)

        layout = QVBoxLayout()
        layout = utils.addAllWidgets(layout, widgets)

        self.setLayout(layout)
