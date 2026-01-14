from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout,  QHBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import Qt, QPoint

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

        layout = QHBoxLayout(self)

        # LEFT COLUMN
        left = QWidget()
        left_layout = QVBoxLayout(left)

        feed = CamFeed("Live feed here")
        unwarp_component = ArrowButton()
        result = CamFeed("Result here")

        left_layout.addWidget(feed)
        left_layout.addWidget(unwarp_component)
        left_layout.addWidget(result)


        # RIGHT COLUMN
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


        # Next button (TODO connect page)
        next_btn = QPushButton("Next", objectName="blue")

        right_layout.addStretch()
        right_layout.addWidget(label)
        right_layout.addWidget(select_box)
        right_layout.addStretch()
        right_layout.addWidget(next_btn, alignment=Qt.AlignRight)

        # FULL PAGE
        layout.addWidget(left)
        layout.addWidget(right)


class CamFeed(QWidget):
    def __init__(self, text):
        super().__init__()

        layout = QHBoxLayout()

        # TODO Dynamic sizes
        self.feed_width = int(1280 * 0.4)
        self.feed_height = int(720 * 0.4)

        # Text here if needed
        self.image_label = QLabel(objectName="camera_initial")
        self.image_label.setFixedSize(self.feed_width, self.feed_height)
        self.image_label.setText(text)

        self.cam_thread = None

        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

class ArrowButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        self.setFixedHeight(100)

        self.button = QPushButton("Unwarped", objectName="clear")
        # self.button.setEnabled(False)
        
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor("#132c49"), 2) # CUstom colour here
        painter.setPen(pen)

        w = self.width()
        h = self.height()
        center_x = w // 2

        painter.drawLine(center_x, 0, center_x, h // 2)
        painter.drawLine(center_x, h // 2, center_x, h)

        # Arrow point
        arrow = QPolygon([
            QPoint(center_x - 6, h - 8),
            QPoint(center_x + 6, h - 8),
            QPoint(center_x, h)
        ])

        painter.setBrush(QColor("#132c49")) 
        painter.drawPolygon(arrow)