from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QGridLayout, 
    QHBoxLayout, QPushButton, QSizePolicy, QToolButton,
    QScrollArea, QComboBox, QSlider, QVBoxLayout,
    QLineEdit, QGraphicsDropShadowEffect, QCheckBox, QStyle, QApplication
)


from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QIcon, QPixmap, QImage, QPolygon, QFont, QDoubleValidator, QPolygonF
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect, QPoint, QSize, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
from PyQt5 import QtSvg

from PyQt5.QtMultimedia import QCameraInfo
from serial.tools import list_ports

import cv2
import numpy as np

from Unwarping_App.components import utils

from Unwarping_App.services import device_service
from Unwarping_App.services import calibration_service

class IconButton(QPushButton):
    def __init__(self, text, icon_path, parent=None):
        super().__init__(parent)

        self.setFixedWidth(115)

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(
            20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

        text_label = QLabel(text)

        if text=="Refresh":
            self.setObjectName("blue")
            icon_label.setStyleSheet("background-color: transparent;")
            text_label.setStyleSheet("""
                background-color: transparent;
                color: white;
                font-weight: bold;
            """)
        else:
            self.setObjectName("headerBlue")
            icon_label.setStyleSheet("background-color: #132C49;")
            text_label.setStyleSheet("""
                background-color: #132C49;
                color: white;
                font-weight: bold;
            """)



        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addStretch()
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(text_label, alignment=Qt.AlignCenter)
        layout.addStretch()

# Devices Dropdown ############################################################################################

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setTristate(False)
        self.setFixedSize(60, 25)  # wide enough for text

        # We paint our own text+knob in paintEvent; indicator provides the pill background
        self.setStyleSheet("""
            QCheckBox { spacing: 0px; }
            QCheckBox::indicator {
                width: 60px;
                height: 25px;
                border-radius: 12px;
                background: #132C49;            /* Connect (blue) */
            }
            QCheckBox::indicator:checked {
                background: #A83232;            /* Disconnect (red) */
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w, h = self.width(), self.height()
        margin = 6
        knob_d = h - 2 * margin
        knob_x = (w - margin - knob_d) if self.isChecked() else margin

        # # label text
        # p.setPen(QColor("white"))
        # font = self.font()
        # font.setWeight(QFont.DemiBold)
        # font.setPointSize(10)  
        # p.setFont(font)
        # text = "Disconnect" if self.isChecked() else "Connect"
        # p.drawText(QRect(0, 0, w, h), Qt.AlignCenter, text)

        # knob
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#F2F2F2"))
        p.drawEllipse(knob_x, margin, knob_d, knob_d)
        p.end()


def _make_status_pixmap(kind: str, size=24) -> QPixmap:
    """
    kind: "connected" (blue check circle) or "disconnected" (red warning triangle)
    """
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)

    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)

    if kind == "connected":
        # blue circle
        p.setBrush(QColor("#0A5CC2"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, size, size)

        # white check
        pen = QPen(QColor("white"))
        pen.setWidth(max(3, size // 9))
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(int(size*0.28), int(size*0.55), int(size*0.43), int(size*0.70))
        p.drawLine(int(size*0.43), int(size*0.70), int(size*0.74), int(size*0.34))

    else:
        # red triangle
        p.setBrush(QColor("#E30000"))
        p.setPen(Qt.NoPen)
        poly = QPolygon([
            QPoint(int(size*0.50), int(size*0.05)),
            QPoint(int(size*0.95), int(size*0.92)),
            QPoint(int(size*0.05), int(size*0.92))
        ])
        p.drawPolygon(poly)

        # white exclamation
        p.setBrush(QColor("white"))
        p.drawRoundedRect(int(size*0.46), int(size*0.30), int(size*0.08), int(size*0.38), 2, 2)
        p.drawEllipse(int(size*0.46), int(size*0.73), int(size*0.08), int(size*0.08))

    p.end()
    return pm

class DeviceRow(QWidget):
    """
    Row layout:
      [status icon] [name] [optional eye] [port dropdown] [toggle switch]
    """
    def __init__(self, name: str, kind: str, include_eye=False, parent=None):
        super().__init__(parent)
        self.kind = kind  # used to decide how to populate ports
        self.include_eye = include_eye

        row = QHBoxLayout(self)
        row.setContentsMargins(28, 16, 28, 16)
        row.setSpacing(18)

        # status icon
        self.status_lbl = QLabel()
        self.status_lbl.setFixedSize(22, 22)
        self.status_lbl.setAlignment(Qt.AlignCenter)

        # name
        self.name_lbl = QLabel(name)
        f = self.name_lbl.font()
        f.setPointSize(11)
        f.setBold(True)
        self.name_lbl.setFont(f)

        # optional eye button
        self.eye_btn = None
        if include_eye:
            self.eye_btn = QToolButton()
            self.eye_btn.setCursor(Qt.PointingHandCursor)
            self.eye_btn.setFixedSize(30, 30)
            # Use a standard icon (no assets). Replace with your own svg if desired.
            self.eye_btn.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
            self.eye_btn.setIconSize(QSize(20, 20))
            self.eye_btn.setStyleSheet("""
                QToolButton {
                    background: #132C49;
                    border-radius: 12px;
                }
                QToolButton:hover { background: #173556; }
            """)
            self.eye_btn.clicked.connect(lambda: None)

        # port dropdown
        self.port_combo = QComboBox()
        self.port_combo.setFixedWidth(200)
        self.port_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: none;
                border-radius: 12px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QComboBox::drop-down { border: 0px; width: 26px; }
            QComboBox::disabled { background-color: #C0C0C0; }
        """)

        # toggle
        self.toggle = ToggleSwitch()

        # spacer to push right controls
        row.addWidget(self.status_lbl)
        row.addWidget(self.name_lbl)
        row.addStretch(1)
        if self.eye_btn:
            row.addWidget(self.eye_btn)
        row.addWidget(self.port_combo)
        row.addWidget(self.toggle)

        # initial state
        start_connected = False
        self.set_connected(start_connected)

        # connect toggle -> update icon
        # self.toggle.stateChanged.connect(lambda _: self.set_connected(self.toggle.isChecked()))

        self.populate_ports()

    def set_connected(self, connected: bool):
        # self.toggle.setChecked(connected)
        pm = _make_status_pixmap("connected" if connected else "disconnected", size=24)
        self.status_lbl.setPixmap(pm)

    def populate_ports(self):
        previous_data = self.port_combo.currentData()


        self.port_combo.clear()
        self.port_combo.addItem("Select port...")

        if self.kind == "camera":
            cams = QCameraInfo.availableCameras()
            if not cams:
                self.port_combo.addItem("No cameras found")
                self.port_combo.setEnabled(False)
                return
            self.port_combo.setEnabled(True)
            for idx, cam in enumerate(cams):
                # description is usually the friendly name
                self.port_combo.addItem(cam.description(), idx)

        else:
            ports = list(list_ports.comports())
            if not ports:
                self.port_combo.addItem("No ports found")
                self.port_combo.setEnabled(False)
                return
            self.port_combo.setEnabled(True)
            for p in ports:
                # show "COM3 — USB Serial Device" style label
                dev = getattr(p, "device", str(p).split(" - ")[0])
                desc = getattr(p, "description", "")
                label = f"{dev} — {desc}" if desc else dev
                self.port_combo.addItem(label, dev)

        if previous_data is not None:
            index = self.port_combo.findData(previous_data)
            if index != -1:
                self.port_combo.setEnabled(False) if self.toggle.isChecked() else self.port_combo.setEnabled(True)
                self.port_combo.setCurrentIndex(index)
            else:
                self.set_connected(False)
                self.toggle.setChecked(False)




class DevicesDropdown(QWidget):
    def __init__(self, parent=None, camera=None, light_thread=None):
        super().__init__(parent)

        self.camera = camera
        self.lights = light_thread

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.setFixedHeight(200)
        self.setObjectName("devicesDropdown")

        self.setStyleSheet("""
            #devicesDropdown {
                background: transparent;   
            }
            #devicesDropdownInner {
                background-color: #F0F0F0;
                border-radius: 14px;
                border: none;
            }
        """)

        # Outer layout gives breathing room for shadow
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(0)

        inner = QWidget(self, objectName="devicesDropdownInner")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 80))
        inner.setGraphicsEffect(shadow)

        # Inner layout holds rows
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        refresh_btn = IconButton("Refresh", "Unwarping_App/components/images/refresh.svg")

        # 4 rows
        self.row_camera = DeviceRow("Camera", kind="camera")
        self.row_printer = DeviceRow("3D Printer", kind="printer")
        self.row_cond = DeviceRow("Conductance", kind="conductance")
        self.row_lights = DeviceRow("Lights", kind="lights")
        
        inner_layout.addWidget(self.row_camera)
        # inner_layout.addWidget(self.row_printer)
        # inner_layout.addWidget(self.row_cond)
        inner_layout.addWidget(self.row_lights)
        inner_layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)
        inner_layout.addStretch(1)

        outer.addWidget(inner)
        self.setLayout(outer)


        # Function calls
        self.row_camera.toggle.stateChanged.connect(lambda: device_service.toggle(self.row_camera, self.camera))
        self.row_lights.toggle.stateChanged.connect(lambda: device_service.toggle(self.row_lights, self.lights))

        refresh_btn.clicked.connect(lambda: self.update_ports())

    def update_ports(self):
        # Update ports for all rows
        self.row_camera.populate_ports()
        self.row_printer.populate_ports()
        self.row_cond.populate_ports()
        self.row_lights.populate_ports()

