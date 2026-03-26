from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QMovie
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect, QSize

import cv2

from Unwarping_App.components.common import ClickableImage

from Unwarping_App.services import sampling_service

class SamplingProgress(QWidget):
    next = pyqtSignal()
    returnToConfig = pyqtSignal()

    def __init__(self, printer, sampling):
        super().__init__()

        self.printer = printer
        self.sampling = sampling
        
        self.initUI()

    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)
        gif = QMovie("Unwarping_App/components/images/Loading.gif")

        self.photo = ClickableImage()

        # RIGHT COLUMN ----------------------------------------
        right = QWidget()
        layout_right = QVBoxLayout(right)

        self.img_loadingCircle = QLabel()
        self.img_loadingCircle.setMovie(gif)
        gif.start()
        gif.setScaledSize(QSize(100, 100))

        self.label_points = QLabel("0/0 points sampled")
        self.label_estimatedTime = QLabel("Estimated time left: ___")

        self.button_pause = QPushButton("Pause", objectName="headerBlue")

        self.operations = OperationButtons()
        self.operations.hide()

        button_temp = QPushButton("Temporary next button", objectName="headerBlue")
        button_temp.clicked.connect(self.next.emit)

        layout_right.addStretch()
        layout_right.addWidget(self.img_loadingCircle, alignment=Qt.AlignCenter)
        layout_right.addStretch()
        layout_right.addWidget(self.operations)
        layout_right.addWidget(self.label_points, alignment=Qt.AlignCenter)
        # layout_right.addWidget(self.label_estimatedTime,alignment=Qt.AlignCenter)
        layout_right.addStretch()
        layout_right.addWidget(self.button_pause)
        layout_right.addWidget(button_temp, alignment=Qt.AlignCenter)
        layout_right.addStretch()


        layout.addWidget(self.photo)
        layout.addWidget(right)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  


        # FUNCTIONS ----------------------------------------
        self.button_pause.clicked.connect(lambda: self.handlePause(True))

        self.operations.btn_resume.clicked.connect(lambda: self.handlePause(False))
        self.operations.btn_abort.clicked.connect(lambda: self.stopSampling())

        sampling_service.progress.pointUpdated.connect(lambda: self.updateLabels("points"))
        sampling_service.progress.samplingDone.connect(lambda: self.next.emit())


    def updateLabels(self, type):
        if type == "points":
            fraction = sampling_service.progress.fraction
            self.label_points.setText(f"{fraction} points sampled")

            # Update the grid coloration based on sampled points.
            if hasattr(self.photo, "setSampledPoints"):
                try:
                    self.photo.setSampledPoints(getattr(self.sampling, "sampled_points_set", set()))
                except Exception:
                    pass

    
    def handlePause(self, stopped):
        if stopped:
            try:
                sampling_service.pause(self.printer)
            except:
                pass

            self.img_loadingCircle.hide()
            self.label_points.hide()
            self.button_pause.hide()
            self.operations.show()
        else:
            self.img_loadingCircle.show()
            self.label_points.show()
            self.button_pause.show()
            self.operations.hide()

            try:
                sampling_service.resume(self.printer)
            except:
                pass



    def stopSampling(self):
        # Reset as default
        self.img_loadingCircle.show()
        # self.label_estimatedTime.show()
        self.label_points.show()
        self.button_pause.show()

        self.operations.hide()

        # Clear any highlighted grid cells.
        if hasattr(self.photo, "setSampledPoints"):
            try:
                self.photo.setSampledPoints(set())
            except Exception:
                pass

        # Return to previous page (signal)
        self.returnToConfig.emit()

        sampling_service.stop(self.printer)


        
class OperationButtons(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        label = QLabel("Sampling Paused")
        label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        self.btn_resume = QPushButton("Resume", objectName="blue")
        self.btn_abort = QPushButton("Abort", objectName="red")

        layout.addWidget(label, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.btn_resume, alignment=Qt.AlignCenter)
        layout.addWidget(self.btn_abort, alignment=Qt.AlignCenter)
        layout.addStretch()