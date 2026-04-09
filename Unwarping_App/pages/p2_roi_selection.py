from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

import cv2
import json

from Unwarping_App.components.common import LightingDropdown, PortControl, CamFeed, ClickableImage
from Unwarping_App.components.utils import addAllWidgets, updateFrame, setBrightness, updateDropdownIndex, unwarpPhoto

from Unwarping_App.services import sampling_service

class ROISelection(QWidget):
    next = pyqtSignal()
    resultAvailable = pyqtSignal(object)
    clearSignal = pyqtSignal()

    def __init__(self, transformation, sampling):
        super().__init__()
        self.transformation = transformation
        self.sampling = sampling

        self.initUI()
    

    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling,"r") as file:
            self.setStyleSheet(file.read())

        layout = QHBoxLayout(self)

        self.photo = ClickableImage()

        # RIGHT COLUMN --------------------------------------
        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_selectArea = QLabel("Select sampling area", objectName="page_title")

        self.referencePoint = ReferencePointSection()
        
        self.ROI = DrawROISection()    

        button_clear = QPushButton("Clear all", objectName="red")

        self.button_next = QPushButton("Next", objectName="blue")
        self.button_next.setEnabled(False)

        layout_right.addStretch()
        layout_right.addWidget(label_selectArea)
        layout_right.addWidget(self.referencePoint)
        layout_right.addWidget(self.ROI)
        layout_right.addWidget(button_clear, alignment=Qt.AlignLeft)
        layout_right.addStretch()
        layout_right.addWidget(self.button_next, alignment=Qt.AlignRight)
        layout_right.addStretch()

        layout_right.setContentsMargins(0,0,0,0)
        layout_right.setSpacing(15)

        
        # COMPOSE --------------------------------------
        layout.addWidget(self.photo)
        layout.addWidget(right, alignment=Qt.AlignCenter)
        
        layout.setContentsMargins(0, 0, 0, 0) 


        self.ROI.setFixedWidth(self.ROI.sizeHint().width())
        self.referencePoint.setFixedWidth(self.ROI.width())
        

        
        # FUNCTIONS --------------------------------------
        self.referencePoint.button_action.clicked.connect(lambda: self.setReference())

        self.ROI.button_draw.clicked.connect(lambda: self.ROIMode("Draw"))
        self.ROI.button_rectangle.clicked.connect(lambda: self.ROIMode("Rectangle"))

        # button_clear.clicked.connect(lambda: self.clearDrawing(self.photo))
        button_clear.clicked.connect(lambda: self.resetAll())

        self.button_next.clicked.connect(self.next.emit)
        self.button_next.clicked.connect(lambda: sampling_service.findLocations(self.transformation, self.sampling, self.photo))

        self.ROI.button_pencil.clicked.connect(lambda: self.setDrawTool("pencil"))
        self.ROI.button_eraser.clicked.connect(lambda: self.setDrawTool("eraser"))

        self.ROI.button_convert.clicked.connect(self.photo.convertToPolygon)
        self.ROI.button_reset.clicked.connect(self.photo.resetROI)
        self.photo.roiSignal.connect(lambda _: self.checkAllowNext())

        self.checkAllowNext()




    def _reference_point_complete(self):
        # making sure user left select mode
        return (
            self.photo.dot is not None
            and self.referencePoint.button_action.text() == "Select"
        )


    def _roi_defined(self):
        # user has defined a region of interest
        img = self.photo
        if img.rectangle is not None:
            return True
        if getattr(img, "polygon_active", False) and img.polygon_points:
            return True
        return False


    def _next_enabled(self):
        return self._reference_point_complete() and self._roi_defined()


    def _refresh_next_button(self):
        self.button_next.setEnabled(self._next_enabled())


    def _on_convert_to_polygon(self):
        self.photo.convertToPolygon()
        self._refresh_next_button()


    def _on_reset_roi(self):
        self.photo.resetROI()
        self._refresh_next_button()


    def _on_next_clicked(self):
        if not self._next_enabled():
            return
        self.next.emit()
        sampling_service.findLocations(self.transformation, self.sampling, self.photo)



    # Function to handle setting a reference point
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

        self._refresh_next_button()

    

    ''' Function to set the active draw tool (pencil or eraser) '''
    def setDrawTool(self, tool):
        self.photo.draw_mode = tool
        # Keep buttons in sync as a toggle pair
        self.ROI.button_pencil.setChecked(tool == "pencil")
        self.ROI.button_eraser.setChecked(tool == "eraser")

    # Function to handle when user selects a drawing type
    def ROIMode(self, type=None):
        self.photo.type = None

        # Handle rectangle selections
        if type == "Rectangle":
            self.ROI.row_2.hide()
            self.ROI.row_3.hide()
            self.ROI.row_4.hide()
            self.ROI.row_5.hide()

            self.photo.type = "Rectangle"
            self.photo.draw_mode = None
            # Clear any draw/polygon history when switching to Rectangle
            self.photo.draw_strokes = []
            self.photo.current_stroke = []
            self.photo.roi_closed = False
            self.photo.polygon_points = []
            self.photo.polygon_active = False
            self.photo.update()

        # Handle hand-drawn selections
        elif type == "Draw":
            self.ROI.row_2.show()
            self.ROI.row_3.show()
            self.ROI.row_4.show()
            self.ROI.row_5.show()

            self.photo.type = "Draw"
            # Clear any rectangle when switching to Draw
            self.photo.rectangle = None
            # Default to pencil when entering draw mode
            self.photo.draw_mode = "pencil"
            self.ROI.button_pencil.setChecked(True)
            self.ROI.button_eraser.setChecked(False)
            self.photo.update()

        self.checkAllowNext()

    # Enable Next only when a sampling region exists.
    def checkAllowNext(self):
        rectangle = self.photo.rectangle
        has_rectangle = bool(rectangle and rectangle.width() > 0 and rectangle.height() > 0)

        polygon_points = getattr(self.photo, "polygon_points", [])
        polygon_active = getattr(self.photo, "polygon_active", False)
        has_polygon = bool(polygon_active and len(polygon_points) >= 3)

        self.button_next.setEnabled(has_rectangle or has_polygon)

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
        self.ROI.row_4.hide()
        self.ROI.row_5.hide()

        self.checkAllowNext()
        self.clearSignal.emit()

        self.button_next.setEnabled(False)

    
    def clearDrawing(self, img):
        img.rectangle = None
        img.dot = None

        img.sample_overlay_x = None
        img.sample_overlay_y = None

        img.resetROI()

        # Reset buttons, user needs to select reference point again
        self.ROI.button_draw.setEnabled(False)
        self.ROI.button_rectangle.setEnabled(False)
        self.ROI.row_2.hide()
        self.ROI.row_3.hide()
        self.ROI.row_4.hide()
        self.ROI.row_5.hide()

        self.referencePoint.button_action.setText("Select")

        self.ROIMode()
        self.checkAllowNext()
        self.clearSignal.emit()
        self._refresh_next_button()


class ReferencePointSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QHBoxLayout(container)

        icon_number = QLabel("1) ")
        icon_number.setStyleSheet("""
            color: #10164D;
            font-weight: bold;
        """)

        label_title = QLabel("Reference Point", objectName="larger")
        label_title.setStyleSheet("font-weight: bold;")

        self.button_action = QPushButton("Select", objectName="blue")

        layout_container.addWidget(icon_number, alignment=Qt.AlignLeft)
        layout_container.addWidget(label_title, alignment=Qt.AlignLeft)
        layout_container.addStretch()
        layout_container.addWidget(self.button_action)

        layout.addWidget(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.setStyleSheet("""
            QWidget#light_blue_box, QLabel { background-color: #C8D3F1; }
        """)


class DrawROISection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)

        # ROW 1 --------------------------------------
        row_1 = QWidget()
        layout_row_1 = QHBoxLayout(row_1)

        icon_number = QLabel("2) ")
        icon_number.setStyleSheet("""
            color: #10164D;
            font-weight: bold;
        """)

        label_selection = QLabel("Sampling Region", objectName="larger")
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

        layout_row_1.setContentsMargins(0,0,0,0)


        # ROW 2 - pencil / eraser tools
        self.row_2 = QWidget()
        layout_row_2 = QHBoxLayout(self.row_2)

        self.button_pencil = QPushButton("✏  Pencil", objectName="blue")
        self.button_pencil.setCheckable(True)
        self.button_pencil.setChecked(True)

        self.button_eraser = QPushButton("◯  Eraser", objectName="clear")
        self.button_eraser.setCheckable(True)

        layout_row_2.addWidget(self.button_pencil)
        layout_row_2.addWidget(self.button_eraser)

        layout_row_2.setContentsMargins(0,0,0,0)


        # ROW 3 - convert / reset + instructions
        self.row_3 = QWidget()
        layout_row_3 = QHBoxLayout(self.row_3)

        label_instructions = QLabel("Draw an enclosed shape to continue")

        layout_row_3.addWidget(label_instructions, alignment=Qt.AlignCenter)
        layout_row_3.setContentsMargins(0,10,0,0)

        # ROW 4 - Convert button
        self.row_4 = QWidget()
        layout_row_4 = QHBoxLayout(self.row_4)

        self.button_convert = QPushButton("⬡  Convert to Polygon", objectName="headerBlue")

        layout_row_4.addWidget(self.button_convert)
        layout_row_4.setContentsMargins(0,0,0,0)

        # ROW 5 - Reset button
        self.row_5 = QWidget()
        layout_row_5 = QHBoxLayout(self.row_5)

        self.button_reset = QPushButton("Reset", objectName="clear")
        
        layout_row_5.addWidget(self.button_reset)
        layout_row_5.setContentsMargins(0,0,0,0)


        # COMPOSE --------------------------------------
        layout_container.addWidget(row_1, alignment=Qt.AlignLeft)
        layout_container.addWidget(self.row_2)
        layout_container.addStretch()
        layout_container.addWidget(self.row_3)
        layout_container.addWidget(self.row_4)
        layout_container.addWidget(self.row_5)

        layout.addWidget(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QPushButton#blue { background-color: #2A54F6; }
            QPushButton#clear { background-color: #F0F0F0; }
            QPushButton#headerBlue { background-color: #132C49; }
        """)

        # INITIALIZATION --------------------------------------
        self.button_draw.setEnabled(False)
        self.button_rectangle.setEnabled(False)
        self.row_2.hide()
        self.row_3.hide()
        self.row_4.hide()
        self.row_5.hide()


