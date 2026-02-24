from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QDialog, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal, Qt, QPoint

import Unwarping_App.components.utils as utils

class LandingPage(QWidget):
    provideTransformation = pyqtSignal()
    createTransformation = pyqtSignal()

    clearVals = pyqtSignal()

    def __init__(self, transformation):
        super().__init__()

        self.transformation = transformation

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
        button_row.setSpacing(25)

        provide_transformation = QPushButton("Sample with working transformation", objectName="blue")
        provide_transformation.setFixedWidth(400)
        provide_transformation.clicked.connect(self.provideTransformation.emit)

        self.create_transformation = QPushButton("Create new transformation", objectName="dark_blue")
        self.create_transformation.setFixedWidth(400)
        self.create_transformation.clicked.connect(lambda: self.handleCreateTransformation())

        button_row.addWidget(provide_transformation, alignment=Qt.AlignTop | Qt.AlignCenter)
        button_row.addWidget(self.create_transformation, alignment=Qt.AlignTop | Qt.AlignCenter)
        button_row.addStretch()

        widgets.append(page_title)
        widgets.append(text_box)
        widgets.append(button_row)

        layout = QVBoxLayout(self)
        layout = utils.addAllWidgets(layout, widgets)

    def handleCreateTransformation(self):
        in_progress = False

        # Check if there are any non-empty values
        for key, val in vars(self.transformation).items():
            # tag_bottom_left is a list 
            if key == "tag_bottom_left":
                if val[0] is not None or val[1] is not None:
                    in_progress = True
            # Check all other vals
            elif val is not None:
                in_progress = True
            
        # Display popup options if transformation is in progress
        if in_progress:
            dialog = ProgressDialog(self, self.transformation)
            pos = self.create_transformation.mapToGlobal(QPoint(-480, self.create_transformation.height()))
            
            dialog.move(pos)
            dialog.show()
            dialog.raise_() 
            
            dialog.button_clear.clicked.connect(lambda: self.handleSelection(dialog, "clear"))
            dialog.button_resume.clicked.connect(lambda: self.handleSelection(dialog))
        
        # Proceed to transformation workflow
        else:
            self.createTransformation.emit()

    # Handle the user's selection for progressing to the transformatio workflow
    def handleSelection(self, dialog, type=None):
        if type == "clear":
            # Clear all
            self.transformation.resetVals()
            
            # Emit signal to clear inputs
            self.clearVals.emit()

        # Proceed to transformation flow
        dialog.hide()
        self.createTransformation.emit()
    

class ProgressDialog(QWidget):
    def __init__(self, parent=None, transformation=None):

        super().__init__(parent)

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.setFixedSize(550, 300)

        layout = QVBoxLayout(self)

        # TODO create a border?
        label_warn = QLabel("Warning!")
        label_warn.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;                     
        """)

        label_msg = QLabel("A transformation is currently in progress. You may continue the current transformation workflow,\nor create a new transformation.")

        buttons_row = QWidget()
        buttons_layout = QHBoxLayout(buttons_row)

        self.button_resume = QPushButton("Resume", objectName="blue")
        self.button_clear = QPushButton("Clear", objectName="red")

        buttons_layout.addWidget(self.button_resume)
        buttons_layout.addWidget(self.button_clear)

        layout.addWidget(label_warn, alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(label_msg, alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(buttons_row, alignment=Qt.AlignCenter)