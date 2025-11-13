from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
import sys

class InputPopUp(QDialog):
    def __init__(self, title, label, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(450, 250)
        
        # Set the main background color
        self.setStyleSheet("background-color: #BADCF7;")
        
        # Create a label for the input prompt
        self.prompt_label = QLabel(self)
        self.prompt_label.setText("Enter File Name:")
        self.prompt_label.setAlignment(Qt.AlignCenter)
        self.prompt_label.setStyleSheet("font-size: 24px; color: #000000; font-weight: bold;")
        self.prompt_label.setGeometry(100, 50, 250, 30)
        
        # Create a line edit widget for user input
        self.input_line_edit = QLineEdit(self)
        self.input_line_edit.setAlignment(Qt.AlignCenter)
        self.input_line_edit.setStyleSheet("font-size: 14px; background-color: white; border-radius: 8px;")
        self.input_line_edit.setGeometry(100, 100, 250, 30)
        
        # Create Save button
        self.save_button = QPushButton('Save', self)
        self.save_button.setStyleSheet("QPushButton{background-color: #1B98E0; font-size: 14px; border-radius: 8px; color: #FFFFFF;} QPushButton:hover { background-color: #0E6EB8; } QPushButton:pressed { background-color: #0A4C7D; }")
        self.save_button.setGeometry(100, 150, 100, 30)
        self.save_button.clicked.connect(self.accept)
        self.save_button.clicked.connect(self.close)
        
        # Create Cancel button
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.setStyleSheet("QPushButton{background-color: #465F66; font-size: 14px; border-radius: 8px; color: #FFFFFF;} QPushButton:hover { background-color: #34484F; } QPushButton:pressed { background-color: #1F2B30; }")
        self.cancel_button.setGeometry(250, 150, 100, 30)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.clicked.connect(self.close)
        
    def getText(self):
        return self.input_line_edit.text()

if __name__ == '__main__':
   
    
    popup = InputPopUp('Error', 'Connection Error')
    
    popup.exec_()
   
    
  
    
    # Properly exit the application
    sys.exit(0)
