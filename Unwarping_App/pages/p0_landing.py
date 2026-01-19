from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt

import Unwarping_App.components.utils as utils

class LandingPage(QWidget):
    provideTransformation = pyqtSignal()
    createTransformation = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMaximumSize(1440, 851)
        self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())
        
        widgets = []
        
        page_title = QLabel("Welcome!", objectName="title_screen_title")
        text_box = QLabel("Start a new sampling run using an existing transformation file. \n If you are a first-time user, you need to create a transformation first.", objectName="title_screen_text")
        text_box.setAlignment(Qt.AlignCenter)

        button_row = QVBoxLayout()
        provide_transformation = QPushButton("Sample with working transformation", objectName="blue")
        provide_transformation.setFixedWidth(400)
        provide_transformation.clicked.connect(self.provideTransformation.emit)

        create_transformation = QPushButton("Create new transformation", objectName="dark_blue")
        create_transformation.setFixedWidth(400)
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
