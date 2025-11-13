import sys
sys.dont_write_bytecode = True


# Import Python libraries and packages
import sys
import cv2
import csv
import queue as Queue
import numpy as np
# from serial import (Serial, SerialException)                  #requires installation of pyserial
import time
from serial.tools import list_ports
import pyqtgraph as pg
import os 

import fitz 

 
# Imports modules from the GUI toolkit PyQt
import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QPoint, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPainter, QImage, QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

# Imports the files from the folder core, which are used to bind/link/connect a button with a function
from .core import serialcon, conductance, printer, pump, gcodegen, captureStdout, camera # file in folder

from printrun.pronsole import pronsole
import math

# Imports UI design implementation
from .gui import newui, testui

from .gui import errorPopUp, infoPopUp, inputPopUp, successPopUp, cationPopUp
#       from Qt designer as
#       main.py files and
#       put it in the same directory
#       as this file -- ??

#   Ui_xxx is the name of the MainWindow
#       defined in QtDesigner (default:
#       MainWindow

PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # for 4k resolution

image_queue = Queue.Queue()  # Queue to hold images
conductance_queue = Queue.Queue()  # Queue to hold conductance values
BaseUiClass = testui.Ui_MainWindow if os.name == 'nt' else newui.Ui_MainWindow
# Provides main application window and initializes GUI; enabling functions to connect with the buttons
class MyApp(BaseUiClass, QtWidgets.QMainWindow):  # inherit all properties from QMainWindow class
    """
    This class Provides main application window and initializes GUI; enabling functions to connect with the buttons
    
    inherits all properties from QMainWindow class (can use all functions and variables from QMainWindow class)
    
    
    """
    
    def __init__(self, camera, printer):  # this init part runs every time an object of MainWin is created
        """
        This init part runs every time an object of MainWin is created (from pyqt5)
        """
        super(MyApp, self).__init__()  # parent constructor
        self.setupUi(self)  # fuction defined in main.py
        self.msg_con_err = QMessageBox()


        #self.initStdoutCapture()
        
        self.serConductance = serialcon.SerialConnection() # Calls class for serial connection
        self.conThread = conductance.ConThread() # Calls class for conductance
        self.Printer = printer # Calls class for printer
        self.Pump=pump.Pump_control() # Calls class for pump
        self.Pump.Connection = serialcon.SerialConnection() #class for serial connection
        self.Gcode=gcodegen.Gcode() # Calls class for gcode
        self.camThread = camera
        camera.change_pixmap_signal.connect(self.update_frame)
        # Image Widget class defined below. QWidget in QTDesigner is call self.displays
      
        self.initwidgets()
        # Creates a Qtimer
        self.Gvupdatetimer=QTimer(self)
        # Emits a timeout() signal at constant intervals (100 millisecond)
        self.Gvupdatetimer.timeout.connect(lambda: self.updategv())  # when timer is over values in queue are plotted
        self.Gvupdatetimer.start(100)
        # self.showMaximized()                               #   maximize window
        self.conductance_min = 0
        
        self.last_pos = [0,0,0]

        self.calculate_parameters_sample()
        self.enable_parameters()
        
        
        
        

    # Initialize Widgets when my_app is generated
    def initwidgets(self):
        # Define trigger elements/inputs
        
        # connect to threshold
        self.con_threshold_sp.valueChanged.connect(self.prttouch)
        self.lower_threshold.valueChanged.connect(self.prttouch)
        
        # Conductance Feedback (control buttons)
        self.con_connect_bt.clicked.connect(self.con_connect) #when button is clicked, con_connect is executed
        self.con_connect_bt.setEnabled(True)

        # Disconnect from conductance meter
        self.con_disconnect_bt.clicked.connect(self.con_disconnect)
        self.con_disconnect_bt.setEnabled(False)

        # Conductance (control buttons)
        self.conThread_start_btn.clicked.connect(self.start_con_thread)
        self.conThread_start_btn.setEnabled(False)

        # Stop conductance meter
        self.conThread_stop_btn.clicked.connect(self.stop_con_thread)
        self.conThread_stop_btn.setEnabled(False)

        # Save conductance data
        self.conThread_save_btn.clicked.connect(self.prompt_save_con)
        self.conThread_save_btn.setEnabled(True)

        # Conductance Plot Range
        self.conPltRange.valueChanged.connect(
            self.conplotrangevalue)  # exectues conplotrangevalue when slidebar is moved
        self.conPltRange.setEnabled(False)

    
        # Printer (control buttons)
        self.prt_con_btn.clicked.connect(self.prtconnect)
        self.prt_send_btn.clicked.connect(self.prtsendgcode)
        self.prt_discon_btn.clicked.connect(self.prtdisconnect)
        self.prt_home_btn.clicked.connect(self.prthome)

        self.prt_startrun_btn.clicked.connect(self.prtrungc)

        #self.prt_poszero_btn.clicked.connect(self.prtposzero)
        #self.prt_poshundred_btn.clicked.connect(self.prtposhundred)

        # Printer Movement in X, Y, Z direction
        self.prt_xp_btn.clicked.connect(lambda: self.prtmove("x","+"))
        self.prt_xn_btn.clicked.connect(lambda: self.prtmove('x','-'))
        self.prt_yp_btn.clicked.connect(lambda: self.prtmove("y","+"))
        self.prt_yn_btn.clicked.connect(lambda: self.prtmove('y','-'))
        self.prt_zp_btn.clicked.connect(lambda: self.prtmove("z","+"))
        self.prt_zn_btn.clicked.connect(lambda: self.prtmove('z','-'))

       #self.prt_fast_btn.clicked.connect(lambda: self.prtsetspeed("5000"))
        #self.prt_slow_btn.clicked.connect(lambda: self.prtsetspeed("5"))
        
        #Add other printer control buttons


        # Pump (control buttons)
        self.pump_con_btn.clicked.connect(self.puconnect)
        self.pump_start_btn.clicked.connect(self.pustart)
        self.pump_stop_btn.clicked.connect(self.pustop)
        #self.pump_discon_btn.clicked.connect(self.pudisconnect)
        #Add other pump btns
        self.pump_samplingq_sel.valueChanged.connect(self.puupdatesamplingq)
        self.pump_dwellq_sel.valueChanged.connect(self.puupdatedwellq)
        self.pump_setq_btn.clicked.connect(lambda: print(self.Pump.setflowrate(str(self.pump_samplingq_sel.value()))))


        #Gcode Generator (control buttons)
        self.gc_gen_btn.clicked.connect(self.gcgen)
        self.gc_currentall_btn.clicked.connect(self.gcgetxyz)
        self.gc_currentx_btn.clicked.connect(self.gcgetx)
        self.gc_currenty_btn.clicked.connect(self.gcgety)
        self.gc_currentz_btn.clicked.connect(self.gcgetz)
        self.gc_currentlz_btn.clicked.connect(self.gcgetlz)

        self.constant_z_mode.toggled.connect(lambda:self.gcmode())
        self.ref_conductance_select.toggled.connect(lambda:self.ref_gcmode())

        self.resolution_mode.toggled.connect(lambda:self.enable_parameters())
        self.sample_spot_mode.toggled.connect(lambda:self.enable_parameters())
        self.dimension_mode.toggled.connect(lambda:self.enable_parameters())
        
        
        self.gc_resx_sel.valueChanged.connect(lambda: self.calculate_parameters_sample())
        self.gc_resy_sel.valueChanged.connect(lambda: self.calculate_parameters_sample())
        self.dim_x_sb.valueChanged.connect(lambda: self.calculate_parameters_sample())
        self.dim_y_sb.valueChanged.connect(lambda: self.calculate_parameters_sample())
        self.gc_setx_sel.valueChanged.connect(lambda: self.calculate_parameters_sample())
        self.gc_sety_sel.valueChanged.connect(lambda: self.calculate_parameters_sample())
        # stop and pause
        self.prt_stop_btn.clicked.connect(lambda: self.Printer.stop_sample())
        self.prt_pause_btn.clicked.connect(lambda: self.change_to_resume())
        
        #update ports
        self.prt_update_btn.clicked.connect(lambda: self.update_ports())
        self.con_update_btn.clicked.connect(lambda: self.update_ports())
        
        self.con_zero_btn.valueChanged.connect(lambda: self.zeroCon())
        
        self.temp_start_btn.clicked.connect(lambda: self.set_temp())
        

        self.ref_on_off_btn.clicked.connect(lambda: self.ref_mode_on_off())
        
        self.ref_x_pos.valueChanged.connect(lambda value: setattr(self.Gcode, 'ref_x', value))
        self.ref_y_pos.valueChanged.connect(lambda value: setattr(self.Gcode, 'ref_y', value))
        self.ref_z_lower.valueChanged.connect(lambda value: setattr(self.Gcode, 'ref_z', value))
        self.ref_dwell.valueChanged.connect(lambda value: setattr(self.Gcode, 'ref_dwell', value))
        self.ref_sample.valueChanged.connect(lambda value: setattr(self.Gcode, 'ref_sample', value))
        
        
        self.ref_end_rb.clicked.connect(lambda: self.ref_end())
        self.ref_start_rb.clicked.connect(lambda: self.ref_end())
        self.ref_both_rb.clicked.connect(lambda: self.ref_end())
        
        
        self.send_btn.clicked.connect(lambda: self.send_absolute_pos())
        
        self.photo_btn.clicked.connect(lambda: self.camThread.take_photo())
        self.video_btn.clicked.connect(lambda: self.start_recording())
        
        self.pause_vid_btn.clicked.connect(lambda: self.pause_video())
        
        self.Printer.get_conductance.connect(lambda: self.handle_printer_request())
        
        self.help_bt.clicked.connect(lambda: self.help())
        
        
        
        self.Printer.done_sampling.connect(lambda: self.gv_gcode_update(True))
        self.setup_sample_toggle()
        
        self.camThread_start_btn.clicked.connect(lambda: self.start_camera())
        self.camThread_stop_btn.clicked.connect(lambda: self.stop_camera())
        
        self.z_first_rb.toggled.connect(lambda: self.z_first_last())
        
    
      
    def setup_sample_toggle(self):
        sb = [
            self.gc_startx_sel,
            self.gc_starty_sel,
            self.gc_startz_sel,
            self.gc_setx_sel,
            self.gc_sety_sel,
            self.gc_resx_sel,
            self.gc_resy_sel,
            self.dim_x_sb,
            self.dim_y_sb,
            self.gc_st_sel,
            self.gc_pause_sel,
            self.gc_zspeedup_sel,
            self.gc_speedxy_sel,
            self.gc_zspeed_sel,
            self.gc_step_sel
        ]
        rb = [
            self.sample_spot_mode,
            self.resolution_mode,
            self.dimension_mode,
            self.conductance_mode,
            self.constant_z_mode
        ]

        btn = [
            self.gc_currentall_btn,
            self.gc_currentx_btn,
            self.gc_currenty_btn,
            self.gc_currentz_btn,
            self.gc_currentlz_btn
]

        for spinbox in sb:
            spinbox.valueChanged.connect(lambda: self.prt_startrun_btn.setEnabled(False))
            
        for radio in rb:
            radio.toggled.connect(lambda: self.prt_startrun_btn.setEnabled(False))
            
        for button in btn:
            button.clicked.connect(lambda: self.prt_startrun_btn.setEnabled(False))
        
    def help(self):
        pdf_path = './help3.pdf'

        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        # Extract text from the PDF as HTML
        html_content = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            html_content += page.get_text("html")  # Extract text as HTML

        # Save the extracted HTML content to an HTML file
        with open("output.html", "w") as file:
            file.write(html_content)

        # Create a dialog window
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Help PDF")
        dialog.setGeometry(100, 100, 600, 800)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Display the HTML content in a QTextBrowser
        text_browser = QtWidgets.QTextBrowser(dialog)
        text_browser.setHtml(html_content)  # Set HTML content with formatting

        layout.addWidget(text_browser)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def load_pdf_content(self, pdf_path):
        document = fitz.open(pdf_path)
        content = ""
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            content += page.get_text()
        return content

        

   
    def set_temp(self):
        """
        set the bed temperature of the printer
        """
        print("setting bed temperature")

        self.Printer.cmd("M140 S%s" % self.prt_bed_temp_sb.value())
        time.sleep(0.1)
        self.Printer.cmd("M104 S%s" % self.prt_nozzel_temp_sb.value())
        
        
        
    def change_to_resume(self):
        """
        change to resume and calls the pause function
        """
        print('resume')

        self.prt_pause_btn.setText('Resume')
        self.Printer.pause_sample()
        self.prt_pause_btn.clicked.connect(lambda: self.change_to_pause())
    def change_to_pause(self):
        """
        change to pause and calls the resume function
        """
        print('pause')
        

        self.prt_pause_btn.setText('Pause')
        self.Printer.resume_sample()
        self.prt_pause_btn.clicked.connect(lambda: self.change_to_resume())

    def update_ports(self):#TODO: add windows compatibility
        self.prt_com_sel.clear()
        self.con_com_sel.clear()
        self.pump_com_sel.clear()
        
        serial_ports = list(list_ports.comports())
            
        #take off the everything after " - " in the port name
        extracted_ports = [str(port).split(' - ')[0] for port in serial_ports]
        extracted_names = [str(port).split(' - ')[1] for port in serial_ports]
        
        
        
        for i, port in enumerate(extracted_ports):
            self.con_com_sel.addItem("", port)
            self.con_com_sel.setItemText(i, extracted_names[i])
            self.prt_com_sel.addItem("", port)
            self.prt_com_sel.setItemText(i, extracted_names[i])
            self.pump_com_sel.addItem("", port)
            self.pump_com_sel.setItemText(i, extracted_names[i])
        self.setComboBoxSize(self.con_com_sel)
        self.setComboBoxSize(self.prt_com_sel)
        self.setComboBoxSize(self.pump_com_sel)

    def handle_printer_request(self):
        self.Printer.cond = self.conThread.capDecode
        self.Printer.got_conductance = True
        

    # function for all message boxes usually triggered in threads
    def messagebox(self, typ, icon):
        """
        

        Args:
            typ (str): type of error
            icon (char): severity of error (warning, information, question, critical)
        """
        

        # Displays error message
        if typ == "connectionErr":
            title = "Connection Error"
            msg = "Select different port and/or baud"
        elif typ == "connectionOk":
            title = "Connected"
            msg = "Connection successful"
        elif typ == "connectionFirst":
            title = "No connection found"
            msg = "Please connect first"
        elif typ == "connectionWrong":
            title = "Wrong device"
            msg = "Wrong device connected"
        elif typ == "wait":
            title = "Please wait"
            msg = "Just a second or two"
        elif typ == "conductanceStopped":
            title = "Stopped"
            msg = "Conductance recording stopped"
        elif typ == "disconnect":
            title = "Disconnected"
            msg = "Serial connection stopped"
        elif typ == "InitCam":
            title = "Initialize Camera"
            msg = "Connecting to camera. Please wait!"
        elif typ == "startcon":
            title = "Start Conductance"
            msg = "Connect and start conductance meter when this mode is used"
        elif typ == "Warning Constant Z mode":
            title = "Warning"
            msg = "Constant Z mode is enabled, please ensure that the Z value is set to the desired value"
        elif typ =="Take out probe":
            title = "Warning"
            msg = "Please take out the probe before homing"
        else:
            title = 'unknown error'
            msg = 'unknown error, see messageBox function'

        if icon == "w":
            #self.msg_con_err.setIcon(QMessageBox.Warning)
            self.msg_con_err = cationPopUp.CationPopUp(title, msg)
        elif icon == "i":
            #self.msg_con_err.setIcon(QMessageBox.Information)
            self.msg_con_err = successPopUp.SuccessPopUp(title, msg)
        #elif icon == "q":
            #self.msg_con_err.setIcon(QMessageBox.Question)
            #self.question = inputPopUp.InputPopUp(title, msg)
        elif icon == "c":
            self.msg_con_err.ErrorPopUp(title, msg)
            #self.msg_con_err.setIcon(QMessageBox.Critical)
        else:
            #self.msg_con_err.setIcon(QMessageBox.Critical)
            self.msg_con_err = errorPopUp.ErrorPopUp(title, msg)
            
            
        self.msg_con_err.exec()

    # Widget change functions. Usually triggerd by signals when in threads
    def widgetenable(self, widget, state):
        """set widget to enabled or disabled

        Args:
            widget (Qwidget): a widget
            state (bool): True or False
        """
        widget.setEnabled(state)

    def gvstatuschange(self, widget, color):  # color change for status graphics widgets
        """
        sets color of widget for status graphics widgets
        widget (Qwidget): a widget
        color (str): color of widget (red or green)
        
        """
        # Sets colour for 'green'
        if color == "green":
            brush = QtGui.QBrush(QtGui.QColor(0, 255, 0))
        # Sets colour for 'red'
        elif color == "red":
            brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        widget.setPalette(palette)

    def gv_gcode_update(self, status):
        
        if status == True: #if able to send another gcode
            
            self.gc_flag.setStyleSheet("background-color: #1BE03F; border-radius: 20px;")#green
            self.ready_label.setText("Ready")
            
            

        else:
            self.gc_flag.setStyleSheet("background-color: #E01B24; border-radius: 20px;") #red
            self.ready_label.setText("Not Ready")
            self.prt_startrun_btn.setEnabled(False)


    # Note:
    # Green represents that the device is connected
    # Red represents that the device is not connected
    def updategv(self):
        """
        Update the status of the devices (the color box)
        """
        #Conductance
        if self.serConductance.type == 'c\r\n' and self.serConductance.status==True:#not sure what c\r\n is?
            self.con_stat_gv.setStyleSheet("background-color: #1BE03F; border-radius: 20px;")
            self.con_stat_label.setText("Connected")
            self.con_stat_label.setStyleSheet("color: #1BE03F;")

        else:

            self.con_stat_gv.setStyleSheet("background-color: #E01B24; border-radius: 20px;")
            self.con_stat_label.setText("Not Connected")
            self.con_stat_label.setStyleSheet("color: #E01B24;")
        #Printer
        if self.Printer.homed:

            self.prt_home_stat_gv.setStyleSheet("background-color: #1BE03F; border-radius: 20px;")
            self.prt_home_label.setText("Homed")
            self.prt_home_label.setStyleSheet("color: #1BE03F;")
            
        else:
            self.prt_home_stat_gv.setStyleSheet("background-color: #E01B24; border-radius: 20px;")
            self.prt_home_label.setText("Not Homed")
            self.prt_home_label.setStyleSheet("color: #E01B24;")
        if self.Printer.prtconnect:
            self.prt_stat_gv.setStyleSheet("background-color: #1BE03F; border-radius: 20px;")
            self.prt_stat_label.setText("Connected")
            self.prt_stat_label.setStyleSheet("color: #1BE03F;")

        else:

            self.prt_stat_gv.setStyleSheet("background-color: #E01B24; border-radius: 20px;")
            self.prt_stat_label.setText("Not Connected")
            self.prt_stat_label.setStyleSheet("color: #E01B24;")

       # if self.Printer.moving:
           # self.gvstatuschange(my_app.prt_moving_gv,"red")
        #elif self.Printer.prtconnect:
         #   self.gvstatuschange(my_app.prt_moving_gv, "green")
        #else:
         #   self.gvstatuschange(my_app.prt_moving_gv, "red")

        #Pump
        #if self.Pump.initialized:
         #   self.gvstatuschange(my_app.pump_stat_gv, "green")
        #else:
         #   self.gvstatuschange(my_app.pump_stat_gv, "red")

        #Camera
        #if self.camThread.capturing:
         #   self.gvstatuschange(my_app.cam_stat_gv, "green")
        #else:
         #   self.gvstatuschange(my_app.cam_stat_gv, "red")

        # Gcode

    #############################################################################################################
    # Functions for the conductance meter
    #############################################################################################################

    # Actions of Buttons for conductance meter serial connection

    # Connect to conductance meter
    def con_connect(self):                      #self.con_com_sel.currentText() set line 859 of main.py
        """
        connect to conductance meter
        """
        #may need to change to check for value              changed from currentText to currentData
        self.serConductance.connect(self.con_com_sel.currentData(), int(self.con_baud_sel.currentText()))# port, baud
        if self.serConductance.status: #if connection is successful
            self.serConductance.checktype(1) #check type of connection (1 line)
            self.serConductance.type = 'c\r\n' #if type is c\r\n ie the arduino sends 'c'... should read the output of arduno
            if self.serConductance.type == 'c\r\n':
                print("Connected to %s @%s" % (self.serConductance.port, self.serConductance.baud))

                my_app.messagebox(typ="connectionOk", icon="i") #sends message box with connectionOk
                self.serConductance.status = True
                # Enable buttons
                my_app.con_disconnect_bt.setEnabled(True)
                my_app.con_connect_bt.setEnabled(False)
                my_app.conThread_start_btn.setEnabled(True)
                app.processEvents()
                self.enable_con_buttons(True)
            else:

                my_app.messagebox(typ="connectionWrong", icon="w")
                self.serConductance.ser.close()
        else:
            my_app.messagebox(typ="connectionErr", icon="w")
            # self.serConductance.ser.close()
        
    def enable_con_buttons(self, enable):
        self.con_connect_bt.setEnabled(not enable)
        self.con_disconnect_bt.setEnabled(enable)
        self.conThread_start_btn.setEnabled(enable)
        self.conThread_stop_btn.setEnabled(enable)
        self.conThread_save_btn.setEnabled(enable)
        self.conPltRange.setEnabled(enable)
        self.con_zero_btn.setEnabled(enable)
        self.conThread_save_btn.setEnabled(enable)
        self.con_threshold_sp.setEnabled(enable)
        self.con_zero_btn.setEnabled(enable)

    
    def con_disconnect(self):
        """
        Disconnect from conductance meter and sends message and disables buttons"""
        try:
            self.serConductance.disconnect()
            self.messagebox("disconnect", "i")
            my_app.con_disconnect_bt.setEnabled(False)
            my_app.con_connect_bt.setEnabled(True)
            my_app.conThread_start_btn.setEnabled(False)
            self.enable_con_buttons(False)
            
        except:
            print("con_disconnect error")



    def start_con_thread(self):
        """
        Actions of Buttons for conductance readout and plotting
        for graphing conductance values
        """
        self.conplotrangevalue()  # Function that takes value form slidebar for
        # self.conThread.plotrange(self.conPltRange.value())
        self.conThread.values = []
        self.conThread.signalmessage.connect(self.messagebox)
        self.conThread.ratems = 10 # Conductance is updating every 10ms
        try:
            self.conThread.connection = self.serConductance

            self.conThread.start()  # start conductance thread

            self.widgetenable(my_app.conThread_start_btn, False)
            self.widgetenable(my_app.conThread_stop_btn, True)
            self.widgetenable(my_app.conPltRange, True)

            self.conThread.timer = QTimer(self)  # Timer to trigger display fuction
            self.conThread.timer.timeout.connect(lambda: self.readconqueue(
                self.conThread.conductance_queue))  # when timer is over values in queue are plotted
            self.conThread.timer.start(self.conThread.ratems)
        except:
            self.messagebox("connectionFirst", "w")

    # Stop conductance meter
    def stop_con_thread(self):
        """
        stop conductance meter (graphing and reading values)
        """
        self.conThread.flag = False
        self.conThread_start_btn.setEnabled(True)
        self.conThread_stop_btn.setEnabled(False)


    # updates time range in minutes from slidebar conPltRange
    def conplotrangevalue(self):
        """
        updates time range in minutes from slidebar conPltRange
        """
        self.conThread.rangesec = self.conPltRange.value()
        try:
            self.conThread.refreshrate = self.conThread.values[-1][0] - self.conThread.values[-2][0]
        except:
            self.conThread.refreshrate = 30

    # Function that moves value pairs form queue from conThread to self.conThread.values list
    def readconqueue(self, queue):
        
        """used in conThread to read values from queue and plot them
        """
        if not queue.empty():
            values = queue.get()
            if values is not None:
                self.graphicsCap.clear()
                values.append(self.Printer.pos[0])#x
                values.append(self.Printer.pos[1])#y
                values.append(self.Printer.pos[2])#z
                self.conThread.values.append(values)
                self.conplotrange()

    # Function that extracts part of self.conThread.values to self.convaluesplot based on conplotrangevalue
    def conplotrange(self):
        """used in conThread to set the range of values to be plotted
        """
        if len(self.conThread.values) > 2:#if there are more than 2 values
            self.convaluesplot = []
            #refreshrate = self.conThread.values[-1][0] - self.conThread.values[-2][0]  # subtract last two time values
            #self.refreshrate(refreshrate)x
            self.rangepts = int(round((self.conThread.rangesec * 1000) / self.conThread.refreshrate))
            if (len(self.conThread.values) > self.rangepts):
                self.convaluesplot = self.conThread.values[-self.rangepts:]
            else:
                self.convaluesplot = self.conThread.values
            self.plotcon()

    # Plot conductance values in graphicsCap
    def plotcon(self):
        """
        used in conplotrange to plot conductance values
        """
        #self.Printer.cond = self.conThread.values[-1][1]
        
        self.graphicsCap.plot([item[0] for item in self.convaluesplot],
    [item[1]-self.conductance_min if item[1] > self.conductance_min else 0 for item in self.convaluesplot], pen=pg.mkPen(width=2.5))  # Define plotted time window
        app.processEvents()#to avoid flickering

    def zeroCon(self):
        """
        sets conductance to zero for val
        """
        self.conductance_min = self.con_zero_btn.value()
        
    # update refreshrate lcd display
    #def refreshrate(self, refreshrate):
        """set refreshrate in lcd display

        Args:
            refreshrate (int): refreshrate
        """
        #self.con_refreshrate_lcd.display(refreshrate)
        # app.processEvents() to avoid flickering

    def prompt_save_con(self):
        window = inputPopUp.InputPopUp('Save Conductance', 'Enter file name:')
        window.exec_()
        text = window.getText()
        if text:
            self.save_con(text)
            print("Conductance data saved to %s.csv" % text)

        pass
        
        # text, ok = QInputDialog.getText(self, 'Save Conductance', 'Enter file name:')
        # ok.setStyleSheet("QLineEdit { background-color: yellow }")
        # if ok and text:
        #     self.save_con(text)
        # pass
    def save_con(self,text): #path unused
        
        """
        save conductance values to csv file
        """
        #print(self.conThread.values)
        #write.writerows(rows)
        # Ensure the conductance folder exists
        folder = 'Conductance'
        if not os.path.exists(folder):
            os.makedirs(folder)
            print("Conductance folder created")
        
        # Construct the file path
        file_path = os.path.join(folder, str(text) + '.csv')
        header = ["time (ms)", "conductance", "x", "y", "z"]
        
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(header)
            writer.writerows(self.conThread.values)
    
    # def update_con_threshold(self, value): ##may be implemented
    #     """
    #     update conductance threshold
    #     """
    #     self.conThread.con_threshold = self.con_threshold_sp.value()
    #############################################################################################################
    # Functions for the printer
    #############################################################################################################



    # Action Buttions for Printer
    def prtconnect(self):
        """
        action buttons for 3d printer
        """ 
        print("Attempting to connect to the 3D printer...")
        print(f"Selected COM Port: {self.prt_com_sel.currentText()}")
        print(f"Selected Baud Rate: {self.prt_baud_sel.currentText()}")



        self.Printer.start() #starts a new thread where the run function is called in prt
        time.sleep(1)
        print("Opening pronsole.py")

        self.Printer.cmd('pronsole.py')
        time.sleep(1)                                       #changed from currentText to currentData
        self.Printer.cmd('connect %s %s' %(self.prt_com_sel.currentData(),self.prt_baud_sel.currentText()))
        time.sleep(1)
        self.enable_prt_buttons(True)
        self.Printer.postimer = QTimer()  # Timer to trigger display fuction
        # when timer is over values in queue are displayed
        self.Printer.postimer.timeout.connect(lambda: self.readprtposqueue(self.Printer.posqueue, self.Printer.temp_queue))
        self.Printer.postimer.timeout.connect(lambda: self.prtpuswitchpump())
        self.Printer.postimer.start(5)
        #print('check status of connection and set flag accordingly and also exit pronsole so serial is free')
    def enable_prt_buttons(self, enable):
        self.prt_send_btn.setEnabled(enable)
        self.prt_home_btn.setEnabled(enable)
        self.prt_yp_btn.setEnabled(enable)
        self.prt_yn_btn.setEnabled(enable)
        self.prt_xp_btn.setEnabled(enable)
        self.prt_xn_btn.setEnabled(enable)
        self.prt_zp_btn.setEnabled(enable)
        self.prt_zn_btn.setEnabled(enable)
        #self.prt_fast_btn.setEnabled(enable)
        #self.prt_slow_btn.setEnabled(enable)
        self.prt_pause_btn.setEnabled(enable)
        #self.prt_poszero_btn.setEnabled(enable)
        #self.prt_poshundred_btn.setEnabled(enable)
        self.prt_send_txt.setEnabled(enable)
        self.prt_send_btn.setEnabled(enable)
        self.prt_con_btn.setEnabled(not enable)
        self.prt_x_val.setEnabled(enable)
        self.prt_y_val.setEnabled(enable)
        self.prt_z_val.setEnabled(enable)
        self.prt_nozzel_temp_sb.setEnabled(enable)
        self.prt_bed_temp_sb.setEnabled(enable)
        self.temp_start_btn.setEnabled(enable)
       
        
    def prtdisconnect(self):
        """
        disconnect from 3d printer
        """
      
        self.Printer.cmd('exit')
        time.sleep(1)
        self.Printer.flag=False
        self.Printer.stop()
        self.enable_prt_buttons(False)

    def prtsendgcode(self):
        """send G code to printer
        """
        text = self.prt_send_txt.displayText()
        self.Printer.cmd(text)

    def prthome(self):
        """
        home the device
        """
        my_app.messagebox(typ="Take out probe", icon="w")
        self.Printer.home()

    def readprtposqueue(self,pos_queue, temp_queue):
        """
        read position queue from printer

        Args:
            queue (queue): queue of the printer position (pos 1 (x), pos 2 (y), pos 3 (z))
        """
        
        
        if not pos_queue.empty():
            pos = pos_queue.get()
          
            self.prt_x_lcd.display(pos[0])
            self.prt_y_lcd.display(pos[1])
            self.prt_z_lcd.display(pos[2])
        if not temp_queue.empty():
            temp = temp_queue.get()
            
            self.prt_bed_temp_lcd.display(temp[0])
            self.prt_nozzel_temp_lcd.display(temp[1])
    def temp_queue(self, queue):
        """
        read temperature queue from printer

        Args:
            queue (queue): queue of the printer temperature
        """
        if not queue.empty():
            temp = queue.get()
            
            #display bed and nozzel
    
    def prtrungc(self):
        """
        start run. should trigger the run function in printer.py
        """
       
        self.gv_gcode_update(False)
        if self.conductance_mode.isChecked():
            self.Printer.conductance_mode = True
            self.Printer.cmd("G90")
        else:
            self.Printer.conductance_mode = False
        
        self.Printer.current_position = self.Gcode.startz
        
        
        
        print("sending" + str(self.Gcode.startx) + " " + str(self.Gcode.starty))
        self.Printer.cmd("G0 X"+str(self.Gcode.startx)+" Y"+str(self.Gcode.starty)+" F1000")
        
        print("sending" + str(self.Gcode.startz))
        self.Printer.cmd("G0 Z"+str(self.Gcode.startz)+" F1000")
        
        print("Starting Run")
  
        
        self.Pump.setflowrate(str(self.Pump.qdwell)) # Dwell flow rate (wait time)
        self.Printer.pumpstatus = 1 # Pump status
        self.Pump.startpump() # Start pump
        self.Printer.gcodelist=self.Gcode.codelist # Gcode list with all code
        #self.Printer.eta_list=self.Gcode.eta_list # ETA list

        self.Printer.sampling = True
        self.Printer.gcodefile=True
        
        
 
        

    # Calls to printer.py to set X,Y,Z to 0,0,0
    def prtposzero(self):
        """set X, Y, Z to 0,0,0
        """
        self.Printer.setposzero()

    # Calls to printer.py to set X,Y,Z to 100,100,100
    def prtposhundred(self):
        """
        set X, Y, Z to 100,100,100
        """
        self.Printer.setposhundred()

    # Direction - movement of printer
    def prtmove(self,axis,direction):
        """
        movement of printer

        Args:
            axis (str): specifies the axis (y,z) -- note x is not used
            direction (+ OR -): specifies the direction of movement *******CHECK THIS********
        """
        self.Printer.cmd("G91")
        if axis=='z':
            val=str(self.prt_z_val.value())
        elif axis=='x':
            val=str(self.prt_x_val.value())
        elif axis=='y':
            val=str(self.prt_y_val.value())
        print("G0 "+axis+direction+val)

        self.Printer.cmd("G0 "+axis+direction+val+'F3000') #changed
        self.Printer.cmd("G90")

    # Speed of the printer
    def prtsetspeed(self,speed):
        """sets the speed of the printer for each axis

        Args:
            speed (int): speed of the printer
        """
        self.Printer.cmd("M203 X"+speed+" Y"+speed+" Z"+speed)
        print("M203 X"+speed+" Y"+speed+" Z"+speed)



    def prtpuswitchpump(self):
        """
        sets flow rate of pump based on printer status
        """
        
        if self.Printer.gcodefile:
            #dwelling flow rate
            if self.Printer.pumpstatus==1 and self.Pump.flowrate!=str(self.Pump.qdwell):
                self.Pump.setflowrate(str(self.Pump.qdwell)) # Dwell flow rate

            #sampling flow rate
            elif self.Printer.pumpstatus==2 and self.Pump.flowrate!=str(self.Pump.qsampling):
                self.Pump.setflowrate(str(self.Pump.qsampling)) # Sampling flow rate

            #stop pump
            elif self.Printer.pumpstatus== 0 and self.Pump.running==True:
                self.Pump.stoppump()
                self.Pump.running=False

    def prttouch(self):##UNUSED
        """
        set conductance threshold
        """
        #if self.Printer.gcodefile:
        self.Printer.con_threshold=self.con_threshold_sp.value() #main 325
        self.Printer.lower_threshold = self.lower_threshold.value()
        print("Lower threshold updated to: %s" % (self.Printer.lower_threshold))
        print("Upper threshold updated to: %s" % (self.Printer.con_threshold))
        print("")
        



    def gcgen(self):
        """
        action buttons for gcode generator
        """
        self.Gcode.codelist=[]
        self.gcreadvalues()
        self.Gcode.eta = 0
        self.Gcode.dist = 0
        self.Gcode.generate()
        self.prt_startrun_btn.setEnabled(True)


    def gcgetx(self):
        """
        obtains value for starting position for X
        """
        self.gc_startx_sel.setValue(self.Printer.pos[0])

    
    def gcgety(self):
        """# Obtains value for starting position for Y
        """
        self.gc_starty_sel.setValue(self.Printer.pos[1])

   
    def gcgetz(self):
        """ # Obtains value for starting position for Z
        """
        self.gc_startz_sel.setValue(self.Printer.pos[2])

    def gcgetxyz(self):
        """gets x y z coordinates
        """
        self.gcgetx()
        self.gcgety()
        self.gcgetz()

    def gcgetlz(self):
        """sets lz to current z position
        """
        self.gc_lz_sel.setValue(self.Printer.pos[2]) ##pos[2] is the z position

    def gcreadvalues(self):
        """
        sets values for gcode generator
        """
        print('read values')

        self.Gcode.startx = self.gc_startx_sel.value()
        self.Gcode.starty = self.gc_starty_sel.value()
        self.Gcode.startz = self.gc_startz_sel.value()
        self.Gcode.resx = self.gc_resx_sel.value()
        self.Gcode.resy = self.gc_resy_sel.value()
        self.Gcode.setx = self.gc_setx_sel.value()
        self.Gcode.sety = self.gc_sety_sel.value()
        self.Gcode.st = self.gc_st_sel.value()
        self.Gcode.pause = self.gc_pause_sel.value()
        self.Gcode.zspeed = self.gc_zspeed_sel.value()
        self.Gcode.zspeedup = self.gc_zspeedup_sel.value()
        self.Printer.z_speed = self.gc_zspeed_sel.value()
        self.Printer.z_speedup = self.gc_zspeedup_sel.value()
        self.Printer.xy_speed = self.gc_speedxy_sel.value()
        self.Gcode.speedxy = self.gc_speedxy_sel.value()
        self.Gcode.filename = self.gc_filename_txt.displayText()
        self.Gcode.x1 = self.Printer.pos[0]
        self.Gcode.y1 = self.Printer.pos[1]
        self.Gcode.z1 = self.Printer.pos[2]


        #self.Gcode.zoff = self.gc_zoff_sel.value()
        self.Gcode.step = self.gc_step_sel.value()

        self.Gcode.lz = self.gc_lz_sel.value()

        self.Printer.sampling_spot_y = self.gc_sety_sel.value() # Sets the number of sampling spots - y


    
    def gcmode(self):
        """
        set mode for gcode generator
        """
        if self.constant_z_mode.isChecked() == True:
            
            my_app.messagebox(typ="Warning Constant Z mode", icon="w")
            self.Printer.conductance_mode = False
            self.Gcode.probe = False
            self.gc_lz_sel.setEnabled(True)
            self.gc_currentlz_btn.setEnabled(True)
            #self.gc_retz_sel.setEnabled(False)
            #self.gc_zoff_sel.setEnabled(False)
            self.Printer.batch = False
        elif self.conductance_mode.isChecked() == True:

            self.Printer.conductance_mode = True
            self.Gcode.probe = True
            self.gc_lz_sel.setEnabled(False)
            self.gc_currentlz_btn.setEnabled(False)
            #self.gc_retz_sel.setEnabled(True)
            #self.gc_zoff_sel.setEnabled(True)
            if self.conThread.flag == False:
                print('connect conductance')

                self.messagebox(typ="startcon", icon="w")
        else:
            self.Gcode.probe = None
    def ref_mode_on_off(self):
        if self.ref_on_off_btn.isChecked():
            self.ref_on_off_btn.setText("Disable") #checked means it is on
            self.Gcode.ref_flag = True
            self.activate_ref_buttons(True)
            self.ref_gcmode()
        
            
        else:
            self.ref_on_off_btn.setText("Enable")
            self.Gcode.ref_flag = False
            self.activate_ref_buttons(False)
            
    
    def activate_ref_buttons(self, toggle):
        self.ref_set_select.setEnabled(toggle)
        self.ref_conductance_select.setEnabled(toggle)
        self.ref_z_lower.setEnabled(toggle)
        
        
        
        self.ref_x_pos.setEnabled(toggle)
        self.ref_y_pos.setEnabled(toggle)
        self.ref_sample.setEnabled(toggle)
        self.ref_dwell.setEnabled(toggle)

    
    def ref_gcmode(self):
        """
        set mode for gcode generator on refrence point
        """
        
        if self.ref_set_select.isChecked() == True:
            self.Gcode.ref_probe = False
            self.ref_z_lower.setEnabled(True)
            self.z_first_rb.setEnabled(True)
        else:
            self.z_last_rb.setChecked(True)
            
            self.z_first_rb.setChecked(False)
            self.z_first_rb.setEnabled(False)
            self.z_first_last()
            self.Gcode.ref_probe = True
            self.ref_z_lower.setEnabled(False)


            
    
    def enable_parameters(self):
        if self.sample_spot_mode.isChecked():
            self.gc_resx_sel.setEnabled(True)
            self.gc_resy_sel.setEnabled(True)
            self.dim_x_sb.setEnabled(True)
            self.dim_y_sb.setEnabled(True)
            self.gc_setx_sel.setEnabled(False)
            self.gc_sety_sel.setEnabled(False)
        elif self.resolution_mode.isChecked():
            self.gc_resx_sel.setEnabled(False)
            self.gc_resy_sel.setEnabled(False)
            self.dim_x_sb.setEnabled(True)
            self.dim_y_sb.setEnabled(True)
            self.gc_setx_sel.setEnabled(True)
            self.gc_sety_sel.setEnabled(True)
        else:
            self.gc_resx_sel.setEnabled(True)
            self.gc_resy_sel.setEnabled(True)
            self.dim_x_sb.setEnabled(False)
            self.dim_y_sb.setEnabled(False)
            self.gc_setx_sel.setEnabled(True)
            self.gc_sety_sel.setEnabled(True)
            
    def ref_end(self):
        if self.ref_end_rb.isChecked():
            self.ref_end_rb.setText("On")
            
            self.Gcode.ref_end_flag = True
            self.Gcode.ref_both_flag = False
        elif self.ref_both_rb.isChecked():
            self.Gcode.ref_both_flag = True
            self.Gcode.ref_end_flag = False
        else:
            self.ref_end_rb.setText("Off")
            self.Gcode.ref_end_flag = False
            self.Gcode.ref_both_flag = False
            
    #Action Buttons for Pump
    
    def z_first_last(self):
        self.Gcode.ref_z_first = self.z_first_rb.isChecked()
        print("Z first: %s" % self.Gcode.ref_z_first)
        
        
        
    def calculate_parameters_sample(self):
        
        
        if self.resolution_mode.isChecked():##change
            
            if self.gc_setx_sel.value() <= 1:
                self.gc_resx_sel.setValue(1)
            else:
                self.gc_resx_sel.setValue(self.dim_x_sb.value() / (self.gc_setx_sel.value() - 1))
            if self.gc_sety_sel.value() <= 1:
                self.gc_resy_sel.setValue(1)
            else:
                self.gc_resy_sel.setValue(self.dim_y_sb.value() / (self.gc_sety_sel.value() - 1))
            
            

        elif self.sample_spot_mode.isChecked():
            if self.gc_resx_sel.value() == 0:
                self.dim_x_sb.setValue(0)
            else:
                self.gc_setx_sel.setValue(math.floor((self.dim_x_sb.value() / self.gc_resx_sel.value()) + 1))
            if self.gc_resy_sel.value() == 0:
                self.dim_y_sb.setValue(0)
            else:
                self.gc_sety_sel.setValue(math.floor((self.dim_y_sb.value() / self.gc_resy_sel.value()) + 1))
        else:
            if self.gc_resx_sel.value() == 0:
                self.dim_x_sb.setValue(0)
            else:
                self.dim_x_sb.setValue((self.gc_resx_sel.value() * (self.gc_setx_sel.value() - 1)))
            if self.gc_resy_sel.value() == 0:
                self.dim_y_sb.setValue(0)
            else:
                self.dim_y_sb.setValue((self.gc_resy_sel.value() * (self.gc_sety_sel.value() - 1)))

            
          
    def puconnect(self):
        """
        action buttons for pump
        """
        self.Pump.Connection.connect(self.pump_com_sel.currentText(), self.pump_baud_sel.currentText())
        if self.Pump.Connection.status:
            self.Pump.Connection.checktype(2)
            if self.Pump.Connection.type=='Command not recognized-type in "help"\r\n':
                print("pump")

                self.Pump.start()
                time.sleep(2)
                self.Pump.startpump()
                self.Printer.pumpstatus=None
                time.sleep(1)
                self.Pump.stoppump()
                self.Pump.setvolume(str(self.pump_v_sel.value()))
                self.Pump.setflowrate(str(self.pump_flowrate_sel.value()))
                self.Pump.setsyringed(str(self.pump_syringed_sel.value()))
                self.Pump.qsampling = str(self.pump_samplingq_sel.value())
                self.Pump.qdwell = str(self.pump_dwellq_sel.value())
            else:
                my_app.messagebox(typ="connectionWrong", icon="w")
                self.Pump.Connection.disconnect()
        else:
            my_app.messagebox(typ="connectionErr", icon="w")
            self.Pump.Connection.disconnect()

        print('clicked')


    def pustart(self):
        """
        start pump
        """
        print(self.Pump.running)

        self.Pump.startpump()
        self.Printer.pumpstatus=None
        self.Pump.running=True

    def pustop(self):
        """stop pump
        """
        print(self.Pump.running)

        self.Pump.stoppump()
        self.Pump.running = False

    def puupdatesamplingq(self):
        """sampling flow rate
        """
        self.Pump.qsampling = self.pump_samplingq_sel.value()
        print(self.Pump.qsampling)
        

    def puupdatedwellq(self):
        """dwell flow rate
        """
        self.Pump.qdwell = self.pump_dwellq_sel.value()
        print(self.Pump.qdwell)
        
    def send_absolute_pos(self):
        """
        send absolute position to printer
        
        """
        
        self.Printer.cmd("G90")
        self.Printer.cmd("G0 X"+str(self.prt_x_val.value())+" Y"+str(self.prt_y_val.value())+" Z"+str(self.prt_z_val.value())+" F2000")


    def update_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_img = q_img.scaled(500, 300, Qt.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(scaled_img))

    def start_camera(self):
        self.camThread.cam_num = self.cam_no_sel.currentText()
        self.camThread.start()

    def start_recording(self):
        if self.camThread.recording:
            self.video_btn.setText("Start Recording")
            self.stop_recording()
        else:
            self.video_btn.setText("Stop Recording")
            self.camThread.start_recording()
            self.recording_symbol.setStyleSheet("background-color: red; border-radius: 15px;")
        

    def stop_recording(self):
        
        self.camThread.stop_recording()
        self.recording_symbol.setStyleSheet("background-color: transparent; border-radius: 15px;")

    def stop_camera(self):
        # Stop the camera thread and release resources
        self.camThread.stop()
        self.video_label.clear()  # Clear the video feed display

    def closeEvent(self, event):
        # Stop the camera thread gracefully
        self.camThread.stop()
        event.accept()
    def pause_video(self):
        if self.camThread.recording:
            self.camThread.pause_recording(False)
            self.pause_vid_btn.setText("Pause")
        else:
            self.camThread.pause_recording(True)
            self.pause_vid_btn.setText("Resume")
            
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_app = MyApp()  # Generate object my_app of class MyApp
    my_app.show()
    sys.exit(app.exec_())