######### End of Devices Dropdown #######################################################################################


class Header(QWidget):
    def __init__(self, stacked_widget, camera, lights):
        super().__init__()

        layout = QHBoxLayout()

        container = QWidget(objectName="header")
        inner_layout = QHBoxLayout(container)

        self.stacked = stacked_widget
        self.camera = camera
        self.lights = lights

        self.legacy_btn = QPushButton("Legacy Mode", objectName="headerGrey")
        self.return_btn = QPushButton("Return", objectName="headerGrey")
        self.return_btn.hide()

        credits_btn = QPushButton("Credits", objectName="headerBlue")
        help_btn = QPushButton("Help", objectName="headerBlue")

        self.devices_btn = IconButton("Devices", "Unwarping_App/components/images/Gear.svg")
        self.devices_btn.clicked.connect(self.showDevicesDropdown)
        self.devices_dropdown = None

        self.legacy_btn.clicked.connect(self.showMonitor)
        self.return_btn.clicked.connect(self.showUnwarping)

        inner_layout.addWidget(self.legacy_btn)
        inner_layout.addWidget(self.return_btn)
        inner_layout.addStretch()
        # inner_layout.addWidget(credits_btn)
        # inner_layout.addWidget(help_btn)
        inner_layout.addWidget(self.devices_btn)

        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

    def showDevicesDropdown(self):
        if self.devices_dropdown is None:
            self.devices_dropdown = DevicesDropdown(self, self.camera, self.lights)
        
        button_pos = self.devices_btn.mapToGlobal(QPoint((self.devices_btn.width() - self.devices_dropdown.sizeHint().width()), self.devices_btn.height()))
        self.devices_dropdown.move(button_pos)
        self.devices_dropdown.show()
        self.devices_dropdown.raise_() 

    def showMonitor(self):
        self.stacked.setCurrentIndex(1)
        self.legacy_btn.hide()
        self.return_btn.show()

    def showUnwarping(self):
        self.stacked.setCurrentIndex(0)
        self.legacy_btn.show()
        self.return_btn.hide()


# ----------- NAV BAR COMPONENT ------------

class NavBar(QWidget):
    def __init__(self, stacked):
        super().__init__()

        self.exit_button = QPushButton("Exit", objectName="red")
        self.steps = Steps()
        self.stacked = stacked

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.exit_button)
        layout.addStretch()
        layout.addWidget(self.steps)
        layout.addStretch()

        # Functions
        self.exit_button.clicked.connect(self.handleExit)

    # Return to landing page
    def handleExit(self):
        self.stacked.setCurrentIndex(0)

# Numbered steps for Nav Bar
class Steps(QWidget):
    stepClicked = pyqtSignal(int)

    def __init__(self, steps=3, filled=1):
        super().__init__()

        self.steps = steps
        self.filledSteps = filled
        self.areas = []

        self.setMinimumHeight(60)
        self.setMinimumWidth(300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMouseTracking(True)

    # Function to render progress bar
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        center_y = h // 2

        radius = 18

        if self.steps > 1:
            spacing = (w - 2 * radius) // (self.steps - 1)
        else:
            spacing = 0

        line_color = QColor("#132c49")
        fill_color = QColor("#132c49")
        empty_color = QColor("white")

        painter.setPen(QPen(line_color, 3))
        painter.drawLine(radius, center_y, w - radius, center_y)

        font = QFont()
        font.setBold(True)
        painter.setFont(font)

        self.areas.clear()

        # Draw steps
        for i in range(self.steps):
            x = radius + i * spacing
            step_number = i + 1

            circle = QRect(
                x - radius,
                center_y - radius,
                2 * radius,
                2 * radius
            )
            self.areas.append((step_number, circle))

            # Colour in filled steps (default = 1)
            if step_number <= self.filledSteps:
                painter.setBrush(QBrush(fill_color))
                painter.setPen(Qt.NoPen)
                text_color = Qt.white
            else:
                painter.setBrush(QBrush(empty_color))
                painter.setPen(QPen(fill_color, 3))
                text_color = Qt.black

            painter.drawEllipse(circle)
            painter.setPen(text_color)
            painter.drawText(circle, Qt.AlignCenter, str(step_number))


    # Update which steps are filled according to the workflow
    def updateSteps(self, index):
        if index in [3, 4, 5, 8]:
            self.filledSteps = 3
        elif index == 2 or index == 7:
            self.filledSteps = 2
        else:
            self.filledSteps = 1

        self.update()

    # Handle user clicks on filled steps
    def mousePressEvent(self, event):
        for step_number, circle in self.areas:
            if circle.contains(event.pos()) and step_number <= self.filledSteps:
                self.stepClicked.emit(step_number)
                return
            
    # Handle user cursor 
    def mouseMoveEvent(self, event):
        # Show a pointing hand cursor if hovering over a clickable step
        for step_number, circle in self.areas:
            if circle.contains(event.pos()) and step_number <= self.filledSteps:
                self.setCursor(Qt.PointingHandCursor)
                return

        # Show the default cursor if step is not filled
        self.setCursor(Qt.ArrowCursor)

# ----------- END OF NAV BAR COMPONENT ------------
        
class FolderSelect(QWidget):
    def __init__(self):
        super().__init__()

        self.container = QWidget(objectName="light_blue_box")
        container_layout = QHBoxLayout()

        self.upload = QPushButton("Select folder", objectName="blue")
        self.path = QLabel("", objectName="path_label")
        self.path.setFixedWidth(300)

        container_layout.addWidget(self.upload, alignment=Qt.AlignLeft)
        container_layout.addWidget(self.path, alignment=Qt.AlignLeft)

        self.container.setLayout(container_layout)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.container, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

class CheckItem(QWidget):
    def __init__(self, title):
        super().__init__()

        # icon here... needs to be check or x
        self.icon = QPushButton()
        self.icon.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))

        self.title = QLabel(title, objectName="larger")
        self.status = QLabel("lalala", objectName="light_blue_box")
        self.status.setFixedWidth(300)

        self.layout = QGridLayout()
        self.layout.addWidget(self.icon, 0, 0, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.title, 0, 1, alignment=Qt.AlignRight)
        self.layout.addWidget(self.status, 0, 2)

        self.setLayout(self.layout)

class NewTransformationItem(QWidget):
    def __init__(self, title, i, width):
        super().__init__()
        max_width = int(width * 0.6)

        # Number icon
        self.step = QPushButton()
        self.step.setIcon(QIcon("Unwarping_App/components/images/circle_{}.svg".format(str(i))))

        # Step title
        self.title = QLabel(title, objectName="larger")

        if title != "Offset":
            self.action = QPushButton("Capture", objectName="blue")
            self.upload = QPushButton("Upload", objectName="clear")

            # Path for image folder 
            self.container = QWidget(objectName="light_blue_box")
            self.path = QLabel("", objectName="path_label")
            self.path.setFixedWidth(max_width - 30)
            
            container_layout = QHBoxLayout()
            container_layout.addWidget(self.path, alignment=Qt.AlignLeft)
            self.container.setLayout(container_layout)

        else:
            # Button for offset
            self.action = QPushButton("Calculate", objectName="blue")
            self.upload = QLabel("")
            self.container = QLabel("", objectName="light_blue_box")
        
        self.container.setFixedWidth(350)

        # Check icon
        self.check = QPushButton()
        self.check.setIcon(QIcon("Unwarping_App/components/images/checkmark.svg"))

        self.step.setFixedSize(50, 50)  # Step icon
        self.title.setFixedWidth(150)  # Title
        
        if title == "Offset":
            self.action.setFixedSize(210, 35) # Accept button
        else: 
            self.action.setFixedSize(100, 35) # Capture button
            self.upload.setFixedSize(100, 35) # Upload button
        
        
        self.container.setFixedSize(max_width, 45)  # Container
        self.check.setFixedSize(50, 50) # Check icon

        # Set fixed size policy
        self.container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.upload.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.check.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.layout = QGridLayout()
        self.layout.addWidget(self.step, 0, 0, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.title, 0, 1, alignment=Qt.AlignLeft)
        
        if title == "Offset":
            self.layout.addWidget(self.action, 0, 2, 0, 2, alignment=Qt.AlignLeft)
        else:
            self.layout.addWidget(self.action, 0, 2, alignment=Qt.AlignLeft)
            self.layout.addWidget(self.upload, 0, 3, alignment=Qt.AlignLeft)
        
        self.layout.addWidget(self.container, 0, 4, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.check, 0, 5, alignment=Qt.AlignLeft)

        self.setLayout(self.layout)

