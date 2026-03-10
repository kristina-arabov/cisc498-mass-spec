from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

import cv2
import json

from Unwarping_App.components.common import LightingDropdown, PortControl, CamFeed, ClickableImage
from Unwarping_App.components.utils import addAllWidgets, updateFrame, setBrightness, updateDropdownIndex, unwarpPhoto

class ROISelection(QWidget):
    next = pyqtSignal()
    resultAvailable = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.initUI()

    # def __init__(self, size, camera, light_connection, json_path):
    #     super().__init__()
    #     self.size = size
    #     self.camera = camera
    #     self.camera.enable_buttons.connect(self.camConnection)

    #     self.light_connection = light_connection
    #     self.light_connection.enable_buttons.connect(self.lightConnection)

    #     self.json_path = json_path
    #     self.initUI()
    
    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)

        self.photo = ClickableImage()

        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_selectArea = QLabel("Select sampling area", objectName="page_title")

        self.referencePoint = ReferencePointSection()
        self.ROI = DrawROISection()

        button_next = QPushButton("Next", objectName="blue")
        button_next.clicked.connect(self.next.emit)

        layout_right.addStretch()
        layout_right.addWidget(label_selectArea)
        layout_right.addWidget(self.referencePoint)
        layout_right.addWidget(self.ROI)
        layout_right.addStretch()
        layout_right.addWidget(button_next, alignment=Qt.AlignRight)
        layout_right.addStretch()

        layout.addWidget(self.photo)
        layout.addWidget(right)
        
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        ''' FUNCTIONS '''
        self.referencePoint.button_action.clicked.connect(lambda: self.setReference())

        self.ROI.button_draw.clicked.connect(lambda: self.ROIMode("Draw"))
        self.ROI.button_rectangle.clicked.connect(lambda: self.ROIMode("Rectangle"))

        self.ROI.button_pencil.clicked.connect(lambda: self.setDrawTool("pencil"))
        self.ROI.button_eraser.clicked.connect(lambda: self.setDrawTool("eraser"))

        self.ROI.button_convert.clicked.connect(self.photo.convertToPolygon)
        self.ROI.button_reset.clicked.connect(self.photo.resetROI)



    ''' Function to handle setting a reference point '''
    def setReference(self):
        if self.referencePoint.button_action.text() == "Select":
            self.referencePoint.button_action.setText("Done")
            self.photo.type = "Dot"

            self.ROI.button_draw.setEnabled(False)
            self.ROI.button_rectangle.setEnabled(False)

            if self.ROI.button_draw.isChecked():
                self.ROI.row_2.hide()
                self.ROI.row_3.hide()
        
        elif self.referencePoint.button_action.text() == "Done":
            self.referencePoint.button_action.setText("Select")
            self.photo.type = None

            # If a dot is on the image, enable the next component
            if self.photo.dot:
                self.ROI.button_draw.setEnabled(True)
                self.ROI.button_rectangle.setEnabled(True)

                if self.ROI.button_draw.isChecked():
                    self.ROIMode("Draw")
                elif self.ROI.button_rectangle.isChecked():
                    self.ROIMode("Rectangle")

    

    ''' Function to set the active draw tool (pencil or eraser) '''
    def setDrawTool(self, tool):
        self.photo.draw_mode = tool
        # Keep buttons in sync as a toggle pair
        self.ROI.button_pencil.setChecked(tool == "pencil")
        self.ROI.button_eraser.setChecked(tool == "eraser")

    ''' Function to handle when user selects a drawing type '''
    def ROIMode(self, type=None):
        # Handle rectangle selections
        if type == "Rectangle":
            self.ROI.row_2.hide()
            self.ROI.row_3.hide()
            self.photo.type = "Rectangle"
            self.photo.draw_mode = None
            # Clear any draw history when switching to Rectangle
            self.photo.draw_strokes = []
            self.photo.current_stroke = []
            self.photo.roi_closed = False
            self.photo.update()

        # Handle hand-drawn selections
        elif type == "Draw":
            self.ROI.row_2.show()
            self.ROI.row_3.show()
            self.photo.type = "Draw"
            # Clear any rectangle when switching to Draw
            self.photo.rectangle = None
            # Default to pencil when entering draw mode
            self.photo.draw_mode = "pencil"
            self.ROI.button_pencil.setChecked(True)
            self.ROI.button_eraser.setChecked(False)
            self.photo.update()

    ''' Reset the entire page back to its initial state '''
    def resetAll(self):
        # Reset canvas
        self.photo.dot = None
        self.photo.rectangle = None
        self.photo.draw_strokes = []
        self.photo.current_stroke = []
        self.photo.roi_closed = False
        self.photo.polygon_points = []
        self.photo.polygon_active = False
        self.photo.type = None
        self.photo.draw_mode = None
        self.photo.update()

        # Reset reference point section
        self.referencePoint.button_action.setText("Select")

        # Reset ROI section — disable buttons, hide tool rows, default to Draw
        self.ROI.button_draw.setEnabled(False)
        self.ROI.button_rectangle.setEnabled(False)
        self.ROI.button_draw.setChecked(True)
        self.ROI.button_rectangle.setChecked(False)
        self.ROI.button_pencil.setChecked(True)
        self.ROI.button_eraser.setChecked(False)
        self.ROI.row_2.hide()
        self.ROI.row_3.hide()

class ReferencePointSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QHBoxLayout(container)

        icon_number = QLabel("1")
        label_title = QLabel("Reference Point selection", objectName="larger")
        label_title.setStyleSheet("font-weight: bold;")

        self.button_action = QPushButton("Select", objectName="blue")

        layout_container.addWidget(icon_number, alignment=Qt.AlignLeft)
        layout_container.addWidget(label_title, alignment=Qt.AlignLeft)
        layout_container.addStretch()
        layout_container.addWidget(self.button_action)

        layout.addWidget(container)

        self.setStyleSheet("""
            QWidget#light_blue_box, QLabel { background-color: #C8D3F1; }
        """)


class DrawROISection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)

        ''' ROW 1 '''
        row_1 = QWidget()
        layout_row_1 = QHBoxLayout(row_1)

        icon_number = QLabel("2")
        label_selection = QLabel("ROI selection", objectName="larger")
        label_selection.setStyleSheet("font-weight: bold;")

        self.button_draw = QRadioButton("Draw")
        self.button_rectangle = QRadioButton("Rectangle")
        
        mode_group = QButtonGroup()
        mode_group.addButton(self.button_draw, 0)
        mode_group.addButton(self.button_rectangle, 1)

        self.button_draw.setChecked(True)

        layout_row_1.addWidget(icon_number, alignment=Qt.AlignLeft)
        layout_row_1.addWidget(label_selection, alignment=Qt.AlignLeft)
        layout_row_1.addStretch()
        layout_row_1.addWidget(self.button_draw)
        layout_row_1.addWidget(self.button_rectangle)


        ''' ROW 2 - pencil / eraser tools '''
        self.row_2 = QWidget()
        layout_row_2 = QHBoxLayout(self.row_2)

        self.button_pencil = QPushButton("✏  Pencil", objectName="blue")
        self.button_pencil.setCheckable(True)
        self.button_pencil.setChecked(True)

        self.button_eraser = QPushButton("◯  Eraser", objectName="clear")
        self.button_eraser.setCheckable(True)

        layout_row_2.addWidget(self.button_pencil)
        layout_row_2.addWidget(self.button_eraser)


        ''' ROW 3 - convert / reset + instructions '''
        self.row_3 = QWidget()
        layout_row_3 = QHBoxLayout(self.row_3)

        self.button_convert = QPushButton("⬡  Convert to Polygon", objectName="blue")
        self.button_reset = QPushButton("Reset", objectName="clear")
        label_instructions = QLabel("Draw an enclosed shape to continue")

        layout_row_3.addWidget(self.button_convert)
        layout_row_3.addWidget(self.button_reset)
        layout_row_3.addStretch()
        layout_row_3.addWidget(label_instructions, alignment=Qt.AlignRight)


        ''' COMPOSE ALL '''
        layout_container.addWidget(row_1)
        layout_container.addWidget(self.row_2)
        layout_container.addWidget(self.row_3)

        layout.addWidget(container)

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QPushButton#blue { background-color: #2A54F6; }
            QPushButton#clear { background-color: #F0F0F0; }
        """)

        ''' DISABLE / HIDE ON INITIALIZATION '''
        self.button_draw.setEnabled(False)
        self.button_rectangle.setEnabled(False)
        self.row_2.hide()
        self.row_3.hide()



    #     widgets = []
    #     layout = QGridLayout()

    #     # Image feed
    #     self.feed = CamFeed("")
    #     self.camera.change_pixmap_signal.connect(lambda frame: updateFrame(self.feed, frame))

    #     self.result = CamFeed("")
    #     self.result.hide() # Hide on default

    #     # Camera, result views
    #     show_cam = QPushButton("Camera view", objectName="blue")
    #     show_cam.clicked.connect(lambda: self.handleCam("cam"))

    #     show_result=QPushButton("Result", objectName="blue")
    #     show_result.clicked.connect(lambda: self.handleCam("result"))
    #     show_result.setEnabled(False)
        
    #     control_col = QWidget()
    #     layout_col = QVBoxLayout()

    #     # Port Controls 
    #     self.camera_connection = PortControl("Camera: ")
    #     self.camera_connection.connect_btn.clicked.connect(lambda: self.camConnection(True))
    #     self.camera_connection.disconnect_btn.clicked.connect(lambda: self.camConnection(False))
    #     self.camera_connection.update_btn.clicked.connect(lambda: self.camera_connection.updatePorts(self.camera))
    #     self.camera_connection.dropdown.currentIndexChanged.connect(lambda: updateDropdownIndex(self.camera, self.camera_connection.dropdown.currentData()))

    #     self.lighting_control = PortControl("Lighting: ")
    #     self.lighting_control.connect_btn.clicked.connect(lambda: self.lightConnection(True))
    #     self.lighting_control.disconnect_btn.clicked.connect(lambda: self.lightConnection(False))
    #     self.lighting_control.update_btn.clicked.connect(lambda: self.lighting_control.updatePorts(self.light_connection))
    #     self.lighting_control.dropdown.currentIndexChanged.connect(lambda: updateDropdownIndex(self.light_connection, self.lighting_control.dropdown.currentData()))
        
    #     # Lighting dropdown
    #     self.lighting = LightingDropdown()
    #     self.lighting.slider.valueChanged.connect(lambda: setBrightness(self.lighting, self.light_connection))

    #     # Save photo
    #     self.save_photo = QPushButton("Take Photo and Unwarp", objectName="dark_blue")
    #     self.save_photo.clicked.connect(lambda: self.onbtnclicked(self.result, show_result))
    #     self.save_photo.setEnabled(False)

    #     widgets.append(self.camera_connection)
    #     widgets.append(self.lighting_control)
    #     widgets.append(self.lighting)
    #     widgets.append(self.save_photo)

    #     layout_col = addAllWidgets(layout_col, widgets)
    #     control_col.setLayout(layout_col)

    #     layout.addWidget(self.feed, 0, 0, 1, 3, alignment=Qt.AlignLeft)
    #     layout.addWidget(self.result, 0, 0, 1, 3, alignment=Qt.AlignLeft)
    #     layout.addWidget(control_col, 0, 2)
    #     layout.addWidget(show_cam, 1, 0)
    #     layout.addWidget(show_result, 1, 1)

    #     self.setLayout(layout)

        
    
    # def handleCam(self, type):
    #     if type == "cam":
    #         self.feed.show()
    #         self.result.hide()
    #     elif type == "result":
    #         self.feed.hide()
    #         self.result.show()

    # def onbtnclicked(self, result, show_result):
    #     # open json file unless there's an error
    #     try:
    #         with open(self.json_path["json"], encoding="utf-8") as fh:
    #             params = json.load(fh)         # a Python dict
    #     except FileNotFoundError:
    #         print(f"Cannot find JSON file: {self.json_path['json']}")
    #         return
    #     except json.JSONDecodeError as err:
    #         print(f"JSON syntax error: {err}")
            
    #     # Get unwarping variables specifically
    #     params = params["checkerboard"][0]

    #     # get image from the camera and unwarp it
    #     img = self.camera.frame.copy()
    #     img = unwarpPhoto(img,params)
    #     self.resultAvailable.emit(img)

    #     #display image
    #     rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     h, w, ch = rgb_image.shape
    #     bytes_per_line = ch * w
    #     q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #     scaled = q_img.scaled(result.feed_width, result.feed_height, Qt.KeepAspectRatio)
    #     result.image_label.setPixmap(QPixmap.fromImage(scaled))
    #     show_result.setEnabled(True)

    # def camConnection(self, connected):
    #     if connected:
    #         if not self.camera.running:
    #             try:
    #                 self.camera.start()
    #             except:
    #                 pass
            
    #         if self.camera.running and self.camera.capture.isOpened():
    #             self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))
    #             self.save_photo.setEnabled(True)
        
    #     elif not connected:
    #         if self.camera.running:
    #             self.camera.stop()
        
    #         self.camera_connection.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))
    #         self.save_photo.setEnabled(False)

    
    # def lightConnection(self, connected):
    #     if connected:
    #         if not self.light_connection.running:
    #             try:
    #                 self.light_connection.start()
    #             except:
    #                 pass
        
    #         if self.light_connection.running:
    #             self.lighting_control.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))
    
    #     elif not connected:
    #         if self.light_connection.running:
    #             self.light_connection.stop()
            
    #         self.lighting_control.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))
