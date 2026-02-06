from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QSlider, QComboBox, QFrame, QApplication, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect

from Unwarping_App.components.utils import processUpload, addAllWidgets, calculateOffset, generateTransformationFolder
from Unwarping_App.components.common import NewTransformationItem, CamFeed

class TransformationReview(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    # def __init__(self, stacked, printer, vars):
    #     super().__init__()
    #     self.stacked = stacked
    #     self.printer = printer
    #     self.vars = vars
    #     self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label_review = QLabel("Review Transformation", objectName="page_title")
        label_estimate = QLabel("Estimated probe-to-camera offset:")
        label_offset = QLabel("<OFFSET RESULT HERE>")

        component_unwarpResult = CamFeed()

        button_save = QPushButton("Save transformation", objectName="headerBlue")

        layout.addStretch()
        layout.addWidget(label_review, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(label_estimate, alignment=Qt.AlignCenter)
        layout.addWidget(label_offset, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(component_unwarpResult, alignment=Qt.AlignCenter)
        layout.addWidget(button_save, alignment=Qt.AlignCenter)
        layout.addStretch()







''' OLD CODE BELOW (NOT FOR THIS PAGE) '''
        # app_window = self.window()
        # size = app_window.size()

        # widgets = []

        # summary = QLabel("Some text explaining what this does!")

        # checkerboard = NewTransformationItem("Checkerboard photos", 1, size.width())
        # checkerboard.action.clicked.connect(lambda: self.stacked.setCurrentIndex(5))
        # checkerboard.upload.clicked.connect(lambda: processUpload(checkerboard, "file"))

        # probe = NewTransformationItem("Probe detection", 2, size.width())
        # probe.action.clicked.connect(lambda: self.stacked.setCurrentIndex(6))
        # probe.upload.clicked.connect(lambda: processUpload(probe, "folder"))

        # offset = NewTransformationItem("Offset", 3, size.width())
        # offset.action.clicked.connect(lambda: calculateOffset(self.vars, offset.container))

        # issues_box = QWidget(objectName="light_blue_box")
        # issues_label = QLabel("Found issues:", objectName="larger")
        # issues_label.setStyleSheet("background-color: #C8D3F1;")

        # issues_list = QLabel("No issues found!", objectName="light_blue_box")

        # issues_layout = QVBoxLayout()
        # issues_layout.addWidget(issues_label)
        # issues_layout.addWidget(issues_list, alignment=Qt.AlignLeft)
        # issues_box.setLayout(issues_layout)

        # save_transformation = QPushButton("Save to transformation", objectName="dark_blue")
        # save_transformation.clicked.connect(lambda: generateTransformationFolder(self.vars))

        # widgets.append(summary)
        # widgets.append(checkerboard)
        # widgets.append(probe)
        # widgets.append(offset)
        # widgets.append(issues_box)
        # widgets.append(save_transformation)

        # layout = QVBoxLayout()
        # layout = addAllWidgets(layout, widgets)

        # layout.setAlignment(checkerboard, Qt.AlignCenter)
        # layout.setAlignment(probe, Qt.AlignCenter)
        # layout.setAlignment(offset, Qt.AlignCenter)

        # self.setLayout(layout)