class PortControl(QWidget):
    def __init__(self, title):
        super().__init__()

        self.icon = QPushButton()
        self.icon.setIcon(QIcon("Unwarping_App/components/images/red_x.svg"))
        self.icon.setFlat(True) 
        self.icon.setIconSize(QSize(36, 36))    
        self.icon.setFixedSize(50, 50)  

        self.title = QLabel(title, objectName="extrinsiccontrollabel")

        self.connect_btn = QPushButton("Connect", objectName="blue")
        self.disconnect_btn = QPushButton("Disconnect", objectName="clear")
        self.update_btn = QPushButton("Update", objectName="clear")

        self.dropdown = QComboBox(objectName="port")

        # Fill dropdown with appropriate port connections
        if title == "Lighting: ":
            # get all available COM ports
            ports = list(list_ports.comports())
            extracted_ports = [str(port).split(' - ')[0] for port in ports]
            extracted_names = [str(port).split(' - ')[1] for port in ports]

            for i, port in enumerate(extracted_ports):
                self.dropdown.addItem("", port)
                self.dropdown.setItemText(i, extracted_names[i])
        elif title == "Camera: ":
            # get all available cameras
            cameras = QCameraInfo.availableCameras()
            for index, camera in enumerate(cameras):
                self.dropdown.addItem(str(index))
                self.dropdown.setItemData(index, index)

        self.layout = QGridLayout()

        # First row
        self.layout.addWidget(self.icon, 0, 0, 0,1)
        self.layout.addWidget(self.title, 0, 1, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.dropdown, 0, 2, 1, 2)

        # Second row
        self.layout.addWidget(self.connect_btn, 1, 1, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.disconnect_btn, 1, 2, alignment=Qt.AlignRight)
        self.layout.addWidget(self.update_btn, 1, 3)

        self.setLayout(self.layout)
    
    def updatePorts(self, item):
        if self.title.text() == "Camera: ":
            self.dropdown.clear()
            cameras = QCameraInfo.availableCameras()
            for index, camera in enumerate(cameras):
                self.dropdown.addItem(str(index))
                self.dropdown.setItemData(index, index)
            
            item.idx = 0 if len(cameras) > 0 else None

        elif self.title.text() == "Lighting: ":
            self.dropdown.clear()
             # get all available COM ports
            ports = list(list_ports.comports())
            extracted_ports = [str(port).split(' - ')[0] for port in ports]
            extracted_names = [str(port).split(' - ')[1] for port in ports]

            for i, port in enumerate(extracted_ports):
                self.dropdown.addItem("", port)
                self.dropdown.setItemText(i, extracted_names[i])
            
            item.idx = extracted_ports[0] if len(ports) > 0 else None


class LightingDropdown(QWidget):
    def __init__(self):
        super().__init__()

        # Put everything in one container
        self.container = QWidget(objectName="light_blue_box")
        self.container.setStyleSheet("QWidget { background-color: #C8D3F1; }")
        self.container.setFixedSize(350, 150)
        container_layout = QGridLayout()

        # Title
        title = QLabel("Lighting adjustment", objectName="larger")
        title.setStyleSheet("font-weight: bold;")

        # Toggle button to show/hide the slider
        self.toggle = QToolButton(objectName="toggle")
        self.toggle.setCheckable(True)
        self.toggle.setArrowType(Qt.UpArrow)
        self.toggle.clicked.connect(lambda: utils.controlToggle(self.toggle.isChecked(), self.toggle, self.lighting_control, self.container, 150)) 

        # specific container only for lighting adjustment stuff
        self.lighting_control = QWidget()
        light_layout = QGridLayout()

        # self.plus and self.minus buttons
        self.minus = QPushButton(" - ", objectName="increment")
        self.plus = QPushButton(text=" + ", objectName="increment")

        self.minus.setFixedSize(25, 25)
        self.plus.setFixedSize(25, 25)
        
        self.minus.setStyleSheet("background-color: #F0F0F0;")
        self.plus.setStyleSheet("background-color: #F0F0F0;")

        # List of self.increments to adjust lighting
        self.increments = QComboBox(objectName="increment_dropdown")
        self.increments.setStyleSheet("background-color: #F0F0F0;")
        self.increments_list = [1, 5, 10, 25]

        for i in self.increments_list:
            self.increments.addItem(str(i))

        # Set slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)


        # Labels for min/max values
        slider_min = QLabel("0")
        slider_max = QLabel("100")

        slider_min.setStyleSheet("font-weight: bold;")
        slider_max.setStyleSheet("font-weight: bold;")

        # Add all buttons to lighting control widget
        light_layout.addWidget(self.minus, 0, 2)
        light_layout.addWidget(self.plus, 0, 3)
        light_layout.addWidget(self.increments, 0, 4)
        light_layout.addWidget(self.slider, 1, 0, 1, 5)
        light_layout.addWidget(slider_min, 2, 0, alignment=Qt.AlignLeft)
        light_layout.addWidget(slider_max, 2, 4, alignment=Qt.AlignRight)

        self.lighting_control.setLayout(light_layout)

        # Add to overall container
        container_layout.addWidget(title, 0, 0, alignment=Qt.AlignLeft)
        container_layout.addWidget(self.toggle, 0, 1, alignment=Qt.AlignRight)
        container_layout.addWidget(self.lighting_control, 1, 0, 1, 2)

        self.container.setLayout(container_layout)

        # Show container
        layout_final = QHBoxLayout()
        layout_final.addWidget(self.container)

        layout_final.setContentsMargins(0, 0, 0, 0)
        layout_final.setSpacing(0)

        self.setLayout(layout_final)

        ''' Functions '''
        self.minus.clicked.connect(lambda: self.brightnessIncrement(self.increments.currentText(), "minus"))
        self.plus.clicked.connect(lambda: self.brightnessIncrement(self.increments.currentText(), "plus"))

    
    def brightnessIncrement(self, value, type):
        if type == 'plus':
            self.slider.setValue(self.slider.value() + int(value))
        else:
            self.slider.setValue(self.slider.value() - int(value))


# class ProbeDropdown(QWidget):
#     def __init__(self):
#         super().__init__()

#         # Put everything in one container
#         self.container = QWidget(objectName="light_blue_box")
#         self.container.setStyleSheet("QWidget { background-color: #C8D3F1; }")
#         self.container.setFixedSize(350, 150)
#         container_layout = QGridLayout()

#         # Title
#         title = QLabel("Corner locations", objectName="larger")
#         title.setStyleSheet("font-weight: bold;")

#         # Toggle button to show/hide input fields
#         self.toggle = QToolButton(objectName="toggle")
#         self.toggle.setCheckable(True)
#         self.toggle.setArrowType(Qt.UpArrow)
#         self.toggle.clicked.connect(lambda: utils.controlToggle(self.toggle.isChecked(), self.toggle, self.input_section, self.container, 150)) 

#         # specific container only for input sections
#         self.input_section = QWidget()
#         input_section_layout = QGridLayout()

#         # Bottom left corner
#         bottom_left_label = QLabel("Bottom-left corner: ( ")

#         self.bottom_left_X = QLineEdit()
#         self.bottom_left_Y = QLineEdit()

#         self.bottom_left_X.setPlaceholderText("X")
#         self.bottom_left_Y.setPlaceholderText("Y")

#         self.bottom_left_X.setStyleSheet("background-color: #F0F0F0;")
#         self.bottom_left_Y.setStyleSheet("background-color: #F0F0F0;")

#         # Top right corner
#         top_right_label = QLabel("Top-right corner:   ( ")

#         self.top_right_X = QLineEdit()
#         self.top_right_Y = QLineEdit()

#         self.top_right_X.setPlaceholderText("X")
#         self.top_right_Y.setPlaceholderText("Y")

#         self.top_right_X.setStyleSheet("background-color: #F0F0F0;")
#         self.top_right_Y.setStyleSheet("background-color: #F0F0F0;")

#         # Tag size input
#         tag_size_label = QLabel("Tag size (mm): ")
#         self.tag_size_input = QLineEdit()
#         self.tag_size_input.setStyleSheet("background-color: #F0F0F0;")

#         space = QLabel(" , ")
#         space2 = QLabel(" , ")
#         end = QLabel(" )")
#         end2 = QLabel(" )")

#         input_section_layout.addWidget(bottom_left_label, 0, 0)
#         input_section_layout.addWidget(self.bottom_left_X, 0, 1, alignment=Qt.AlignLeft)
#         input_section_layout.addWidget(space, 0, 2,alignment=Qt.AlignLeft)
#         input_section_layout.addWidget(self.bottom_left_Y, 0, 3, alignment=Qt.AlignLeft)
#         input_section_layout.addWidget(end, 0, 4, alignment=Qt.AlignLeft)

