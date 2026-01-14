from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout,  QPushButton
from PyQt5.QtCore import Qt

from Unwarping_App.components.common import FolderSelect, CheckItem
from Unwarping_App.components.utils import processUpload, verifyTransformation, addAllWidgets

''' This page handles any existing transformations the user provides'''
class ProvideTransformation(QWidget):
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

        # widgets = []

        # summary = QLabel("Provide a working transformation that will be applied to any photos taken with the current set-up.")

        # folder_select = FolderSelect()
        # folder_select.upload.clicked.connect(lambda: processUpload(folder_select, "folder"))

        # checking_layout = QVBoxLayout()

        # checkerboard_check = CheckItem("Checkerboard photos")
        # apriltag_check = CheckItem("AprilTag photos")
        # json_check = CheckItem("JSON file")

        # checking_layout.addWidget(checkerboard_check)
        # checking_layout.addWidget(apriltag_check)
        # checking_layout.addWidget(json_check)

        # verify_button = QPushButton("Verify transformation", objectName="dark_blue")
        # verify_button.clicked.connect(lambda: verifyTransformation(folder_select.path.text(), self.json_path))

        # widgets.append(summary)
        # widgets.append(folder_select)
        # widgets.append(checking_layout)
        # widgets.append(verify_button)

        # layout = QVBoxLayout()
        # layout = addAllWidgets(layout, widgets)

        # layout.setAlignment(checking_layout, Qt.AlignCenter)

        # self.setLayout(layout)
