from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout
import sys

class InfoPopUp(QDialog):
    def __init__(self, title, label, parent=None):
        super().__init__(parent)
        self.setWindowTitle("info")
        self.setFixedSize(450, 300)
        
        # Set the main background color
        self.setStyleSheet("background-color: #E8F5FC;")
        
        # Create a label for the input prompt
        self.prompt_label = QLabel(self)
        self.prompt_label.setText(label)
        self.prompt_label.setStyleSheet("font-size: 30px; color: #000000; font-weight: bold;")
        self.prompt_label.setGeometry(25, 140, 400, 40)
        self.prompt_label.setAlignment(Qt.AlignCenter)

        # Create a white 'X' inside the circle
        self.x_label = QLabel(self)
        self.x_label.setGeometry(165, 8, 122, 122)
        self.x_label.setStyleSheet("color: white; font-size: 80px; font-weight: bold; border-radius: 61px; background-color: #1B98E0;border: 1px solid #000000;")
        self.x_label.setAlignment(Qt.AlignCenter)
        self.x_label.setText("i")

        
        # Create Ok button
        self.ok_button = QPushButton('OK', self)
        self.ok_button.setGeometry(165,181,122,30)
        self.ok_button.setStyleSheet("background-color: #1B98E0; color: white; font-size: 20px; border-radius: 15px; ")
        self.ok_button.clicked.connect(self.accept)
       
        
        self.message = QLabel(self)
        self.message.setText(label)
        self.message.setStyleSheet("font-size: 15px; color: #000000; font-weight: semi-bold; background-color: #BADCF7; ")
        self.message.setGeometry(39, 230, 370, 60)
        self.message.setWordWrap(True)
        
        

        
    



if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    popup = InfoPopUp('Error', 'Connection Error')
    
    popup.exec_()
   
    
  
    
    # Properly exit the application
    sys.exit(0)
