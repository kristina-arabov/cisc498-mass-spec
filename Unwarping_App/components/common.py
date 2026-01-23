from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QGridLayout, 
    QHBoxLayout, QPushButton, QSizePolicy, QToolButton,
    QScrollArea, QComboBox, QSlider, QVBoxLayout,
    QLineEdit, QGraphicsDropShadowEffect, QCheckBox, QStyle
)


from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QIcon, QPixmap, QImage, QPolygon, QFont
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect, QPoint, QSize, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
from PyQt5 import QtSvg

from PyQt5.QtMultimedia import QCameraInfo
from serial.tools import list_ports

import cv2

from Unwarping_App.components import utils

class DevicesButton(QPushButton):
    def __init__(self, text, icon_path, parent=None):
        super().__init__(parent)

        self.setObjectName("headerBlue")
        self.setFixedWidth(115)

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(
            20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        icon_label.setStyleSheet("background-color: #132C49;")

        text_label = QLabel(text)
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




class DevicesDropdown(QWidget):
    def __init__(self, parent=None, camera=None):
        super().__init__(parent)

        self.camera = camera

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.setFixedSize(550, 300)
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

        # 4 rows
        self.row_camera = DeviceRow("Camera", kind="camera", include_eye=True)
        self.row_printer = DeviceRow("3D Printer", kind="printer")
        self.row_cond = DeviceRow("Conductance", kind="conductance")
        self.row_lights = DeviceRow("Lights", kind="lights")

        inner_layout.addWidget(self.row_camera)
        inner_layout.addWidget(self.row_printer)
        inner_layout.addWidget(self.row_cond)
        inner_layout.addWidget(self.row_lights)
        inner_layout.addStretch(1)

        outer.addWidget(inner)
        self.setLayout(outer)


        # Function calls
        self.row_camera.toggle.stateChanged.connect(lambda: self.camConnection())
        

    # Camera connect / disconnect functionality
    def camConnection(self):
        if self.row_camera.toggle.isChecked():
            if not self.camera.running:
                try:
                    self.camera.start()
                except:
                    pass
            
            if self.camera.running and self.camera.capture.isOpened():
                self.row_camera.set_connected(True) # Doesn't always work?
        
        elif not self.row_camera.toggle.isChecked():
            if self.camera.running:
                self.camera.stop()

            self.row_camera.set_connected(False)

######### End of Devices Dropdown #######################################################################################


class Header(QWidget):
    def __init__(self, stacked_widget, camera):
        super().__init__()

        layout = QHBoxLayout()

        container = QWidget(objectName="header")
        inner_layout = QHBoxLayout(container)

        self.stacked = stacked_widget
        self.camera = camera

        self.legacy_btn = QPushButton("Legacy Mode", objectName="headerGrey")
        self.return_btn = QPushButton("Return", objectName="headerGrey")
        self.return_btn.hide()

        credits_btn = QPushButton("Credits", objectName="headerBlue")
        help_btn = QPushButton("Help", objectName="headerBlue")

        self.devices_btn = DevicesButton("Devices", "Unwarping_App/components/images/Gear.svg")
        self.devices_btn.clicked.connect(self.showDevicesDropdown)
        self.devices_dropdown = None

        self.legacy_btn.clicked.connect(self.showMonitor)
        self.return_btn.clicked.connect(self.showUnwarping)

        inner_layout.addWidget(self.legacy_btn)
        inner_layout.addWidget(self.return_btn)
        inner_layout.addStretch()
        inner_layout.addWidget(credits_btn)
        inner_layout.addWidget(help_btn)
        inner_layout.addWidget(self.devices_btn)

        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

    def showDevicesDropdown(self):
        if self.devices_dropdown is None:
            self.devices_dropdown = DevicesDropdown(self, self.camera)
        
        button_pos = self.devices_btn.mapToGlobal(QPoint(-480, self.devices_btn.height()))
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


# TO BE UPDATED ANYWAY
class NavButtons(QWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked
        self.back_button = QPushButton(" ← ", objectName="clear")
        self.back_button.clicked.connect(self.goBack)

        self.page_title = QLabel("", objectName="page_title")
        self.next_button = QPushButton(" → ", objectName="blue")
        self.next_button.clicked.connect(self.goForward)

        self.layout = QGridLayout()
        self.layout.addWidget(self.back_button, 0, 0, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.page_title, 0, 1, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.next_button, 0, 2, alignment=Qt.AlignRight)

        self.setLayout(self.layout)
    
    def goForward(self):
        pages = len(self.stacked)

        self.back_button.setEnabled(True)

        if (self.stacked.currentIndex() + 1) <= (pages - 1):
            self.stacked.setCurrentIndex(self.stacked.currentIndex() + 1)
            self.back_button.setEnabled(True)
        
        if self.stacked.currentIndex() in [5, 8]:
            self.next_button.setEnabled(False)

    def goBack(self):
        if self.stacked.currentIndex() == 6:
            self.stacked.setCurrentIndex(0)
        # elif self.stacked.currentIndex() == 6:
        #     self.stacked.setCurrentIndex(4)
        #     self.next_button.setEnabled(False)
        elif self.stacked.currentIndex() > 0:
            self.stacked.setCurrentIndex(self.stacked.currentIndex() - 1)
            self.next_button.setEnabled(True) if self.stacked.currentIndex() != 4 else self.next_button.setEnabled(False)
        
        if self.stacked.currentIndex() == 0:
            self.back_button.setEnabled(False)
            self.next_button.setEnabled(False)

        
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

        self.minus.clicked.connect(lambda: self.brightnessIncrement(self.increments.currentText(), "minus"))
        self.plus.clicked.connect(lambda: self.brightnessIncrement(self.increments.currentText(), "plus"))

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

        self.setLayout(layout_final)
    
    def brightnessIncrement(self, value, type):
        if type == 'plus':
            self.slider.setValue(self.slider.value() + int(value))
        else:
            self.slider.setValue(self.slider.value() - int(value))


class ProbeDropdown(QWidget):
    def __init__(self):
        super().__init__()

        # Put everything in one container
        self.container = QWidget(objectName="light_blue_box")
        self.container.setStyleSheet("QWidget { background-color: #C8D3F1; }")
        self.container.setFixedSize(350, 150)
        container_layout = QGridLayout()

        # Title
        title = QLabel("Corner locations", objectName="larger")
        title.setStyleSheet("font-weight: bold;")

        # Toggle button to show/hide input fields
        self.toggle = QToolButton(objectName="toggle")
        self.toggle.setCheckable(True)
        self.toggle.setArrowType(Qt.UpArrow)
        self.toggle.clicked.connect(lambda: utils.controlToggle(self.toggle.isChecked(), self.toggle, self.input_section, self.container, 150)) 

        # specific container only for input sections
        self.input_section = QWidget()
        input_section_layout = QGridLayout()

        # Bottom left corner
        bottom_left_label = QLabel("Bottom-left corner: ( ")

        self.bottom_left_X = QLineEdit()
        self.bottom_left_Y = QLineEdit()

        self.bottom_left_X.setPlaceholderText("X")
        self.bottom_left_Y.setPlaceholderText("Y")

        self.bottom_left_X.setStyleSheet("background-color: #F0F0F0;")
        self.bottom_left_Y.setStyleSheet("background-color: #F0F0F0;")

        # Top right corner
        top_right_label = QLabel("Top-right corner:   ( ")

        self.top_right_X = QLineEdit()
        self.top_right_Y = QLineEdit()

        self.top_right_X.setPlaceholderText("X")
        self.top_right_Y.setPlaceholderText("Y")

        self.top_right_X.setStyleSheet("background-color: #F0F0F0;")
        self.top_right_Y.setStyleSheet("background-color: #F0F0F0;")

        # Tag size input
        tag_size_label = QLabel("Tag size (mm): ")
        self.tag_size_input = QLineEdit()
        self.tag_size_input.setStyleSheet("background-color: #F0F0F0;")

        space = QLabel(" , ")
        space2 = QLabel(" , ")
        end = QLabel(" )")
        end2 = QLabel(" )")

        input_section_layout.addWidget(bottom_left_label, 0, 0)
        input_section_layout.addWidget(self.bottom_left_X, 0, 1, alignment=Qt.AlignLeft)
        input_section_layout.addWidget(space, 0, 2,alignment=Qt.AlignLeft)
        input_section_layout.addWidget(self.bottom_left_Y, 0, 3, alignment=Qt.AlignLeft)
        input_section_layout.addWidget(end, 0, 4, alignment=Qt.AlignLeft)

        input_section_layout.addWidget(top_right_label, 1, 0)
        input_section_layout.addWidget(self.top_right_X, 1, 1, alignment=Qt.AlignLeft)
        input_section_layout.addWidget(space2, 1, 2, alignment=Qt.AlignLeft)
        input_section_layout.addWidget(self.top_right_Y, 1, 3, alignment=Qt.AlignLeft)
        input_section_layout.addWidget(end2, 1, 4,alignment=Qt.AlignLeft)

        input_section_layout.addWidget(tag_size_label, 2, 0)
        input_section_layout.addWidget(self.tag_size_input, 2, 1)

        self.input_section.setLayout(input_section_layout)

        # Add to overall container
        container_layout.addWidget(title, 0, 0, alignment=Qt.AlignLeft)
        container_layout.addWidget(self.toggle, 0, 1, alignment=Qt.AlignRight)
        container_layout.addWidget(self.input_section, 1, 0, 1, 2)

        self.container.setLayout(container_layout)

        # Show container
        layout_final = QHBoxLayout()
        layout_final.addWidget(self.container)

        self.setLayout(layout_final)
        
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
    def __init__(self, text):
        super().__init__()

        layout = QHBoxLayout()

        # dynamic size changing
        self.feed_width = int(1280 * 0.7)
        self.feed_height = int(720 * 0.7)

        # PUT text in here
        self.image_label = QLabel(objectName="camera_initial")
        self.image_label.setFixedSize(self.feed_width, self.feed_height)
        self.image_label.setText(text)

        self.cam_thread = None

        layout.addWidget(self.image_label)

        self.setLayout(layout)

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

    # function to set corner colour based on action
    def set_colour(self, i, colour):
        self.corner_colours[i] = QColor(colour)
        self.update()
    
    def paintEvent(self, event):
        self.setFixedSize(100, 100) # TODO dynamic?
        square = QRect(15, 15, 75, 75)
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
    # Overlay with unwarped image, else black screen
    def __init__(self):
        super().__init__()
        self.original_pixmap = None
        self.setStyleSheet("background-color: black;")
        
        self.type = "Dot" # dot on default

        self.rectangle = None
        self.dot = None

        # probe rectange is a list of corners, dot is just one point
        self.probe_rectangle = []
        self.probe_dot = None
        self.real_points = []

        self.sample_overlay_x = None
        self.sample_overlay_y = None
        # self.sample_overlay = None

        # positions + flag
        self.start_point = None
        self.end_point = None
        self.drawing = False

        self.feed_width = int(1280 * 0.7)
        self.feed_height = int(720 * 0.7)
        self.setFixedSize(self.feed_width, self.feed_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.type == "Rectangle":
                self.start_point = event.pos() # grab start position
                self.drawing = True
            elif self.type == "Dot":
                self.dot = event.pos() # grab the (x, y) for the dot
                self.update()

    def mouseMoveEvent(self, event):
        # keep grabbing end point until user stops moving mouse
        if self.type == "Rectangle" and self.drawing:
            self.end_point = event.pos() 
            self.sample_overlay_x = None
            self.sample_overlay_y = None
            self.update()

    def mouseReleaseEvent(self, event):
        # grab the (x, y) of the end point
        if event.button() == Qt.LeftButton and self.type == "Rectangle":
            self.end_point = event.pos()
            self.drawing = False
            # draw the entire rectangle
            self.rectangle = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.Antialiasing)

        # Draw full rectangle
        if self.rectangle:
            painter.setPen(QPen(QColor("#BBFF00"), 3))
            painter.drawRect(self.rectangle)

        # If rectangle is still being drawn, update so the user sees
        if self.drawing and self.start_point and self.end_point:
            painter.setPen(QPen(QColor("#BBFF00"), 3, Qt.DashLine)) # looks cool
            painter.drawRect(QRect(self.start_point, self.end_point).normalized())

        # Draw dot
        if self.dot:
            painter.setPen(QPen(QColor("#16FFFF"), 4))
            painter.drawPoint(self.dot)

        # Pixel overlay
        if self.sample_overlay_x and self.sample_overlay_y:
            # Get offset between points relative to number of probing spots
            painter.setPen(QPen(QColor("#EAFFC2"), 3))
            pixels_x = int((self.end_point.x() - self.start_point.x()) / (self.sample_overlay_x))
            pixels_y = int((self.end_point.y() - self.start_point.y()) / (self.sample_overlay_y))

            y = self.start_point.y()
            x = self.start_point.x()

            for i in range(self.sample_overlay_y + 1):
                for j in range(self.sample_overlay_x + 1):
                    painter.drawPoint(QPoint(x, y))
                    x += pixels_x
                    
                x = self.start_point.x()
                y += pixels_y
            
            painter.end()

        self.update()
    
    def setNewPixmap(self, pixmap):
        rgb_img = cv2.cvtColor(pixmap, cv2.COLOR_BGR2RGB)
        self.original_pixmap = rgb_img

        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.scaled = q_img.scaled(int(1280 * 0.7), int(720 * 0.7), Qt.KeepAspectRatio)
        self.scaled = QPixmap.fromImage(self.scaled)
        self.setPixmap(self.scaled)
        

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

class CamFeedSmall(QWidget):
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
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        feed = CamFeedSmall("Live feed here")
        unwarp_component = ArrowButton()
        result = CamFeedSmall("Result here")

        layout.addWidget(feed)
        layout.addWidget(unwarp_component)
        layout.addWidget(result)