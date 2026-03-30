import os
import shutil

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt


class SamplingComplete(QWidget):
    goToPrerun = pyqtSignal()
    goToROI = pyqtSignal()

    def __init__(self, sampling):
        super().__init__()
        self.sampling = sampling
        self.initUI()
    
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        
        layout = QVBoxLayout(self)

        label_finished = QLabel("Sampling run finished", objectName="page_title")

        button_save = QPushButton("Save timestamp CSV file", objectName="blue")

        button_prerun = QPushButton("Return to Pre-run Config", objectName="headerBlue")

        button_roi = QPushButton("Return to ROI Selection", objectName="headerBlue")

        layout.addStretch()
        layout.addWidget(label_finished, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(button_save, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(button_prerun, alignment=Qt.AlignCenter)
        layout.addWidget(button_roi, alignment=Qt.AlignCenter)
        layout.addStretch()

        # FUNCTIONS ----------------------------------------
        button_save.clicked.connect(self.saveCSV)
        button_prerun.clicked.connect(self.goToPrerun.emit)
        button_roi.clicked.connect(self.goToROI.emit)


    def saveCSV(self):
        if not self.sampling.csv_filename or not os.path.exists(self.sampling.csv_filename):
            return

        default_name = os.path.basename(self.sampling.csv_filename)
        default_dir = os.path.join("collectedData", default_name)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV File",
            default_dir,
            "CSV Files (*.csv)"
        )

        if not path:
            return

        # Ensure .csv extension
        if not path.lower().endswith(".csv"):
            path += ".csv"

        shutil.copy2(self.sampling.csv_filename, path)