#         input_section_layout.addWidget(top_right_label, 1, 0)
#         input_section_layout.addWidget(self.top_right_X, 1, 1, alignment=Qt.AlignLeft)
#         input_section_layout.addWidget(space2, 1, 2, alignment=Qt.AlignLeft)
#         input_section_layout.addWidget(self.top_right_Y, 1, 3, alignment=Qt.AlignLeft)
#         input_section_layout.addWidget(end2, 1, 4,alignment=Qt.AlignLeft)

#         input_section_layout.addWidget(tag_size_label, 2, 0)
#         input_section_layout.addWidget(self.tag_size_input, 2, 1)

#         self.input_section.setLayout(input_section_layout)

#         # Add to overall container
#         container_layout.addWidget(title, 0, 0, alignment=Qt.AlignLeft)
#         container_layout.addWidget(self.toggle, 0, 1, alignment=Qt.AlignRight)
#         container_layout.addWidget(self.input_section, 1, 0, 1, 2)

#         self.container.setLayout(container_layout)

#         # Show container
#         layout_final = QHBoxLayout()
#         layout_final.addWidget(self.container)

#         self.setLayout(layout_final)
        
class CheckerboardDropdown(QWidget):
    def __init__(self):
        super().__init__()

        # Put everything in one container
        self.container = QWidget(objectName="light_blue_box")
        self.container.setStyleSheet("QWidget { background-color: #C8D3F1; }")
        # TODO erm more dynamic
        self.container.setFixedSize(350, 100)
        container_layout = QGridLayout()

        # Title
        title = QLabel("Board parameters", objectName="larger")
        title.setStyleSheet("font-weight: bold;")

        # Toggle button to show/hide the checkerboard parameters
        self.toggle = QToolButton(objectName="toggle")
        self.toggle.setCheckable(True)
        self.toggle.setArrowType(Qt.UpArrow)
        self.toggle.clicked.connect(lambda: utils.controlToggle(self.toggle.isChecked(), self.toggle, self.parameters, self.container, 100)) 

        # specific container only for parameters (also alignment view? but can be added later)
        self.parameters = QWidget()
        parameters_layout = QHBoxLayout()

        checkerboard_label = QLabel("Checkerboard size: (", objectName="larger")
        
        self.cols = QLineEdit()
        self.rows = QLineEdit()

        self.cols.setPlaceholderText("columns")
        self.rows.setPlaceholderText("rows")
        
        self.cols.setStyleSheet("background-color: #F0F0F0;")
        self.rows.setStyleSheet("background-color: #F0F0F0;")

        checkerboard_space = QLabel(" , ", objectName="larger")
        checkerboard_end = QLabel(")", objectName="larger")

        # add to parameters layout
        parameters_layout.addWidget(checkerboard_label, alignment=Qt.AlignLeft)
        parameters_layout.addWidget(self.cols, alignment=Qt.AlignLeft)
        parameters_layout.addWidget(checkerboard_space, alignment=Qt.AlignLeft)
        parameters_layout.addWidget(self.rows, alignment=Qt.AlignLeft)
        parameters_layout.addWidget(checkerboard_end, alignment=Qt.AlignLeft)

        # add layout to parameters section
        self.parameters.setLayout(parameters_layout)

        # Add to overall container
        container_layout.addWidget(title, 0, 0, alignment=Qt.AlignLeft)
        container_layout.addWidget(self.toggle, 0, 1, alignment=Qt.AlignRight)
        container_layout.addWidget(self.parameters, 1, 0, 1, 2, alignment=Qt.AlignLeft)

        self.container.setLayout(container_layout)

        # Show container
        layout_final = QHBoxLayout()
        layout_final.addWidget(self.container)

        self.setLayout(layout_final)
        
class CamFeed(QWidget):
    def __init__(self, text=None, scale=None):
        super().__init__()

        layout = QHBoxLayout(self)

        # dynamic size changing
        if scale:
            self.feed_width = int(1280 * scale)
            self.feed_height = int(720 * scale)
        else:
            self.feed_width = int(1280 * 0.7)
            self.feed_height = int(720 * 0.7)

        self.image_label = QLabel(objectName="camera_initial")
        self.image_label.setFixedSize(self.feed_width, self.feed_height)
        self.image_label.setText(text)

        self.image_label.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed
        )

        layout.addWidget(self.image_label)
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)   


class TagInformationSection(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)

        label_tagInformation = QLabel("Probe-to-Tag Information", objectName="larger")
        label_tagInformation.setStyleSheet("font-weight: bold;")

        self.label_msg = QLabel("An AprilTag must be clearly visible in the image.")

        ''' ROW 1 '''
        row_1 = QWidget()
        layout_row_1 = QHBoxLayout(row_1)

        label_bottomLeft = QLabel("Bottom-left corner")
        label_bottomLeft.setStyleSheet("font-weight: bold;")

        label_bottomLeftX = QLabel("X: ")
        self.input_bottomLeftX = QLineEdit()
        self.input_bottomLeftX.setValidator(QDoubleValidator())

        label_bottomLeftY = QLabel("Y: ")
        self.input_bottomLeftY = QLineEdit()
        self.input_bottomLeftY.setValidator(QDoubleValidator())

        self.button_autofill = QPushButton("Use current location", objectName="clear")

        layout_row_1.addWidget(label_bottomLeft, alignment=Qt.AlignLeft)
        layout_row_1.addStretch()
        layout_row_1.addWidget(label_bottomLeftX)
        layout_row_1.addWidget(self.input_bottomLeftX)
        layout_row_1.addWidget(label_bottomLeftY)
        layout_row_1.addWidget(self.input_bottomLeftY)

        layout_row_1.setContentsMargins(0,0,0,0)
        # layout_row_1.setSpacing(0)


        ''' ROW 2 '''
        row_2 = QWidget()
        layout_row_2 = QHBoxLayout(row_2)

        label_tagSize = QLabel("Tag size (mm): ")
        label_tagSize.setStyleSheet("font-weight: bold;")
        
        self.input_tagSize = QLineEdit()
        self.input_tagSize.setValidator(QDoubleValidator())

        layout_row_2.addWidget(label_tagSize)
        layout_row_2.addWidget(self.input_tagSize)

        layout_row_2.setContentsMargins(0,0,0,0)


        ''' COMPOSE '''
        layout_container.addWidget(label_tagInformation)
        layout_container.addWidget(self.label_msg)
        layout_container.addWidget(row_2)
        layout_container.addStretch()
        layout_container.addWidget(row_1)
        layout_container.addWidget(self.button_autofill)
        

        layout.addWidget(container)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

        self.setStyleSheet("""
            QWidget { background-color: #C8D3F1; }
            QLineEdit { background-color: white; }
            QPushButton#clear { background-color: #F0F0F0; }
        """)


    # Function to set the printer location in the X and Y inputs
    def setPrinterPos(self, printer):
        pos = device_service.getPrinterPosition(printer)

        if pos is not None:
            self.input_bottomLeftX.setText(str(pos[0]))
            self.input_bottomLeftY.setText(str(pos[1]))



class TagOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # default colours (grey)
        self.corner_colours = [
            QColor("#C5C5C5"),  # bottom right
            QColor("#C5C5C5"),  # bottom left
            QColor("#C5C5C5"),  # top left
            QColor("#C5C5C5"),  # top right
        ]

        self.setContentsMargins(0,0,0,0)

    # function to set corner colour based on action
    def set_colour(self, i, colour):
        self.corner_colours[i] = QColor(colour)
        self.update()
    
    def paintEvent(self, event):
        screen = QApplication.instance().primaryScreen()
        current_height = screen.size().height()

        base_screen_height = 1117
        scale = current_height / base_screen_height
        size = min(int(100 * scale), 100)

        self.setFixedSize(size, size)
        square_l = min(int(15 * scale), 15)
        square_r = min(int(75 * scale), 75)

        square = QRect(square_l, square_l, square_r, square_r)
        image = QPixmap("Unwarping_App/components/images/tag.svg") # set tag image as background
        image = image.scaled(square.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # set painter object
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(square, image)
        painter.drawRect(square)

        # make dot
        radius = 7
        diameter = radius * 2
        
        # set corners
        corners = [
            (square.right() - radius, square.bottom() - radius),
            (square.left() - radius, square.bottom() - radius),
            (square.left() - radius, square.top() - radius),
            (square.right() - radius, square.top() - radius),
        ]

        for i, (x, y) in enumerate(corners):
            painter.setBrush(QBrush(self.corner_colours[i]))
            painter.drawEllipse(x, y, diameter, diameter)

class ClickableImage(QLabel):
    roiSignal = pyqtSignal(object)

    # Overlay with unwarped image, else black screen
    def __init__(self):
        super().__init__()
        self.original_pixmap = None
        self.setStyleSheet("background-color: black;")
        
        self.type = None # None on default

        self.dot = None
        self.rectangle = None

        # probe rectange is a list of corners, dot is just one point
        self.probe_rectangle = []
        self.probe_dot = None
        self.real_points = []
        self.visited_points = []

        self.sample_overlay_x = None
        self.sample_overlay_y = None
        self.rowsOnly = False

        self.x_range = None
        self.y_range = None
        # self.sample_overlay = None

        # Positions + flag
        self.start_point = None
        self.end_point = None
        self.drawing = False


        # Scaling factor (for different monitor sizes)
        self.scale_val = self.compute_scale()

        self.feed_width = int(1280 * self.scale_val)
        self.feed_height = int(720 * self.scale_val)

        # Draw mode state
        self.draw_mode = None       # "pencil" or "eraser"
        self.draw_strokes = []      # list of completed strokes (each stroke = list of QPoint)
        self.current_stroke = []    # stroke currently being drawn
        self.cursor_pos = None      # cursor position for indicator
        self.roi_closed = False     # True after "Done" is clicked
        self.eraser_radius = 15
        self.polygon_points = []    # simplified polygon from convertToPolygon()
        self.polygon_active = False # True when polygon has been computed

        # Polygon grid state (populated by updateOverlayPolygon)
        self.probe_polygon = []            # [x0, y0, x1, y1] real-world bounding box
        self._polygon_valid_pixels = []    # pixel midpoints of cells inside polygon

        self.setFixedSize(self.feed_width, self.feed_height)
        self.setMouseTracking(True)


    # Function to handle scaling of image feed
    def compute_scale(self):
        screen = QApplication.instance().primaryScreen()
        available = screen.size().height()

        base_screen_height = 1117
        base_scale = 0.7

        scale = base_scale * (available / base_screen_height)
        scale = min(scale, base_scale)

        return scale


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.type == "Rectangle":
                self.start_point = event.pos() # grab start position
                self.drawing = True
            elif self.type == "Dot":
                self.dot = event.pos() # grab the (x, y) for the dot
                self.update()
            elif self.type == "Draw":
                if self.draw_mode == "pencil":
                    self.roi_closed = False
                    self.polygon_active = False
                    self.current_stroke = [event.pos()]
                    self.drawing = True
                elif self.draw_mode == "eraser":
                    self.drawing = True
                    self._eraseAt(event.pos())

    def mouseMoveEvent(self, event):
        # keep grabbing end point until user stops moving mouse
        if self.type == "Rectangle" and self.drawing:
            self.end_point = event.pos()
            self.sample_overlay_x = None
            self.sample_overlay_y = None
            self.update()
        elif self.type == "Draw":
            self.cursor_pos = event.pos()
            if self.drawing:
                if self.draw_mode == "pencil":
                    self.current_stroke.append(event.pos())
                elif self.draw_mode == "eraser":
                    self._eraseAt(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        # grab the (x, y) of the end point
        if event.button() == Qt.LeftButton and self.type == "Rectangle":
            self.end_point = event.pos()
            self.drawing = False
            # draw the entire rectangle
            self.rectangle = QRect(self.start_point, self.end_point).normalized()
            self.update()
        elif event.button() == Qt.LeftButton and self.type == "Draw":
            if self.draw_mode == "pencil" and self.current_stroke:
                self.draw_strokes.append(self.current_stroke)
                self.current_stroke = []
            self.drawing = False
            self.update()

    def leaveEvent(self, event):
        self.cursor_pos = None
        self.update()

    def _eraseAt(self, pos):
        r2 = self.eraser_radius ** 2
        new_strokes = []
        for stroke in self.draw_strokes:
            # Split stroke into segments at erased gaps
            segment = []
            for p in stroke:
                dx, dy = p.x() - pos.x(), p.y() - pos.y()
                if dx * dx + dy * dy > r2:
                    segment.append(p)
                else:
                    if len(segment) > 1:
                        new_strokes.append(segment)
                    segment = []
            if len(segment) > 1:
                new_strokes.append(segment)
        self.draw_strokes = new_strokes
        self.update()

    def closeROI(self):
        """Fill the drawn shape with a semi-transparent overlay."""
        self.roi_closed = True
        self.update()

    def resetROI(self):
        """Clear all drawn strokes, polygon, fill, and grid state."""
        self.draw_strokes = []
        self.current_stroke = []
        self.roi_closed = False
        self.polygon_points = []
        self.polygon_active = False
        self.probe_polygon = []
        self._polygon_valid_pixels = []
        self.sample_overlay_x = None
        self.sample_overlay_y = None
        
        self.update()

    def convertToPolygon(self):
        """Rasterize strokes → find contour → simplify to a polygon with approxPolyDP."""
        import numpy as np

        all_strokes = self.draw_strokes + (
            [self.current_stroke] if len(self.current_stroke) > 1 else []
        )
        if not any(len(s) > 1 for s in all_strokes):
            return

        # Rasterize strokes onto a binary mask
        mask = np.zeros((self.feed_height, self.feed_width), dtype=np.uint8)
        for stroke in all_strokes:
            if len(stroke) > 1:
                pts = np.array([[p.x(), p.y()] for p in stroke], dtype=np.int32)
                cv2.polylines(mask, [pts], isClosed=False, color=255, thickness=3)

        # Dilate to bridge small gaps between strokes
        kernel = np.ones((9, 9), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # Find the outermost contour
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return

        contour = max(contours, key=cv2.contourArea)

        # Simplify with Douglas-Peucker (0.3 % of perimeter — more points, finer shape)
        epsilon = 0.003 * cv2.arcLength(contour, closed=True)
        approx = cv2.approxPolyDP(contour, epsilon, closed=True)

        self.polygon_points = [QPoint(int(p[0][0]), int(p[0][1])) for p in approx]
        self.polygon_active = True
        self.roi_closed = False  # switch from simple fill to polygon fill
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        try:
            # Draw full rectangle
            if self.rectangle:
                painter.setPen(QPen(QColor("#BBFF00"), 3))
                painter.setOpacity(0.1) if self.rowsOnly else painter.setOpacity(1)
                painter.drawRect(self.rectangle)


            # If rectangle is still being drawn, update so the user sees
            if self.type == "Rectangle" and self.drawing and self.start_point and self.end_point:
                painter.setPen(QPen(QColor("#BBFF00"), 3, Qt.DashLine)) # looks cool
                painter.drawRect(QRect(self.start_point, self.end_point).normalized())

            # Draw dot
            if self.dot:
                painter.setPen(QPen(QColor("#16FFFF"), 4))
                painter.setOpacity(1.0)
                painter.drawPoint(self.dot)

            # Polygon overlay
            if (self.polygon_active and self.polygon_points and self.probe_polygon):

                # Rows
                if self.sample_overlay_y is not None and self.rowsOnly:
                    polygon = QPolygonF(self.polygon_points)

                    bx0, by0, bx1, by1 = self.probe_polygon
                    real_w = bx1 - bx0
                    real_h = by1 - by0

                    px_min = min(p.x() for p in self.polygon_points)
                    px_max = max(p.x() for p in self.polygon_points)
                    py_min = min(p.y() for p in self.polygon_points)
                    py_max = max(p.y() for p in self.polygon_points)

                    px_span = (px_max - px_min) or 1
                    py_span = (py_max - py_min) or 1

                    painter.setPen(QPen(QColor("#67FFD9"), 2))
                    painter.setOpacity(1.0)

                    row_pixels = []

                    # Draw rows
                    for val in self.y_range:
                        ty = (val - by0) / real_h
                        py = py_min + (1 - ty) * py_span

                        segments = self.get_row_segments(py)

                        row_pixels.append((val, py, segments))

                        for x0, x1 in segments:
                            painter.drawLine(int(x0), int(py), int(x1), int(py))

                    prev_point = None
                    rows = list(reversed(row_pixels))

                    # Serpentine direction
                    for row_idx, (y_val, py, segments) in enumerate(rows):

                        if not segments:
                            continue

                        # Flip direction every row
                        if row_idx % 2 == 0:
                            ordered_segments = segments
                        else:
                            ordered_segments = list(reversed(segments))

                        for seg_idx, (x_start, x_end) in enumerate(ordered_segments):

                            # Direction within segment
                            if row_idx % 2 == 0:
                                px_start, px_end = x_start, x_end
                            else:
                                px_start, px_end = x_end, x_start

                            # Draw horizontal line
                            painter.drawLine(int(px_start), int(py), int(px_end), int(py))

                            # Connect to previous segment
                            if prev_point is not None:
                                painter.drawLine(
                                    int(prev_point[0]), int(prev_point[1]),
                                    int(px_start), int(py)
                                )

                            # Convert point to real-world
                            tx_start = (px_start - px_min) / px_span
                            tx_end   = (px_end   - px_min) / px_span
                            ty       = (py - py_min) / py_span

                            real_y = by0 + (1 - ty) * real_h
                            real_x_start = bx0 + tx_start * real_w
                            real_x_end   = bx0 + tx_end   * real_w

                            loc1 = (round(real_x_start, 2), round(real_y, 2))
                            loc2 = (round(real_x_end, 2), round(real_y, 2))

                            # Get locations
                            if loc1 not in self.real_points:
                                self.real_points.append(loc1)
                            
                            if loc2 not in self.real_points:
                                self.real_points.append(loc2)

                            r = 6

                            # Check visited points
                            if loc1 in self.visited_points:
                                painter.setPen(Qt.NoPen)
                                painter.setBrush(QColor("#00FF00"))
                                painter.drawEllipse(int(px_start - r), int(py - r), r * 2, r * 2)

                            if loc2 in self.visited_points:
                                painter.setPen(Qt.NoPen)
                                painter.setBrush(QColor("#00FF00"))
                                painter.drawEllipse(int(px_end - r), int(py - r), r * 2, r * 2)

                            # Draw point if visited
                            if prev_point is not None:
                                prev_tx = (prev_point[0] - px_min) / px_span
                                prev_ty = (prev_point[1] - py_min) / py_span

                                prev_real_x = bx0 + prev_tx * real_w
                                prev_real_y = by0 + (1 - prev_ty) * real_h

                                prev_loc = (round(prev_real_x, 2), round(prev_real_y, 2))

                                if prev_loc in self.visited_points:
                                    painter.drawEllipse(
                                        int(prev_point[0] - r),
                                        int(prev_point[1] - r),
                                        r * 2, r * 2
                                    )

                            prev_point = (px_end, py)


                # Grid
                elif self.sample_overlay_x is not None and self.sample_overlay_y is not None and not self.rowsOnly:
                    bx0, by0, bx1, by1 = self.probe_polygon
                    real_w = bx1 - bx0
                    real_h = by1 - by0

                    px_min = min(p.x() for p in self.polygon_points)
                    px_max = max(p.x() for p in self.polygon_points)
                    py_min = min(p.y() for p in self.polygon_points)
                    py_max = max(p.y() for p in self.polygon_points)
                    px_span = (px_max - px_min) or 1
                    py_span = (py_max - py_min) or 1

                    # Grid lines over the bounding box (dim)
                    painter.setPen(QPen(QColor("#EAFFC2"), 1))
                    painter.setOpacity(0.25)

                    for val in self.x_range:
                        t = (val - bx0) / real_w
                        px = int(px_min + t * px_span)
                        painter.drawLine(px, py_min, px, py_max)

                    for val in self.y_range:
                        t = (val - by0) / real_h
                        py = int(py_min + (1 - t) * py_span)
                        painter.drawLine(px_min, py, px_max, py)

                    painter.setPen(QPen(QColor("#EAFFC2"), 3))
                    painter.setOpacity(1.0)

                    # Build cell-index lookup: (i, j) -> (px, py)
                    valid_cell_pixels = {(entry[2], entry[3]): (entry[0], entry[1]) for entry in self._polygon_valid_pixels}

                    # Grids
                    rows = list(range(len(self.y_range) - 1))
                    rows = list(reversed(rows))

                    for row_idx, j in enumerate(rows):

                        if row_idx % 2 == 0:
                            x_indices = range(len(self.x_range) - 1)
                        else:
                            x_indices = reversed(range(len(self.x_range) - 1))

                        for i in x_indices:

                            if (i, j) not in valid_cell_pixels:
                                continue

                            left  = self.x_range[i]
                            right = self.x_range[i + 1]

                            top = self.y_range[j + 1]
                            bottom = self.y_range[j]

                            # Real midpoint
                            mid_x_real = (left + right) / 2
                            mid_y_real = (top + bottom) / 2

                            location = (round(mid_x_real, 2), round(mid_y_real, 2))

                            # Stored pixel midpoint (avoids float rounding mismatch)
                            mid_px, mid_py = valid_cell_pixels[(i, j)]

                            if location in self.visited_points:

                                # Corners
                                tx_left   = (left - bx0) / real_w
                                tx_right  = (right - bx0) / real_w
                                ty_top    = (top - by0) / real_h
                                ty_bottom = (bottom - by0) / real_h

                                px_left   = px_min + tx_left * px_span
                                px_right  = px_min + tx_right * px_span

                                py_top    = py_min + (1 - ty_top) * py_span
                                py_bottom = py_min + (1 - ty_bottom) * py_span

                                rect_x = int(px_left)
                                rect_y = int(min(py_top, py_bottom))
                                rect_w = int(px_right - px_left)
                                rect_h = int(abs(py_bottom - py_top))

                                painter.setPen(Qt.NoPen)
                                painter.setOpacity(0.6)
                                painter.fillRect(rect_x, rect_y, rect_w, rect_h, QColor("#BBFF00"))

                            else:
                                # Draw sampling location (midpoint of grid cell)
                                painter.setPen(QPen(QColor("#EAFFC2"), 3))
                                painter.drawPoint(mid_px, mid_py)

                                # Add midpoint to real locations
                                if location not in self.real_points:
                                    self.real_points.append(location)



            # Rectangle overlay
            if self.rectangle and not self.polygon_active:
                
                # Rows
                if self.sample_overlay_y is not None and self.rowsOnly:
                    painter.setPen(QPen(QColor("#EAFFC2"), 2))
                    painter.setOpacity(0.6)

                    start_x = self.rectangle.left()
                    start_y = self.rectangle.top()
                    end_x   = self.rectangle.right()
                    end_y   = self.rectangle.bottom()

                    width  = end_x - start_x
                    height = end_y - start_y

                    x0, y0, x1, y1 = self.probe_rectangle
                    real_width  = x1 - x0
                    real_height = y1 - y0

                    # Draw rows only 
                    for val in self.y_range:
                        ty = (val - y0) / real_height
                        y = int(start_y + (1 - ty) * height)

                        painter.drawLine(start_x, y, end_x, y)

                    painter.setPen(QPen(QColor("#67FFD9"), 3))
                    painter.setOpacity(1.0)

                    prev_point = None

                    for row_idx, y_val in enumerate(reversed(self.y_range)):

                        ty = (y_val - y0) / real_height
                        py = start_y + (1 - ty) * height

                        # Serpentine direction
                        if row_idx % 2 == 0:
                            x_start_real = x0
                            x_end_real   = x1
                        else:
                            x_start_real = x1
                            x_end_real   = x0

                        # ty_pixel = (py - start_y) / height
                        # real_y = y0 + (1 - ty_pixel) * real_height

                        # print(y_val)
                        # print(real_y)

                        location1 = (round(x_start_real, 2), round(y_val, 2))
                        location2 = (round(x_end_real, 2), round(y_val, 2))

                        if location1 not in self.real_points:
                            self.real_points.append(location1)

                        if location2 not in self.real_points:
                            self.real_points.append(location2)

                        # Convert X
                        tx_start = (x_start_real - x0) / real_width
                        tx_end   = (x_end_real - x0) / real_width

                        px_start = start_x + tx_start * width
                        px_end   = start_x + tx_end * width

                        # Draw horizontal line
                        painter.setPen(QPen(QColor("#67FFD9"), 3))
                        painter.drawLine(int(px_start), int(py), int(px_end), int(py))

                        # Draw vertical connection
                        if prev_point:
                            painter.drawLine(
                                int(prev_point[0]), int(prev_point[1]),
                                int(px_start), int(py)
                            )

                        
                        # Check visited points
                        # Start point
                        if location1 in self.visited_points:
                            painter.setPen(Qt.NoPen)
                            painter.setBrush(QColor("#00FF00"))
                            r = 7
                            painter.drawEllipse(int(px_start - r), int(py - r), r * 2, r * 2)

                        # End point
                        if location2 in self.visited_points:
                            painter.setPen(Qt.NoPen)
                            painter.setBrush(QColor("#00FF00"))
                            r = 7
                            painter.drawEllipse(int(px_end - r), int(py - r), r * 2, r * 2)

                        # Intersection point (vertical connection start)
                        if prev_point:
                            prev_location = (
                                round((prev_point[0] - start_x) / width * real_width + x0, 2),
                                round((1 - (prev_point[1] - start_y) / height) * real_height + y0, 2)
                            )

                            if prev_location in self.visited_points:
                                painter.drawEllipse(int(prev_point[0] - r), int(prev_point[1] - r), r * 2, r * 2)

                        prev_point = (px_end, py)


                # Grid
                elif self.sample_overlay_x is not None and self.sample_overlay_y is not None and not self.rowsOnly:
                    painter.setPen(QPen(QColor("#EAFFC2"), 2))
                    painter.setOpacity(0.6)

                    start_x = self.rectangle.left()
                    start_y = self.rectangle.top()
                    end_x   = self.rectangle.right()
                    end_y   = self.rectangle.bottom()

                    width  = self.rectangle.width()
                    height = self.rectangle.height()

                    x0, y0, x1, y1 = self.probe_rectangle

                    real_width  = x1 - x0
                    real_height = y1 - y0

                    # Vertical lines
                    for val in self.x_range:
                        tx = (val - x0) / real_width
                        x = int(start_x + tx * width)

                        painter.drawLine(x, start_y, x, end_y)

                    # Horizontal lines
                    for val in self.y_range:
                        ty = (val - y0) / real_height
                        y = int(start_y + (1 - ty) * height)

                        painter.drawLine(start_x, y, end_x, y)

                    painter.setPen(QPen(QColor("#EAFFC2"), 3))
                    painter.setOpacity(1.0)


                    for j in range(len(self.y_range) - 1):
                        # Serpentine direction
                        if j % 2 == 0:
                            # Left to right
                            x_indices = range(len(self.x_range) - 1)
                        else:
                            # Right to left
                            x_indices = reversed(range(len(self.x_range) - 1))

                        for i in x_indices:

                            left  = self.x_range[i]
                            right = self.x_range[i + 1]

                            top    = self.y_range[j + 1]
                            bottom = self.y_range[j]

                            # Midpoint 
                            mid_x_real = (left + right) / 2
                            mid_y_real = (top + bottom) / 2

                            # Normalize midpoint
                            tx = (mid_x_real - x0) / real_width
                            ty = (mid_y_real - y0) / real_height

                            # Convert to pixel 
                            mid_x = start_x + tx * width
                            mid_y = start_y + (1 - ty) * height

                            location = (round(mid_x_real, 2), round(mid_y_real, 2))
                            if location not in self.real_points:
                                self.real_points.append(location)

                            if location in self.visited_points:

                                # Corners 
                                tx_left   = (left - x0) / real_width
                                tx_right  = (right - x0) / real_width
                                ty_top    = (top - y0) / real_height
                                ty_bottom = (bottom - y0) / real_height

                                px_left   = start_x + tx_left * width
                                px_right  = start_x + tx_right * width

                                py_top    = start_y + (1 - ty_top) * height
                                py_bottom = start_y + (1 - ty_bottom) * height

                                rect_x = int(px_left)
                                rect_y = int(min(py_top, py_bottom))
                                rect_w = int(px_right - px_left)
                                rect_h = int(abs(py_bottom - py_top))

                                painter.setPen(Qt.NoPen)
                                painter.setOpacity(0.6)
                                painter.fillRect(rect_x, rect_y, rect_w, rect_h, QColor("#BBFF00"))

                            else:
                                painter.setPen(QPen(QColor("#EAFFC2"), 3))
                                painter.drawPoint(int(mid_x), int(mid_y))


            # ── Draw mode rendering ──────────────────────────────────────────────

            stroke_color = QColor("#FF6B35")
            pen_stroke = QPen(stroke_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

            # Computed polygon (shown after "Convert to Polygon")
            if self.polygon_active and self.polygon_points:
                poly = QPolygon(self.polygon_points)
                painter.setPen(QPen(QColor("#BBFF00"), 2))
                painter.setOpacity(0.6)
                painter.setBrush(QBrush(QColor(187, 255, 0, 100)))
                painter.drawPolygon(poly)
                painter.setBrush(Qt.NoBrush)
                # Also draw the raw strokes dimly so the user can still see what they drew
                dim_pen = QPen(QColor(255, 107, 53, 80), 1, Qt.DotLine)
                painter.setPen(dim_pen)
                for stroke in self.draw_strokes:
                    for i in range(1, len(stroke)):
                        painter.drawLine(stroke[i - 1], stroke[i])

            # Filled ROI overlay (shown after "Done")
            elif self.roi_closed:
                all_points = []
                for stroke in self.draw_strokes:
                    all_points.extend(stroke)
                if all_points:
                    polygon = QPolygon(all_points)
                    painter.setPen(QPen(stroke_color, 2))
                    painter.setBrush(QBrush(QColor(255, 107, 53, 70)))
                    painter.drawPolygon(polygon)
                    painter.setBrush(Qt.NoBrush)

            else:
                # Completed strokes
                painter.setPen(pen_stroke)
                for stroke in self.draw_strokes:
                    for i in range(1, len(stroke)):
                        painter.drawLine(stroke[i - 1], stroke[i])

                # Stroke currently being drawn
                if self.current_stroke:
                    painter.setPen(pen_stroke)
                    for i in range(1, len(self.current_stroke)):
                        painter.drawLine(self.current_stroke[i - 1], self.current_stroke[i])

            # Cursor indicator
            if self.cursor_pos and self.type == "Draw":
                if self.draw_mode == "pencil":
                    painter.setPen(QPen(stroke_color, 2))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(self.cursor_pos, 5, 5)
                elif self.draw_mode == "eraser":
                    painter.setPen(QPen(QColor("#FFFFFF"), 2, Qt.DashLine))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(self.cursor_pos, self.eraser_radius, self.eraser_radius)


            # Emit signal
            self.roiSignal.emit({
                "dot": self.dot,
                "rect": self.rectangle,
                "probe_rect": self.probe_rectangle,
                "x_range": self.x_range,
                "y_range": self.y_range,
                "x_count": self.sample_overlay_x,
                "y_count": self.sample_overlay_y,
                "rows": self.rowsOnly,
                "polygon": self.polygon_points,
                "probe_polygon": self.probe_polygon,
                "probe_polygon_valid_pts": self._polygon_valid_pixels
            })

        except Exception as e:
            print(e)
            pass
        
    def setNewPixmap(self, pixmap=None):
        if pixmap is not None:
            rgb_img = cv2.cvtColor(pixmap, cv2.COLOR_BGR2RGB)
            self.original_pixmap = rgb_img

            h, w, ch = rgb_img.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.scaled = q_img.scaled(int(1280 * self.scale_val), int(720 * self.scale_val), Qt.KeepAspectRatio)
            self.scaled = QPixmap.fromImage(self.scaled)
            self.setPixmap(self.scaled)
        
        else:
            self.setPixmap(QPixmap())


    # Only update shapes for Pre-run config page
    def setValsPage3(self, data):
        self.dot = data["dot"]
        self.rectangle = data["rect"]
        self.polygon_points = list(data["polygon"])
        self.polygon_active = bool(data["polygon"])

        self.update()


    # Update all sampling variables for Sampling Progress page
    def setValsPage4(self, data):
        self.visited_points = [] # Reset visited points at start of sample run
        self.sample_overlay_x = None 
        self.sample_overlay_y = None

        self.dot = data["dot"]
        self.rectangle = data["rect"]

        self.polygon_points = list(data["polygon"])
        self.polygon_active = bool(data["polygon"])
        self.probe_polygon = data["probe_polygon"]
        self._polygon_valid_pixels = data["probe_polygon_valid_pts"]

        self.probe_rectangle = data["probe_rect"]

        self.rowsOnly = data["rows"]

        # Only update Y vals if doing drag sampling
        if self.rowsOnly:
            self.x_range = None
            self.sample_overlay_x = None

            self.y_range = data["y_range"]
            self.sample_overlay_y = data["y_count"]

        # Update all
        else:
            self.x_range = data["x_range"]
            self.y_range = data["y_range"]
            
            self.sample_overlay_x = data["x_count"]
            self.sample_overlay_y = data["y_count"]

        self.update()


    def addVisitedLocation(self, location):
        self.visited_points.append(location)
        self.update()


    # Function to update the rectangle ROI overlay
    def updateOverlay(self, x, y, type, sampling):
        self.real_points = []

        try:
            if self.rectangle:
                if sampling.rectangle:
                    self.probe_rectangle = sampling.rectangle
                else:
                    self.probe_rectangle = [100, 40, 115, 50]
                
                x0, y0, x1, y1 = self.probe_rectangle

                # Sampling spots based sizing
                if type == 0:
                    x_increment = abs(x1 - x0) / float(x)
                    y_increment = abs(y1 - y0) / float(y)

                    self.x_range = np.arange(x0, x1, x_increment)
                    self.y_range = np.arange(y0, y1, y_increment)

                    self.x_range = np.append(self.x_range, x1)
                    self.y_range = np.append(self.y_range, y1)

                    self.sample_overlay_x = len(self.x_range)
                    self.sample_overlay_y = len(self.y_range)
                
                # Resolution based sizing
                elif type == 1:
                    self.x_range = np.arange(x0, x1, float(x))
                    self.y_range = np.arange(y0, y1, float(y))

                    self.x_range = np.append(self.x_range, x1)
                    self.y_range = np.append(self.y_range, y1)

                    if len(self.x_range) >= 3 and (self.x_range[-1] - self.x_range[-2]) < float(x) / 2:
                        self.x_range = np.delete(self.x_range, -2)
                    if len(self.y_range) >= 3 and (self.y_range[-1] - self.y_range[-2]) < float(y) / 2:
                        self.y_range = np.delete(self.y_range, -2)

                    self.sample_overlay_x = len(self.x_range)
                    self.sample_overlay_y = len(self.y_range)


                self.update()

                # Transfer all sampling points to sampling item
                sampling.real_points_list = self.real_points

        except:
            self.sample_overlay_x = None
            self.sample_overlay_y = None


    # Function to update the overlay to show rows (Drag sampling)
    # Shows the serpentine sampling path
    def updateOverlayRows(self, y, type, sampling):
        self.real_points = []
        
        try:
            if self.rectangle: 
                if sampling.rectangle:
                    self.probe_rectangle = sampling.rectangle
                else:
                    self.probe_rectangle = [100, 40, 115, 50]
                
                x0, y0, x1, y1 = self.probe_rectangle

                # Sampling spots based sizing
                if type == 0:
                    y_increment = abs(y1 - y0) / float(y)
                    self.y_range = np.arange(y0, y1, y_increment)
                    self.y_range = np.append(self.y_range, y1)

                    self.sample_overlay_x = None
                    self.sample_overlay_y = len(self.y_range)

                # Resolution based sizing
                elif type == 1:
                    self.y_range = np.arange(y0, y1, float(y))
                    self.y_range = np.append(self.y_range, y1)

                    if len(self.y_range) >= 3 and (self.y_range[-1] - self.y_range[-2]) < float(y) / 2:
                        self.y_range = np.delete(self.y_range, -2)

                    self.sample_overlay_x = None
                    self.sample_overlay_y = len(self.y_range)

                self.update()

                # Transfer all sampling points to sampling item
                sampling.real_points_list = self.real_points

        except:
            self.sample_overlay_x = None
            self.sample_overlay_y = None


    def updateOverlayPolygon(self, x, y, type, sampling):
        """Build a grid over the polygon bounding box and filter to cells inside the polygon.

        Grid lines cover the bounding box; only cell midpoints inside the polygon
        are kept as sampling points.  Uses cv2.pointPolygonTest for containment.
        """
        self.real_points = []
        self.probe_polygon = []
        self._polygon_valid_pixels = []

        try:
            if not self.polygon_active or not self.polygon_points:
                return

            # Real-world bounding box: use sampling.drawn if available,
            # otherwise fall back to hardcoded test values (10 x 15 mm box).
            if hasattr(sampling, 'drawn') and sampling.drawn:
                xs = [p[0] for p in sampling.drawn]
                ys = [p[1] for p in sampling.drawn]
                bx0, bx1 = min(xs), max(xs)
                by0, by1 = min(ys), max(ys)
            else:
                bx0, by0, bx1, by1 = 100, 40, 115, 55  # 15 x 15 mm test box

            real_w = bx1 - bx0
            real_h = by1 - by0
            if real_w <= 0 or real_h <= 0:
                return

            # Build grid lines over the bounding box
            if type == 0:  # number of sampling spots
                x_range = np.arange(bx0, bx1, real_w / float(x))
                y_range = np.arange(by0, by1, real_h / float(y))
            elif type == 1:  # resolution in mm
                x_range = np.arange(bx0, bx1, float(x))
                y_range = np.arange(by0, by1, float(y))
            else:
                return

            x_range = np.append(x_range, bx1)
            y_range = np.append(y_range, by1)

            # For resolution mode: if the last cell is smaller than half the
            # resolution, merge it into the previous cell by dropping the
            # second-to-last boundary (e.g. [0,3,6,9,10] → [0,3,6,10]).
            if type == 1:
                if len(x_range) >= 3 and (x_range[-1] - x_range[-2]) < float(x) / 2:
                    x_range = np.delete(x_range, -2)
                if len(y_range) >= 3 and (y_range[-1] - y_range[-2]) < float(y) / 2:
                    y_range = np.delete(y_range, -2)

            self.x_range = x_range
            self.y_range = y_range
            self.probe_polygon = [bx0, by0, bx1, by1]

            # Pixel-space bounding box of the polygon
            px_min = min(p.x() for p in self.polygon_points)
            px_max = max(p.x() for p in self.polygon_points)
            py_min = min(p.y() for p in self.polygon_points)
            py_max = max(p.y() for p in self.polygon_points)
            px_span = (px_max - px_min) or 1
            py_span = (py_max - py_min) or 1

            poly_pts_np = np.array(
                [[p.x(), p.y()] for p in self.polygon_points], dtype=np.int32
            )

            valid_pixels = []
            for j in range(len(y_range) - 1):
                for i in range(len(x_range) - 1):
                    mid_x_real = (x_range[i] + x_range[i + 1]) / 2
                    mid_y_real = (y_range[j] + y_range[j + 1]) / 2

                    # Map real-world midpoint → pixel space via bounding box proportions
                    tx = (mid_x_real - bx0) / real_w
                    ty = (mid_y_real - by0) / real_h
                    px = int(px_min + tx * px_span)
                    py = int(py_min + (1 - ty) * py_span)

                    if cv2.pointPolygonTest(poly_pts_np, (float(px), float(py)), False) >= 0:
                        # self.real_points.append((round(mid_x_real, 2), round(mid_y_real, 2)))
                        valid_pixels.append((px, py, i, j))

            self._polygon_valid_pixels = valid_pixels
            self.sample_overlay_x = len(x_range)
            self.sample_overlay_y = len(y_range)

            self.update()
            sampling.real_points_list = self.real_points

        except Exception:
            self.sample_overlay_x = None
            self.sample_overlay_y = None

    
    def updateOverlayPolygonRows(self, y, type, sampling):
        self.real_points = []
        self.probe_polygon = []
        self._polygon_valid_pixels = []

        try:
            if not self.polygon_active or not self.polygon_points:
                return

            if hasattr(sampling, 'drawn') and sampling.drawn:
                xs = [p[0] for p in sampling.drawn]
                ys = [p[1] for p in sampling.drawn]
                bx0, bx1 = min(xs), max(xs)
                by0, by1 = min(ys), max(ys)
            else:
                bx0, by0, bx1, by1 = 100, 40, 115, 55

            real_w = bx1 - bx0
            real_h = by1 - by0
            if real_w <= 0 or real_h <= 0:
                return

            # Sampling spots
            if type == 0: 
                y_range = np.arange(by0, by1, real_h / float(y))
            
            # Resolution
            elif type == 1:
                y_range = np.arange(by0, by1, float(y))
            else:
                return

            y_range = np.append(y_range, by1)


            self.x_range = None 
            self.y_range = y_range
            self.probe_polygon = [bx0, by0, bx1, by1]

            self.sample_overlay_x = None
            self.sample_overlay_y = len(y_range)

            self._polygon_valid_pixels = []

            self.update()
            sampling.real_points_list = self.real_points

        except Exception:
            self.sample_overlay_x = None
            self.sample_overlay_y = None

    
    # Draw row intersections
    def get_row_segments(self, y):
        intersections = []
        pts = self.polygon_points
        n = len(pts)

        for i in range(n):
            p1 = pts[i]
            p2 = pts[(i + 1) % n]

            y1, y2 = p1.y(), p2.y()

            if (y1 <= y < y2) or (y2 <= y < y1):
                t = (y - y1) / (y2 - y1)
                x = p1.x() + t * (p2.x() - p1.x())
                intersections.append(x)

        intersections.sort()

        segments = []
        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                segments.append((intersections[i], intersections[i + 1]))

        return segments



class InputField(QWidget):
    def __init__(self, title):
        super().__init__()

        layout = QHBoxLayout()

        self.name = QLabel(title, objectName="larger")
        self.input = QLineEdit()

        layout.addWidget(self.name)
        layout.addWidget(self.input)

        if title == "Tag bottom-left corner: ":
            self.input2 = QLineEdit()

            space = QLabel(", ")

            self.input.setPlaceholderText("X")
            self.input2.setPlaceholderText("Y")

            layout.addWidget(space)
            layout.addWidget(self.input2)

        self.setLayout(layout)

class ArrowButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.instance().primaryScreen()
        current_height = screen.size().height()

        base_screen_height = 1117
        scale = current_height / base_screen_height
        length = min(int(65 * scale), 75)

        layout = QVBoxLayout(self)
        self.setFixedHeight(length)

        self.button = QPushButton("Unwarp", objectName="clear")
        # self.button.setEnabled(False)
        
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.button)

        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(0)  

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor("#132c49"), 2)
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

class UnwarpComparison(QWidget):
    def __init__(self, size=None):
        super().__init__()

        layout = QVBoxLayout(self)
        val = self.compute_scale()

        self.feed = CamFeed(scale=val)
        self.arrow = ArrowButton()
        self.result = CamFeed(scale=val)

        layout.addWidget(self.feed)
        layout.addWidget(self.arrow)
        layout.addWidget(self.result)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


    # Function to handle scaling of the image feeds
    def compute_scale(self):
        screen = QApplication.instance().primaryScreen()
        available = screen.size()

        base_screen_height = 1117
        base_scale = 0.42

        scale = base_scale * (available.height() / base_screen_height)

        scale = min(scale, base_scale)

        return scale
