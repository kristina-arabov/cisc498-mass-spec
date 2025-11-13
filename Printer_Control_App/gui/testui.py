from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from pyqtgraph import PlotWidget
import os
from serial.tools import list_ports






# The main window that provides the framework for building oppscan.py's user interface

        
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Get the screen resolution
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Base font sizes for a standard 1920x1080 resolution
        base_font_size = 13
        base_header_font_size = 20

        # Calculate scaling factor based on screen resolution (you can choose width or height for scaling)
        scaling_factor_width =  screen_width / 1920
        scaling_factor_height = screen_height / 1080

        # Use an average of width and height scaling factors or choose one based on preference
        scaling_factor = (scaling_factor_width + scaling_factor_height) / 2

        # Adjust font sizes based on scaling factor
        font_size = int(base_font_size * scaling_factor)
        header_font_size = int(base_header_font_size * scaling_factor)

        # Define styles with dynamic font sizes
        text_style_semibold = f"font: {font_size}pt ; font-weight: 350;"
        text_style_regular = f"font: {font_size}pt ; font-weight: 300;"
        text_style_header = f"font: {header_font_size}pt ; font-weight: 500;"

        blue_button = f"""
            QPushButton {{
                background-color: #1B98E0;  
                color: white;
                font-size: {font_size}px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #0E76B2;  
                color: white;
            }}
            QPushButton:pressed {{
                background-color: #0C5C8A;
                color: white; 
            }}
            QPushButton:disabled {{
                background-color: rgba(27, 152, 224, 0.15);
            }}
        """
        clear_button = f"""
            QPushButton {{
                color: black;
                font-size: {font_size}px;
                border: 2px solid black;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(27, 152, 224, 0.15);
                color: white;
                border: 2px solid #1B98E0;
            }}
            QPushButton:pressed {{
                background-color: #0C5C8A;
                color: white;
                border: 2px solid #4AAEE8; 
            }}
            QPushButton:disabled {{
                background-color: rgba(27, 152, 224, 0.15);
                border: 2px solid rgba(27, 152, 224, 0.15);
            }}
        """
        clear_combobox = f'''
            QComboBox {{
                border: 1px solid black;
                border-radius: 8px;  /* Rounded corners */
                font-size: {font_size}px;
                background-color: white;
                padding-left: 30px;  
                color: black;
                min-height: 30px;  
            }}
            QComboBox::drop-down {{
                border: 0px;
                background: transparent;
                width: 15px;  
            }}
            QComboBox::down-arrow {{
                image: url(gui/images/down-arrow.png);
                height: 20px;
                width: 10px;
            }}
            QComboBox::on {{
                border: 2px solid black;
                background-color: lightgray;
            }}
            QComboBox QListView {{
                border: 1px solid black;
                border-radius: 8px;  
                color: black;
                background-color: #E8F5FC;  
                padding: 5px; 
            }}
            QComboBox QListView::item {{
                padding: 5px;
                background-color: #E8F5FC;  
                color: black; 
            }}
            QComboBox QListView::item:selected {{
                background-color: #d3e0ea;  
                color: black;  
            }}
            QComboBox QListView::item:hover {{
                background-color: #e0e0e0;  
                color: black;  
            }}
        '''
        text_button = f"""
        QPushButton {{
            background-color: transparent;
            color: black;
            font-size: {font_size}px;
        }}
        QPushButton:hover {{
            background-color: transparent;
            color: #1B98E0;
        }}
        """
        tab_style = f"""
            QTabWidget::pane {{
                background-color: #CFE9F7;
                border: none;
                position: absolute;
                top: 0px;
                left: 0px;
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            QTabBar::tab {{
                background: #BECCD1;
                color: black;
                width: {120 * scaling_factor}px;
                height: {38 * scaling_factor}px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                alignment: center;
                border: 2px solid #C2C7CB;
            }}
            QTabBar::tab:hover {{
                background: #949A9C;
            }}
            QTabBar::tab:selected {{
                background: #4AAEE8;
                color: white;
                border-color: #1B98E0; 
                margin-bottom: -2px;
            }}
        """
        radio_button = f""" 
        QRadioButton::indicator {{
            width: {20 * scaling_factor}px;
            height: {20 * scaling_factor}px;
            border-radius: {10 * scaling_factor}px;
        }}
        QRadioButton::indicator::unchecked {{
            border: 1px solid black;
            background-color: white;
        }}
        QRadioButton::indicator::checked {{
            border: 1px solid black;
            background-color: black;
        }}
        """
        doubleSpinBox = f"""
        QDoubleSpinBox {{
            border: 1px solid black;
            border-radius: 8px;
            font-size: {font_size}px;
            background-color: white;
            padding-left: 10px;  
            color: black;
            min-height: {30 * scaling_factor}px;
        }}
        QDoubleSpinBox:focus {{
            outline: none;  
        }}
        QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: {20 * scaling_factor}px;
            border: 1px solid black;
            border-top-right-radius: 8px;
            border-bottom: 1px solid black;
        }}
        QDoubleSpinBox::down-button {{
            width: {20 * scaling_factor}px;
            border: 1px solid black;
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            border-bottom-right-radius: 8px;
            border-top: 1px solid black;
        }}
        QDoubleSpinBox::up-arrow {{
            image: url(gui/images/up-arrow.png);
            width: {10 * scaling_factor}px;
            height: {10 * scaling_factor}px;
        }}
        QDoubleSpinBox::down-arrow {{
            image: url(gui/images/down-arrow.png);
            width: {10 * scaling_factor}px;
            height: {10 * scaling_factor}px;
        }}
        QDoubleSpinBox::up-button:hover{{
            background-color: #F0F4F5;
        }}
        QDoubleSpinBox::down-button:hover{{
            background-color: #F0F4F5;
        }}
        QDoubleSpinBox::disabled {{
            background-color: #F0F4F5;
        }}
        """
        spinBox = f"""
        QSpinBox {{
            border: 1px solid black;
            border-radius: 8px;
            font-size: {font_size}px;
            background-color: white;
            padding-left: 10px;  
            color: black;
            min-height: {30 * scaling_factor}px;
        }}
        QSpinBox:focus {{
            outline: none;
        }}
        QSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: {20 * scaling_factor}px;
            border: 1px solid black;
            border-top-right-radius: 8px;
            border-bottom: 1px solid black;
        }}
        QSpinBox::down-button {{
            width: {20 * scaling_factor}px;
            border: 1px solid black;
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            border-bottom-right-radius: 8px;
            border-top: 1px solid black;
        }}
        QSpinBox::up-arrow {{
            image: url(gui/images/up-arrow.png);
            width: {10 * scaling_factor}px;
            height: {10 * scaling_factor}px;
        }}
        QSpinBox::down-arrow {{
            image: url(gui/images/down-arrow.png);
            width: {10 * scaling_factor}px;
            height: {10 * scaling_factor}px;
        }}
        QSpinBox::up-button:hover{{
            background-color: #F0F4F5;
        }}
        QSpinBox::down-button:hover{{
            background-color: #F0F4F5;
        }}
        QSpinBox::disabled {{
            background-color: #F0F4F5;
        }}
        """
        plus_button = f"""
            QPushButton {{
                border: 3px solid black;
                border-radius: 15px;
                width: {30 * scaling_factor}px;
                height: {30 * scaling_factor}px;
                background-color: white;
                color: black;
                font-size: {font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #F0F4F5;
            }}
            QPushButton:pressed {{
                background-color: #DCE6E9;
            }}
        """
        grey_button = f""" 
        QPushButton {{
            color: white;
            background-color: #465F66;
            border-radius: 8px;
            font-size: {font_size}px;
        }}
        QPushButton:hover {{
            background-color: #30393C;
        }}
        QPushButton:pressed {{
            background-color: #101112;
        }}
        QPushButton:disabled {{
            background-color: #465F66;
        }}
        """
        
        #main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1440, 851)
        MainWindow.setMinimumSize(QtCore.QSize(1440, 851))
        MainWindow.setMaximumSize(QtCore.QSize(1440, 851))
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # Apply the background color to the entire main window
        MainWindow.setStyleSheet("background-color: #F0F4F5;")
        
        
        # Create the printer label
        self.printer_label = QtWidgets.QLabel(self.centralwidget)
        self.printer_label.setGeometry(QtCore.QRect(30, 10, 140, 50))
        self.printer_label.setObjectName("printer_label")
        self.printer_label.setStyleSheet(text_style_header)
        self.printer_label.setText("Printer")
        
        # Create the connect button for printer
        self.prt_con_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_con_btn.setGeometry(QtCore.QRect(30, 73, 140, 40))
        self.prt_con_btn.setObjectName("prt_con_btn")
        self.prt_con_btn.setStyleSheet(blue_button)
        self.prt_con_btn.setText("Connect")
        
        #prt disconnect
        self.prt_discon_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_discon_btn.setGeometry(QtCore.QRect(182, 73, 140, 40))
        self.prt_discon_btn.setObjectName("prt_discon_btn")
        self.prt_discon_btn.setStyleSheet(blue_button)
        self.prt_discon_btn.setText("Disconnect")
        
        #prt status
        self.prt_stat_gv = QtWidgets.QGraphicsView(self.centralwidget)
        self.prt_stat_gv.setGeometry(QtCore.QRect(180,17, 40, 40))
        self.prt_stat_gv.setObjectName("prt_stat_gv")
        self.prt_stat_gv.setStyleSheet("background-color: #E01B24; border-radius: 20px;")
        
        #prt status label
        self.prt_stat_label = QtWidgets.QLabel(self.centralwidget)
        self.prt_stat_label.setGeometry(QtCore.QRect(230, 30, 110, 20))
        self.prt_stat_label.setObjectName("prt_stat_label")
        self.prt_stat_label.setStyleSheet("font: 10pt ; font-weight: semi-bold; color: #E01B24;")
        self.prt_stat_label.setText("Not Connected")

        #prt baud rate
        self.prt_baud_label = QtWidgets.QLabel(self.centralwidget)
        self.prt_baud_label.setGeometry(QtCore.QRect(367,20,59,21)) 
        self.prt_baud_label.setObjectName("prt_baud_label")
        self.prt_baud_label.setStyleSheet(text_style_regular)
        self.prt_baud_label.setText("Baud:")
        
        self.prt_baud_sel = QtWidgets.QComboBox(self.centralwidget)
        self.prt_baud_sel.setGeometry(QtCore.QRect(426, 17, 118, 40))
        self.prt_baud_sel.setObjectName("prt_baud_sel")
        self.prt_baud_sel.setStyleSheet(clear_combobox)

       
        
        #printer port
        self.prt_com_label = QtWidgets.QLabel(self.centralwidget)
        self.prt_com_label.setGeometry(QtCore.QRect(367, 80, 50, 21))
        self.prt_com_label.setObjectName("prt_com_label")
        self.prt_com_label.setStyleSheet(text_style_regular)
        self.prt_com_label.setText("Port:")
        
        self.prt_com_sel = QtWidgets.QComboBox(self.centralwidget)
        self.prt_com_sel.setGeometry(QtCore.QRect(426, 73, 117, 40))
        self.prt_com_sel.setObjectName("prt_com_sel")
        self.prt_com_sel.setStyleSheet(clear_combobox)
        
        self.prt_update_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_update_btn.setGeometry(QtCore.QRect(553, 73, 117, 40))
        self.prt_update_btn.setObjectName("prt_update_btn")
        self.prt_update_btn.setStyleSheet(clear_button)
        self.prt_update_btn.setText("Update")
        
        ##Conductance
        self.cond_label = QtWidgets.QLabel(self.centralwidget)
        self.cond_label.setGeometry(QtCore.QRect(697, 8, 260, 54))
        self.cond_label.setObjectName("cond_label")
        self.cond_label.setStyleSheet(text_style_header)
        self.cond_label.setText("Conductance")
        
        
        self.con_connect_bt = QtWidgets.QPushButton(self.centralwidget)
        self.con_connect_bt.setGeometry(QtCore.QRect(798,71,140,40))
        self.con_connect_bt.setObjectName("con_connect_bt")
        self.con_connect_bt.setStyleSheet(blue_button)
        self.con_connect_bt.setText("Connect")
        
        self.con_disconnect_bt = QtWidgets.QPushButton(self.centralwidget)
        self.con_disconnect_bt.setGeometry(QtCore.QRect(953,71,140,40))
        self.con_disconnect_bt.setObjectName("con_disconnect_bt")
        self.con_disconnect_bt.setStyleSheet(blue_button)
        self.con_disconnect_bt.setText("Disconnect")
        
        self.con_stat_gv = QtWidgets.QGraphicsView(self.centralwidget)
        self.con_stat_gv.setGeometry(QtCore.QRect(950,17, 40, 40))
        self.con_stat_gv.setObjectName("con_stat_gv")
        self.con_stat_gv.setStyleSheet("background-color: #E01B24; border-radius: 20px;")
        
        self.con_stat_label = QtWidgets.QLabel(self.centralwidget)
        self.con_stat_label.setGeometry(QtCore.QRect(1000, 30, 110, 20))
        self.con_stat_label.setObjectName("con_stat_label")
        self.con_stat_label.setStyleSheet("font: 10pt ; font-weight: semibold; color: #E01B24;")
        self.con_stat_label.setText("Not Connected")
        
        self.con_baud_label = QtWidgets.QLabel(self.centralwidget)
        self.con_baud_label.setGeometry(QtCore.QRect(1122,20,59,21))
        self.con_baud_label.setObjectName("con_baud_label")
        self.con_baud_label.setStyleSheet(text_style_regular)
        self.con_baud_label.setText("Baud:")
        
        self.con_baud_sel = QtWidgets.QComboBox(self.centralwidget)
        self.con_baud_sel.setGeometry(QtCore.QRect(1181, 17, 118, 40))
        self.con_baud_sel.setObjectName("con_baud_sel")
        self.con_baud_sel.setStyleSheet(clear_combobox)
        
        self.con_com_label = QtWidgets.QLabel(self.centralwidget)
        self.con_com_label.setGeometry(QtCore.QRect(1122,80,50,21))
        self.con_com_label.setObjectName("con_com_label")
        self.con_com_label.setStyleSheet(text_style_regular)
        self.con_com_label.setText("Port:")
        
        self.con_com_sel = QtWidgets.QComboBox(self.centralwidget)
        self.con_com_sel.setGeometry(QtCore.QRect(1181, 73, 117, 40))
        self.con_com_sel.setObjectName("con_com_sel")
        self.con_com_sel.setStyleSheet(clear_combobox)
        
        self.con_update_btn = QtWidgets.QPushButton(self.centralwidget)
        self.con_update_btn.setGeometry(QtCore.QRect(1308, 73, 117, 40))
        self.con_update_btn.setObjectName("con_update_btn")
        self.con_update_btn.setStyleSheet(clear_button)
        self.con_update_btn.setText("Update")
        
        self.help_bt = QtWidgets.QPushButton(self.centralwidget)
        self.help_bt.setGeometry(QtCore.QRect(1350, 0, 117, 40))
        self.help_bt.setObjectName("help_bt")
        self.help_bt.setStyleSheet(text_button)
        self.help_bt.setText("Help")
        
        self.h_line = QtWidgets.QFrame(self.centralwidget)
        self.h_line.setGeometry(QtCore.QRect(0, 120, 1440, 20))
        self.h_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.h_line.setObjectName("h_line")
        self.h_line.setStyleSheet("color: #465F66;")
        
        
        #setup tabs
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setGeometry(QtCore.QRect(20, 135, 528, 690))
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setStyleSheet(tab_style)
        sample_tab = QtWidgets.QWidget()
        sample_tab.setObjectName("sample_tab")
        sample_tab.setStyleSheet("background-color: #CFE9F7; border-radius: 8px;")
        pump_tab = QtWidgets.QWidget()
        pump_tab.setObjectName("pump_tab")
        pump_tab.setStyleSheet("background-color: #CFE9F7; border-radius: 8px;")
        refrence_tab = QtWidgets.QWidget()
        refrence_tab.setObjectName("refrence_tab")
        refrence_tab.setStyleSheet("background-color: #CFE9F7; border-radius: 8px;")
        terminal_tab = QtWidgets.QWidget()
        terminal_tab.setObjectName("terminal_tab")
        terminal_tab.setStyleSheet("background-color: black; border-radius: 8px;")
        
        self.tabWidget.addTab(sample_tab, "Sampling")
        self.tabWidget.addTab(pump_tab, "Pump")
        self.tabWidget.addTab(refrence_tab, "Reference")
        self.tabWidget.addTab(terminal_tab, "Terminal")
        
        ##################################################################
        #####################     SAMPLING TAB     #######################
        ##################################################################
        
        #start position label
        self.start_pos_label = QtWidgets.QLabel(sample_tab)
        self.start_pos_label.setGeometry(QtCore.QRect(10, 25, 100, 50))
        self.start_pos_label.setObjectName("start_pos_label")
        self.start_pos_label.setStyleSheet(text_style_semibold)
        self.start_pos_label.setText("Start<br>Position:")
        
        self.start_x_label = QtWidgets.QLabel(sample_tab)
        self.start_x_label.setGeometry(QtCore.QRect(172, 10, 15, 20))
        self.start_x_label.setObjectName("start_x_label")
        self.start_x_label.setStyleSheet(text_style_semibold)
        self.start_x_label.setText("X")
        
        self.start_y_label = QtWidgets.QLabel(sample_tab)
        self.start_y_label.setGeometry(QtCore.QRect(288, 10, 15, 20))
        self.start_y_label.setObjectName("start_y_label")
        self.start_y_label.setStyleSheet(text_style_semibold)
        self.start_y_label.setText("Y")
        
        self.start_z_label = QtWidgets.QLabel(sample_tab)
        self.start_z_label.setGeometry(QtCore.QRect(402, 10, 15, 20))
        self.start_z_label.setObjectName("start_z_label")
        self.start_z_label.setStyleSheet(text_style_semibold)
        self.start_z_label.setText("Z")
        
        
        #start position comboboxes
        #set position
        self.gc_startx_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_startx_sel.setGeometry(QtCore.QRect(120, 35, 105, 30))
        self.gc_startx_sel.setObjectName("gc_startx_sel")
        self.gc_startx_sel.setStyleSheet(doubleSpinBox)
        
        self.gc_starty_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_starty_sel.setGeometry(QtCore.QRect(235, 35, 105, 30))
        self.gc_starty_sel.setObjectName("gc_starty_sel")
        self.gc_starty_sel.setStyleSheet(doubleSpinBox)
        
        self.gc_startz_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_startz_sel.setGeometry(QtCore.QRect(350, 35, 105, 30))
        self.gc_startz_sel.setObjectName("gc_startz_sel")
        self.gc_startz_sel.setStyleSheet(doubleSpinBox)
        
        self.start_unit_label = QtWidgets.QLabel(sample_tab)
        self.start_unit_label.setGeometry(QtCore.QRect(465, 35, 40, 30))
        self.start_unit_label.setObjectName("start_unit_label")
        self.start_unit_label.setStyleSheet(text_style_regular)
        self.start_unit_label.setText("mm")
    
    
        #set current position button
        self.gc_currentall_btn = QtWidgets.QPushButton(sample_tab)
        self.gc_currentall_btn.setGeometry(QtCore.QRect(10, 85, 105, 30))
        self.gc_currentall_btn.setObjectName("gc_currentall_btn")
        self.gc_currentall_btn.setStyleSheet(clear_button)
        self.gc_currentall_btn.setText("set all")
        
        self.gc_currentx_btn = QtWidgets.QPushButton(sample_tab)
        self.gc_currentx_btn.setGeometry(QtCore.QRect(120, 85, 105, 30))
        self.gc_currentx_btn.setObjectName("gc_currentx_btn")
        self.gc_currentx_btn.setStyleSheet(clear_button)
        self.gc_currentx_btn.setText("set X")
        
        self.gc_currenty_btn = QtWidgets.QPushButton(sample_tab)
        self.gc_currenty_btn.setGeometry(QtCore.QRect(235, 85, 105, 30))
        self.gc_currenty_btn.setObjectName("gc_currenty_btn")
        self.gc_currenty_btn.setStyleSheet(clear_button)
        self.gc_currenty_btn.setText("set Y")
        
        self.gc_currentz_btn = QtWidgets.QPushButton(sample_tab)
        self.gc_currentz_btn.setGeometry(QtCore.QRect(350, 85, 105, 30))
        self.gc_currentz_btn.setObjectName("gc_currentz_btn")
        self.gc_currentz_btn.setStyleSheet(clear_button)
        self.gc_currentz_btn.setText("set Z")
        
        #sampling spots
        self.sampling_spots_label = QtWidgets.QLabel(sample_tab)
        self.sampling_spots_label.setGeometry(QtCore.QRect(10, 125,100, 50))
        self.sampling_spots_label.setObjectName("sampling_spots_label")
        self.sampling_spots_label.setStyleSheet(text_style_semibold) 
        self.sampling_spots_label.setText("Sampling<br>Spots:")
        
        self.sample_spot_mode = QtWidgets.QRadioButton(sample_tab)
        self.sample_spot_mode.setGeometry(QtCore.QRect(400, 135, 40, 30))
        self.sample_spot_mode.setObjectName("dimension_mode")
        self.sample_spot_mode.setStyleSheet(radio_button)
        
        self.gc_setx_sel = QtWidgets.QSpinBox(sample_tab)
        self.gc_setx_sel.setGeometry(QtCore.QRect(120, 135, 105, 30))
        self.gc_setx_sel.setObjectName("gc_setx_sel")
        self.gc_setx_sel.setStyleSheet(spinBox)
        self.gc_setx_sel.setValue(1)
        self.gc_setx_sel.setMinimum(1)
        
        self.gc_sety_sel = QtWidgets.QSpinBox(sample_tab)
        self.gc_sety_sel.setGeometry(QtCore.QRect(235, 135, 105, 30))
        self.gc_sety_sel.setObjectName("gc_sety_sel")
        self.gc_sety_sel.setStyleSheet(spinBox)
        self.gc_sety_sel.setValue(1)
        self.gc_sety_sel.setMinimum(1)
        
        self.units_label = QtWidgets.QLabel(sample_tab)
        self.units_label.setGeometry(QtCore.QRect(350, 135, 30, 30))
        self.units_label.setObjectName("units_label")
        self.units_label.setStyleSheet(text_style_regular)
        self.units_label.setText("#")
        
        
        
        #resolution
        self.resolution_label = QtWidgets.QLabel(sample_tab)
        self.resolution_label.setGeometry(QtCore.QRect(10, 175, 100, 50))
        self.resolution_label.setObjectName("resolution_label")
        self.resolution_label.setStyleSheet(text_style_semibold)
        self.resolution_label.setText("Resolution:")
        
        self.gc_resx_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_resx_sel.setGeometry(QtCore.QRect(120, 185, 105, 30))
        self.gc_resx_sel.setObjectName("gc_resx_sel")
        self.gc_resx_sel.setStyleSheet(doubleSpinBox)
        
        self.gc_resy_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_resy_sel.setGeometry(QtCore.QRect(235, 185, 105, 30))
        self.gc_resy_sel.setObjectName("gc_resy_sel")
        self.gc_resy_sel.setStyleSheet(doubleSpinBox)
        
        self.resolution_unit_label = QtWidgets.QLabel(sample_tab)
        self.resolution_unit_label.setGeometry(QtCore.QRect(350, 185, 40, 30))
        self.resolution_unit_label.setObjectName("resolution_unit_label")
        self.resolution_unit_label.setStyleSheet(text_style_regular)
        self.resolution_unit_label.setText("mm")
        
        self.resolution_mode = QtWidgets.QRadioButton(sample_tab)
        self.resolution_mode.setGeometry(QtCore.QRect(400, 185, 40, 30))
        self.resolution_mode.setObjectName("resolution_mode")
        self.resolution_mode.setStyleSheet(radio_button)
        
        
        #dimensions
        self.dimensions_label = QtWidgets.QLabel(sample_tab)
        self.dimensions_label.setGeometry(QtCore.QRect(10, 225,100, 50))
        self.dimensions_label.setObjectName("dimensions_label")
        self.dimensions_label.setStyleSheet(text_style_semibold)
        self.dimensions_label.setText("Dimension:")
        
        self.dim_x_sb = QtWidgets.QDoubleSpinBox(sample_tab)
        self.dim_x_sb.setGeometry(QtCore.QRect(120, 235, 105, 30))
        self.dim_x_sb.setObjectName("dim_x_sb")
        self.dim_x_sb.setStyleSheet(doubleSpinBox)
        
        self.dim_y_sb = QtWidgets.QDoubleSpinBox(sample_tab)
        self.dim_y_sb.setGeometry(QtCore.QRect(235, 235, 105, 30))
        self.dim_y_sb.setObjectName("dim_y_sb")
        self.dim_y_sb.setStyleSheet(doubleSpinBox)
        
        self.dim_unit_label = QtWidgets.QLabel(sample_tab)
        self.dim_unit_label.setGeometry(QtCore.QRect(350, 235, 40, 30))
        self.dim_unit_label.setObjectName("dim_unit_label")
        self.dim_unit_label.setStyleSheet(text_style_regular)
        self.dim_unit_label.setText("mm")
        
        self.dimension_mode = QtWidgets.QRadioButton(sample_tab)
        self.dimension_mode.setGeometry(QtCore.QRect(400, 235, 40, 30))
        self.dimension_mode.setObjectName("dimension_mode")
        self.dimension_mode.setStyleSheet(radio_button)
        self.dimension_mode.setChecked(True)
        
        #mode radio group
        self.calculation_mode_group = QtWidgets.QButtonGroup(MainWindow)
        self.calculation_mode_group.setObjectName("calculation_mode_group")
        self.calculation_mode_group.addButton(self.sample_spot_mode)
        self.calculation_mode_group.addButton(self.resolution_mode)
        self.calculation_mode_group.addButton(self.dimension_mode)
        
        #sample and dwell time
        self.sample_time_label = QtWidgets.QLabel(sample_tab)
        self.sample_time_label.setGeometry(QtCore.QRect(10, 275, 100, 50))
        self.sample_time_label.setObjectName("sample_time_label")
        self.sample_time_label.setStyleSheet(text_style_semibold)
        self.sample_time_label.setText("Sample<br>Time:")
        
        self.gc_st_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_st_sel.setGeometry(QtCore.QRect(120, 285, 105, 30))
        self.gc_st_sel.setObjectName("gc_st_sel")
        self.gc_st_sel.setStyleSheet(doubleSpinBox)
        
        self.dwell_time_label = QtWidgets.QLabel(sample_tab)
        self.dwell_time_label.setGeometry(QtCore.QRect(235, 275, 100, 50))
        self.dwell_time_label.setObjectName("dwell_time_label")
        self.dwell_time_label.setStyleSheet(text_style_semibold)
        self.dwell_time_label.setText("Dwell<br>Time:")
        
        self.gc_pause_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_pause_sel.setGeometry(QtCore.QRect(310, 285, 105, 30))
        self.gc_pause_sel.setObjectName("gc_pause_sel")
        self.gc_pause_sel.setStyleSheet(doubleSpinBox)
        
        self.time_unit_label = QtWidgets.QLabel(sample_tab)
        self.time_unit_label.setGeometry(QtCore.QRect(425, 285, 50, 30))
        self.time_unit_label.setObjectName("time_unit_label")
        self.time_unit_label.setStyleSheet(text_style_regular)
        self.time_unit_label.setText("sec")
        
        #speed
        self.z_up_speed_label = QtWidgets.QLabel(sample_tab)
        self.z_up_speed_label.setGeometry(QtCore.QRect(10, 325, 100, 50))
        self.z_up_speed_label.setObjectName("z_up_speed_label")
        self.z_up_speed_label.setStyleSheet(text_style_semibold)
        self.z_up_speed_label.setText("Z Up<br>Speed:")
        
        self.gc_zspeedup_sel = QtWidgets.QSpinBox(sample_tab)
        self.gc_zspeedup_sel.setGeometry(QtCore.QRect(120, 335, 105, 30))
        self.gc_zspeedup_sel.setObjectName("gc_zspeedup_sel")
        self.gc_zspeedup_sel.setStyleSheet(spinBox)
        self.gc_zspeedup_sel.setValue(1)
        self.gc_zspeedup_sel.setMinimum(1)
        
        self.xyspeed_label = QtWidgets.QLabel(sample_tab)
        self.xyspeed_label.setGeometry(QtCore.QRect(235, 325, 100, 50))
        self.xyspeed_label.setObjectName("xyspeed_label")
        self.xyspeed_label.setStyleSheet(text_style_semibold)
        self.xyspeed_label.setText("XY<br>Speed:")
        
        self.gc_speedxy_sel = QtWidgets.QSpinBox(sample_tab)
        self.gc_speedxy_sel.setGeometry(QtCore.QRect(310, 335, 105, 30))
        self.gc_speedxy_sel.setObjectName("gc_speedxy_sel")
        self.gc_speedxy_sel.setStyleSheet(spinBox)
        
        
        self.speed_unit_label = QtWidgets.QLabel(sample_tab)
        self.speed_unit_label.setGeometry(QtCore.QRect(425, 335, 80, 30))
        self.speed_unit_label.setObjectName("speed_unit_label")
        self.speed_unit_label.setStyleSheet(text_style_regular)
        self.speed_unit_label.setText("mm/min")
        
        
        self.gc_flag = QtWidgets.QGraphicsView(sample_tab)
        self.gc_flag.setGeometry(QtCore.QRect(350, 405, 40, 40))
        self.gc_flag.setObjectName("gc_flag")
        self.gc_flag.setStyleSheet("background-color: #1BE03F; border-radius: 20px;")
        
        self.ready_label = QtWidgets.QLabel(sample_tab)
        self.ready_label.setGeometry(QtCore.QRect(400, 405, 110, 30))
        self.ready_label.setObjectName("ready_label")
        self.ready_label.setStyleSheet(text_style_regular)
        self.ready_label.setText("Ready")
        
        self.z_down_speed_label = QtWidgets.QLabel(sample_tab)
        self.z_down_speed_label.setGeometry(QtCore.QRect(10, 375, 100, 50))
        self.z_down_speed_label.setObjectName("z_down_speed_label")
        self.z_down_speed_label.setStyleSheet(text_style_semibold)
        self.z_down_speed_label.setText("Z Down<br>Speed:")

        
        self.gc_zspeed_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_zspeed_sel.setGeometry(QtCore.QRect(120, 385, 105, 30))
        self.gc_zspeed_sel.setObjectName("gc_zspeed_sel")
        self.gc_zspeed_sel.setStyleSheet(doubleSpinBox)
        self.gc_zspeed_sel.setValue(50)
        self.gc_zspeed_sel.setMinimum(1)
        self.gc_zspeed_sel.setMaximum(10000)
        
        self.z_down_speed_unti_label = QtWidgets.QLabel(sample_tab)
        self.z_down_speed_unti_label.setGeometry(QtCore.QRect(235, 375, 100, 50))
        self.z_down_speed_unti_label.setObjectName("z_down_speed_unti_label")
        self.z_down_speed_unti_label.setStyleSheet(text_style_semibold)
        self.z_down_speed_unti_label.setText("mm/min")
        
        #step size
        self.step_size_label = QtWidgets.QLabel(sample_tab)
        self.step_size_label.setGeometry(QtCore.QRect(260, 475, 100, 50))
        self.step_size_label.setObjectName("step_size_label")
        self.step_size_label.setStyleSheet(text_style_semibold)
        self.step_size_label.setText("Step<br>Size:")
        
        self.gc_step_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_step_sel.setGeometry(QtCore.QRect(325, 475, 105, 30))
        self.gc_step_sel.setObjectName("gc_step_sel")
        self.gc_step_sel.setStyleSheet(doubleSpinBox)

        
        self.step_size_units_label = QtWidgets.QLabel(sample_tab)
        self.step_size_units_label.setGeometry(QtCore.QRect(435, 475, 80, 30))
        self.step_size_units_label.setObjectName("step_size_units_label")
        self.step_size_units_label.setStyleSheet(text_style_semibold)
        self.step_size_units_label.setText("mm")
        
        
        
        
        #sample mode
        self.conductance_mode = QtWidgets.QRadioButton(sample_tab)
        self.conductance_mode.setGeometry(QtCore.QRect(210, 475, 30, 50))
        self.conductance_mode.setObjectName("constant_z_mode")
        self.conductance_mode.setStyleSheet(radio_button)
        
        self.gc_modetrue_label = QtWidgets.QLabel(sample_tab)
        self.gc_modetrue_label.setGeometry(QtCore.QRect(10, 475, 200, 50))
        self.gc_modetrue_label.setObjectName("gc_modetrue_label")
        self.gc_modetrue_label.setStyleSheet(text_style_semibold)
        self.gc_modetrue_label.setText("Conductance Mode:")
        
        self.constant_z_mode = QtWidgets.QRadioButton(sample_tab)
        self.constant_z_mode.setGeometry(QtCore.QRect(210, 525, 30, 50))
        self.constant_z_mode.setObjectName("conductance_mode")
        self.constant_z_mode.setStyleSheet(radio_button)
        self.constant_z_mode.setChecked(True)
        
        self.mode_true_label = QtWidgets.QLabel(sample_tab)
        self.mode_true_label.setGeometry(QtCore.QRect(10, 525, 200, 50))
        self.mode_true_label.setObjectName("mode_true_label")
        self.mode_true_label.setStyleSheet(text_style_semibold)
        self.mode_true_label.setText("Constant Z Mode:")
        
        self.z_lower_label = QtWidgets.QLabel(sample_tab)
        self.z_lower_label.setGeometry(QtCore.QRect(235, 525, 100, 50))
        self.z_lower_label.setObjectName("z_lower_label")
        self.z_lower_label.setStyleSheet(text_style_semibold)
        self.z_lower_label.setText("Sample Z:")
        
        self.gc_lz_sel = QtWidgets.QDoubleSpinBox(sample_tab)
        self.gc_lz_sel.setGeometry(QtCore.QRect(325, 535, 105, 30))
        self.gc_lz_sel.setObjectName("gc_lz_sel")
        self.gc_lz_sel.setStyleSheet(doubleSpinBox)
        self.gc_lz_sel.setMaximum(180)
        
        
        self.gc_currentlz_btn = QtWidgets.QPushButton(sample_tab)
        self.gc_currentlz_btn.setGeometry(QtCore.QRect(435, 535, 80, 30))
        self.gc_currentlz_btn.setObjectName("gc_currentlz_btn")
        self.gc_currentlz_btn.setStyleSheet(clear_button)
        self.gc_currentlz_btn.setText("set Z")
   
   
        #sample mode button group
        self.sample_mode_group = QtWidgets.QButtonGroup(MainWindow)
        self.sample_mode_group.setObjectName("sample_mode_group")
        self.sample_mode_group.addButton(self.constant_z_mode)
        self.sample_mode_group.addButton(self.conductance_mode)
   
        #start run and file name
        self.gc_filename_txt = QtWidgets.QLineEdit(sample_tab)
        self.gc_filename_txt.setGeometry(QtCore.QRect(10, 575, 200, 30))
        self.gc_filename_txt.setObjectName("gc_filename_txt")
        self.gc_filename_txt.setStyleSheet("font: 16pt ; font-weight: regular; background-color: white; border: 1px solid black; border-radius: 10px; color: black; text-align: center;")
        self.gc_filename_txt.setPlaceholderText("File Name:")

        self.gc_gen_btn = QtWidgets.QPushButton(sample_tab)
        self.gc_gen_btn.setGeometry(QtCore.QRect(10, 610, 200, 30))
        self.gc_gen_btn.setObjectName("gc_gen_btn")
        self.gc_gen_btn.setStyleSheet(blue_button)
        self.gc_gen_btn.setText("Send Gcode")
        
        self.prt_startrun_btn = QtWidgets.QPushButton(sample_tab)
        self.prt_startrun_btn.setGeometry(QtCore.QRect(320, 575, 200, 65))
        self.prt_startrun_btn.setObjectName("prt_startrun_btn")
        self.prt_startrun_btn.setStyleSheet(blue_button)
        self.prt_startrun_btn.setText("Start Run")
                
        # coordinates
        self.coordinates_label = QtWidgets.QLabel(self.centralwidget)
        self.coordinates_label.setGeometry(QtCore.QRect(555, 135, 320, 50))
        self.coordinates_label.setObjectName("coordinates_label")
        self.coordinates_label.setStyleSheet("font: 22pt ; font-weight: semi-bold; text-decoration: underline;")
        self.coordinates_label.setText("Coordinates (mm): ")
        
        

        self.x_cord_label = QtWidgets.QLabel(self.centralwidget)
        self.x_cord_label.setGeometry(QtCore.QRect(571, 200, 100, 50))
        self.x_cord_label.setObjectName("x_cord_label")
        self.x_cord_label.setStyleSheet("font: 20pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        self.x_cord_label.setText("X")

        self.y_cord_label = QtWidgets.QLabel(self.centralwidget)
        self.y_cord_label.setGeometry(QtCore.QRect(671, 200, 100, 50))
        self.y_cord_label.setObjectName("y_cord_label")
        self.y_cord_label.setStyleSheet("font: 20pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        self.y_cord_label.setText("Y")

        
        self.z_cord_label = QtWidgets.QLabel(self.centralwidget)
        self.z_cord_label.setGeometry(QtCore.QRect(771, 200, 100, 50))
        self.z_cord_label.setObjectName("z_cord_label")
        self.z_cord_label.setStyleSheet("font: 20pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        self.z_cord_label.setText("Z")
        
        self.prt_x_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.prt_x_lcd.setGeometry(QtCore.QRect(571, 250, 100, 50))
        self.prt_x_lcd.setObjectName("prt_x_lcd")
        self.prt_x_lcd.setStyleSheet("background-color: white; color: black;")
        
        self.prt_y_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.prt_y_lcd.setGeometry(QtCore.QRect(671, 250, 100, 50))
        self.prt_y_lcd.setObjectName("prt_y_lcd")
        self.prt_y_lcd.setStyleSheet("background-color: white; color: black;")
        
        self.prt_z_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.prt_z_lcd.setGeometry(QtCore.QRect(771, 250, 100, 50))
        self.prt_z_lcd.setObjectName("prt_z_lcd")
        self.prt_z_lcd.setStyleSheet("background-color: white; color: black;")
        
        
        #plus and minus buttons
        self.prt_xn_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_xn_btn.setGeometry(QtCore.QRect(576, 310, 30, 30))
        self.prt_xn_btn.setObjectName("prt_xn_btn")
        self.prt_xn_btn.setStyleSheet(plus_button)
        self.prt_xn_btn.setText("-")
        
        self.prt_xp_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_xp_btn.setGeometry(QtCore.QRect(636, 310, 30, 30))
        self.prt_xp_btn.setObjectName("prt_xp_btn")
        self.prt_xp_btn.setStyleSheet(plus_button)
        self.prt_xp_btn.setText("+")

        self.prt_yn_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_yn_btn.setGeometry(QtCore.QRect(676, 310, 30, 30))
        self.prt_yn_btn.setObjectName("prt_yn_btn")
        self.prt_yn_btn.setStyleSheet(plus_button)
        self.prt_yn_btn.setText("-")
        
        self.prt_yp_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_yp_btn.setGeometry(QtCore.QRect(736, 310, 30, 30))
        self.prt_yp_btn.setObjectName("prt_yp_btn")
        self.prt_yp_btn.setStyleSheet(plus_button)
        self.prt_yp_btn.setText("+")
        
        self.prt_zn_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_zn_btn.setGeometry(QtCore.QRect(776, 310, 30, 30))
        self.prt_zn_btn.setObjectName("prt_zn_btn")
        self.prt_zn_btn.setStyleSheet(plus_button)
        self.prt_zn_btn.setText("-")
        
        self.prt_zp_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_zp_btn.setGeometry(QtCore.QRect(836, 310, 30, 30))
        self.prt_zp_btn.setObjectName("prt_zp_btn")
        self.prt_zp_btn.setStyleSheet(plus_button)
        self.prt_zp_btn.setText("+")
        
        
        #values for change and absolute coordinates
        self.prt_x_val = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.prt_x_val.setGeometry(QtCore.QRect(576, 350, 90, 30))
        self.prt_x_val.setObjectName("prt_x_val")
        self.prt_x_val.setStyleSheet(doubleSpinBox)
        self.prt_x_val.setMaximum(190)
        
        self.prt_y_val = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.prt_y_val.setGeometry(QtCore.QRect(676, 350, 90, 30))
        self.prt_y_val.setObjectName("prt_y_val")
        self.prt_y_val.setStyleSheet(doubleSpinBox)
        self.prt_y_val.setMaximum(190)
        
        self.prt_z_val = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.prt_z_val.setGeometry(QtCore.QRect(776, 350, 90, 30))
        self.prt_z_val.setObjectName("prt_z_val")
        self.prt_z_val.setStyleSheet(doubleSpinBox)
        self.prt_z_val.setMaximum(190)
        
        self.send_btn = QtWidgets.QPushButton(self.centralwidget)
        self.send_btn.setGeometry(QtCore.QRect(576, 390, 290, 40))
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setStyleSheet(grey_button)
        self.send_btn.setText("Send Absolute Coordinates")
        
        self.prt_home_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_home_btn.setGeometry(QtCore.QRect(576, 440, 143, 40))
        self.prt_home_btn.setObjectName("prt_home_btn")
        self.prt_home_btn.setStyleSheet(blue_button)
        self.prt_home_btn.setText("Home")

        self.prt_home_stat_gv = QtWidgets.QGraphicsView(self.centralwidget)
        self.prt_home_stat_gv.setGeometry(QtCore.QRect(731, 440, 40, 40))
        self.prt_home_stat_gv.setObjectName("prt_home_stat_gv")
        self.prt_home_stat_gv.setStyleSheet("background-color: #E01B24; border-radius: 20px;")
        
        self.prt_home_label = QtWidgets.QLabel(self.centralwidget)
        self.prt_home_label.setGeometry(QtCore.QRect(781, 450, 100, 20))
        self.prt_home_label.setObjectName("prt_home_label")
        self.prt_home_label.setStyleSheet("font: 10pt ; font-weight: semibold; color: #E01B24;")
        self.prt_home_label.setText("Not Homed")
        
        self.prt_pause_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_pause_btn.setGeometry(QtCore.QRect(576, 490, 143, 40))
        self.prt_pause_btn.setObjectName("prt_pause_btn")
        self.prt_pause_btn.setStyleSheet(blue_button)
        self.prt_pause_btn.setText("Pause")
        
        self.prt_stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prt_stop_btn.setGeometry(QtCore.QRect(722, 490, 143, 40))
        self.prt_stop_btn.setObjectName("prt_stop_btn")
        self.prt_stop_btn.setStyleSheet(blue_button)
        self.prt_stop_btn.setText("Stop")
        
        self.temp_label = QtWidgets.QLabel(self.centralwidget)
        self.temp_label.setGeometry(QtCore.QRect(555, 530, 305, 50))
        self.temp_label.setObjectName("temp_label")
        self.temp_label.setStyleSheet("font: 22pt ; font-weight: semi-bold; text-decoration: underline;")
        self.temp_label.setText("Temperature(˚C):")
    
        self.bed_temp_label = QtWidgets.QLabel(self.centralwidget)
        self.bed_temp_label.setGeometry(QtCore.QRect(576, 600, 140, 50))
        self.bed_temp_label.setObjectName("bed_temp_label")
        self.bed_temp_label.setStyleSheet("font: 20pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        self.bed_temp_label.setText("Bed")
        
        self.extruder_temp_label = QtWidgets.QLabel(self.centralwidget)
        self.extruder_temp_label.setGeometry(QtCore.QRect(726, 600, 145, 50))
        self.extruder_temp_label.setObjectName("extruder_temp_label")
        self.extruder_temp_label.setStyleSheet("font: 20pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        self.extruder_temp_label.setText("Extruder")
        
        self.prt_bed_temp_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.prt_bed_temp_lcd.setGeometry(QtCore.QRect(576, 650, 140, 50))
        self.prt_bed_temp_lcd.setObjectName("prt_bed_temp_lcd")
        self.prt_bed_temp_lcd.setStyleSheet("background-color: white; color: black;")
        
        self.prt_nozzel_temp_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.prt_nozzel_temp_lcd.setGeometry(QtCore.QRect(726, 650, 140, 50))
        self.prt_nozzel_temp_lcd.setObjectName("prt_nozzel_temp_lcd")
        self.prt_nozzel_temp_lcd.setStyleSheet("background-color: white; color: black;")

        self.prt_bed_temp_sb = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.prt_bed_temp_sb.setGeometry(QtCore.QRect(576, 710, 140, 30))
        self.prt_bed_temp_sb.setObjectName("prt_bed_temp_sb")
        self.prt_bed_temp_sb.setStyleSheet(doubleSpinBox)
        
        self.prt_nozzel_temp_sb = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.prt_nozzel_temp_sb.setGeometry(QtCore.QRect(726, 710, 140, 30))
        self.prt_nozzel_temp_sb.setObjectName("prt_nozzel_temp_sb")
        self.prt_nozzel_temp_sb.setStyleSheet(doubleSpinBox)
        
        self.temp_start_btn = QtWidgets.QPushButton(self.centralwidget)
        self.temp_start_btn.setGeometry(QtCore.QRect(576, 750, 290, 40))
        self.temp_start_btn.setObjectName("temp_start_btn")
        self.temp_start_btn.setStyleSheet(grey_button)
        self.temp_start_btn.setText("Set Temperature")
        
        
        #conduction
        self.conduction_label = QtWidgets.QLabel(self.centralwidget)
        self.conduction_label.setGeometry(QtCore.QRect(1065, 135, 220, 50))
        self.conduction_label.setObjectName("conduction_label")
        self.conduction_label.setStyleSheet("font: 22pt ; font-weight: semi-bold; text-decoration: underline;")
        self.conduction_label.setText("Conductance:")
        
        self.lower_threshold_label = QtWidgets.QLabel(self.centralwidget)
        self.lower_threshold_label.setGeometry(QtCore.QRect(1210, 200, 150,30))
        self.lower_threshold_label.setObjectName("lower_threshold_label")
        self.lower_threshold_label.setStyleSheet("font: 10pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        self.lower_threshold_label.setText("Low Threshold:")
        
        self.lower_threshold = QtWidgets.QSpinBox(self.centralwidget)
        self.lower_threshold.setGeometry(QtCore.QRect(1360, 200, 60, 30))
        self.lower_threshold.setObjectName("lower_threshold")
        self.lower_threshold.setStyleSheet(spinBox)
        self.lower_threshold.setValue(0)
        self.lower_threshold.setMaximum(1023)
        
        #conduction graph
        self.graphicsCap = PlotWidget(self.centralwidget)
        self.graphicsCap.setGeometry(QtCore.QRect(890, 232, 530, 220))
        self.graphicsCap.setObjectName("graphicsCap")
        
        self.conThread_start_btn = QtWidgets.QPushButton(self.centralwidget)
        self.conThread_start_btn.setGeometry(QtCore.QRect(890, 452, 100, 30))
        self.conThread_start_btn.setObjectName("conThread_start_btn")
        self.conThread_start_btn.setStyleSheet(blue_button)
        self.conThread_start_btn.setText("Start")
        
        self.conThread_stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.conThread_stop_btn.setGeometry(QtCore.QRect(991, 452, 100, 30))
        self.conThread_stop_btn.setObjectName("conThread_stop_btn")
        self.conThread_stop_btn.setStyleSheet(blue_button)
        self.conThread_stop_btn.setText("Stop")
        
        self.conThread_save_btn = QtWidgets.QPushButton(self.centralwidget)
        self.conThread_save_btn.setGeometry(QtCore.QRect(1092, 452, 100, 30))
        self.conThread_save_btn.setObjectName("conThread_save_btn")
        self.conThread_save_btn.setStyleSheet(clear_button)
        self.conThread_save_btn.setText("Save")
        
        
        self.scale_label = QtWidgets.QLabel(self.centralwidget)
        self.scale_label.setGeometry(QtCore.QRect(1290, 452, 111, 20))
        self.scale_label.setObjectName("scale_label")
        self.scale_label.setText("Scale")
    
        self.conPltRange = QtWidgets.QSlider(self.centralwidget)
        self.conPltRange.setGeometry(QtCore.QRect(1245, 472, 175, 20))
        self.conPltRange.setMinimum(1)
        self.conPltRange.setMaximum(180)
        self.conPltRange.setPageStep(60)
        self.conPltRange.setSliderPosition(180)
        self.conPltRange.setOrientation(QtCore.Qt.Horizontal)
        self.conPltRange.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.conPltRange.setTickInterval(60)
        self.conPltRange.setObjectName("conPltRange")
        
        self.zero_at_label = QtWidgets.QLabel(self.centralwidget)
        self.zero_at_label.setGeometry(QtCore.QRect(890, 200, 70, 30))
        self.zero_at_label.setObjectName("zero_at_label")
        self.zero_at_label.setText("Zero at:")
        self.zero_at_label.setStyleSheet("font: 10pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        
        self.con_zero_btn = QtWidgets.QSpinBox(self.centralwidget)
        self.con_zero_btn.setGeometry(QtCore.QRect(960, 200, 75, 20))
        self.con_zero_btn.setObjectName("con_zero_btn")
        self.con_zero_btn.setStyleSheet(spinBox)
        
        self.threshold_label = QtWidgets.QLabel(self.centralwidget)
        self.threshold_label.setGeometry(QtCore.QRect(1037, 200, 100, 30))
        self.threshold_label.setObjectName("threshold_label")
        self.threshold_label.setText("Threshold:")
        self.threshold_label.setStyleSheet("font: 10pt ; font-weight: semi-bold; qproperty-alignment: 'AlignCenter';")
        
        self.con_threshold_sp = QtWidgets.QSpinBox(self.centralwidget)
        self.con_threshold_sp.setGeometry(QtCore.QRect(1135, 200, 75, 30))
        self.con_threshold_sp.setObjectName("con_threshold_sp")
        self.con_threshold_sp.setStyleSheet(spinBox)
       
        
        ##################################################
        #####################     CAMERA     #############
        ##################################################
        
        self.cameras_label = QtWidgets.QLabel(self.centralwidget)
        self.cameras_label.setGeometry(QtCore.QRect(1094, 483, 200, 50))
        self.cameras_label.setObjectName("cameras_label")
        self.cameras_label.setStyleSheet("font: 22pt ; font-weight: semi-bold; text-decoration: underline;")
        self.cameras_label.setText("Camera:")
        
        self.camThread_start_btn = QtWidgets.QPushButton(self.centralwidget)
        self.camThread_start_btn.setGeometry(QtCore.QRect(890, 533, 125, 30))
        self.camThread_start_btn.setObjectName("camThread_start_btn")
        self.camThread_start_btn.setStyleSheet(blue_button)
        self.camThread_start_btn.setText("Connect")
        
        self.camThread_stop_btn = QtWidgets.QPushButton(self.centralwidget)
        self.camThread_stop_btn.setGeometry(QtCore.QRect(1016, 533, 125, 30))
        self.camThread_stop_btn.setObjectName("camThread_stop_btn")
        self.camThread_stop_btn.setStyleSheet(blue_button)
        self.camThread_stop_btn.setText("Disconnect")
        
        self.cam_number_label = QtWidgets.QLabel(self.centralwidget)
        self.cam_number_label.setGeometry(QtCore.QRect(1220, 533, 100, 30))
        self.cam_number_label.setObjectName("cam_number_label")
        self.cam_number_label.setStyleSheet("font: 15pt ; font-weight: semi-bold; text-decoration: underline;")
        self.cam_number_label.setText("Camera:")
        
        self.cam_no_sel = QtWidgets.QComboBox(self.centralwidget)
        self.cam_no_sel.setGeometry(QtCore.QRect(1320, 533, 100, 30))
        self.cam_no_sel.setObjectName("cam_no_sel")
        self.cam_no_sel.setStyleSheet(clear_combobox)
        self.cam_no_sel.addItem("")
        self.cam_no_sel.addItem("")
        self.cam_no_sel.addItem("")
        
        
        self.video_label = QtWidgets.QLabel(self.centralwidget)
        self.video_label.setGeometry(QtCore.QRect(905, 569,500 , 219))
        self.video_label.setObjectName("video_label")
        self.video_label.setStyleSheet("background-color: white; border: 1px solid black; border-radius: 10px;")

        self.photo_btn = QtWidgets.QPushButton(self.centralwidget)
        self.photo_btn.setGeometry(QtCore.QRect(905, 790, 150, 30))
        self.photo_btn.setObjectName("photo_btn")
        self.photo_btn.setStyleSheet(clear_button)
        self.photo_btn.setText("Take Photo")
        
        self.video_btn = QtWidgets.QPushButton(self.centralwidget)
        self.video_btn.setGeometry(QtCore.QRect(1057,790, 150, 30))
        self.video_btn.setObjectName("video_btn")
        self.video_btn.setStyleSheet(clear_button)
        self.video_btn.setText("Start Video")
        
        self.pause_vid_btn = QtWidgets.QPushButton(self.centralwidget)
        self.pause_vid_btn.setGeometry(QtCore.QRect(1209, 790, 150, 30))
        self.pause_vid_btn.setObjectName("pause_vid_btn")
        self.pause_vid_btn.setStyleSheet(clear_button)
        self.pause_vid_btn.setText("Pause")
        
        self.recording_symbol = QtWidgets.QGraphicsView(self.centralwidget)
        self.recording_symbol.setGeometry(QtCore.QRect(1361, 602, 30, 30))
        self.recording_symbol.setObjectName("recording_symbol")
        self.recording_symbol.setStyleSheet("background-color: transparent; border-radius: 15px;")
        #refrence tab
        self.ref_on_off_btn = QtWidgets.QPushButton(refrence_tab)
        self.ref_on_off_btn.setGeometry(QtCore.QRect(164, 10, 200, 30))
        self.ref_on_off_btn.setObjectName("ref_on_off_btn")
        self.ref_on_off_btn.setStyleSheet(blue_button)
        self.ref_on_off_btn.setText("Start")
        self.ref_on_off_btn.setCheckable(True)
        self.ref_on_off_btn.setChecked(False)
        
        
        self.ref_set_select = QtWidgets.QRadioButton(refrence_tab)
        self.ref_set_select.setGeometry(QtCore.QRect(10, 50, 40, 30))
        self.ref_set_select.setObjectName("ref_set_select")
        self.ref_set_select.setStyleSheet(radio_button)
        self.ref_set_select.setChecked(True)
        
        self.ref_set_label = QtWidgets.QLabel(refrence_tab)
        self.ref_set_label.setGeometry(QtCore.QRect(50, 50, 200, 30))
        self.ref_set_label.setObjectName("ref_set_label")
        self.ref_set_label.setStyleSheet(text_style_semibold)
        self.ref_set_label.setText("Constant Z Mode")
        
        self.ref_conductance_select = QtWidgets.QRadioButton(refrence_tab)
        self.ref_conductance_select.setGeometry(QtCore.QRect(10, 90, 40, 30))
        self.ref_conductance_select.setObjectName("ref_conductance_select")
        self.ref_conductance_select.setStyleSheet(radio_button)
        
        self.ref_conductance_label = QtWidgets.QLabel(refrence_tab)
        self.ref_conductance_label.setGeometry(QtCore.QRect(50, 90, 200, 30))
        self.ref_conductance_label.setObjectName("ref_conductance_label")
        self.ref_conductance_label.setStyleSheet(text_style_semibold)
        self.ref_conductance_label.setText("Conductance Mode")
        
        self.ref_mode_group = QtWidgets.QButtonGroup(refrence_tab)
        self.ref_mode_group.setObjectName("ref_mode_group")
        self.ref_mode_group.addButton(self.ref_set_select)
        self.ref_mode_group.addButton(self.ref_conductance_select)
        
        
        self.z_lower_ref_label = QtWidgets.QLabel(refrence_tab)
        self.z_lower_ref_label.setGeometry(QtCore.QRect(10, 130, 200, 30))
        self.z_lower_ref_label.setObjectName("z_lower_ref_label")
        self.z_lower_ref_label.setStyleSheet(text_style_semibold)
        self.z_lower_ref_label.setText("Sample Z:")
        
        self.ref_z_lower = QtWidgets.QDoubleSpinBox(refrence_tab)   
        self.ref_z_lower.setGeometry(QtCore.QRect(120, 130, 105, 30))
        self.ref_z_lower.setObjectName("ref_z_lower")
        self.ref_z_lower.setStyleSheet(doubleSpinBox)
        
        self.x_cord_ref_label = QtWidgets.QLabel(refrence_tab)
        self.x_cord_ref_label.setGeometry(QtCore.QRect(10, 170, 20, 30))
        self.x_cord_ref_label.setObjectName("x_cord_ref_label")
        self.x_cord_ref_label.setStyleSheet(text_style_semibold)
        self.x_cord_ref_label.setText("X:")
        
        self.ref_x_pos = QtWidgets.QDoubleSpinBox(refrence_tab)
        self.ref_x_pos.setGeometry(QtCore.QRect(35, 170, 105, 30))
        self.ref_x_pos.setObjectName("ref_x_pos")
        self.ref_x_pos.setStyleSheet(doubleSpinBox)
        
        self.y_cord_ref_label = QtWidgets.QLabel(refrence_tab)
        self.y_cord_ref_label.setGeometry(QtCore.QRect(10, 210, 20, 30))
        self.y_cord_ref_label.setObjectName("y_cord_ref_label")
        self.y_cord_ref_label.setStyleSheet(text_style_semibold)
        self.y_cord_ref_label.setText("Y:") 
        
        self.ref_y_pos = QtWidgets.QDoubleSpinBox(refrence_tab)
        self.ref_y_pos.setGeometry(QtCore.QRect(35, 210, 105, 30))
        self.ref_y_pos.setObjectName("ref_y_pos")
        self.ref_y_pos.setStyleSheet(doubleSpinBox)
        
        self.ref_dwell_label = QtWidgets.QLabel(refrence_tab)
        self.ref_dwell_label.setGeometry(QtCore.QRect(10, 250, 150, 30))
        self.ref_dwell_label.setObjectName("ref_dwell_label")
        self.ref_dwell_label.setStyleSheet(text_style_semibold)
        self.ref_dwell_label.setText("Dwell Time:")
        
        self.ref_dwell = QtWidgets.QDoubleSpinBox(refrence_tab)
        self.ref_dwell.setGeometry(QtCore.QRect(150, 250, 105, 30))
        self.ref_dwell.setObjectName("ref_dwell")
        self.ref_dwell.setStyleSheet(doubleSpinBox)
        
        self.ref_sample_label = QtWidgets.QLabel(refrence_tab)
        self.ref_sample_label.setGeometry(QtCore.QRect(10, 290, 150, 30))
        self.ref_sample_label.setObjectName("ref_sample_label")
        self.ref_sample_label.setStyleSheet(text_style_semibold)
        self.ref_sample_label.setText("Sample Time:")
        
        self.ref_sample = QtWidgets.QDoubleSpinBox(refrence_tab)
        self.ref_sample.setGeometry(QtCore.QRect(150, 290, 105, 30))
        self.ref_sample.setObjectName("ref_sample")
        self.ref_sample.setStyleSheet(doubleSpinBox)
        
        self.ref_end_label = QtWidgets.QLabel(refrence_tab)
        self.ref_end_label.setGeometry(QtCore.QRect(10, 330, 150, 80))
        self.ref_end_label.setObjectName("ref_end_label")
        self.ref_end_label.setStyleSheet(text_style_semibold)
        self.ref_end_label.setText("Refrence<br> at End:")
        
        self.ref_start_label = QtWidgets.QLabel(refrence_tab)
        self.ref_start_label.setGeometry(QtCore.QRect(10, 400, 150, 80))
        self.ref_start_label.setObjectName("ref_start_label")
        self.ref_start_label.setStyleSheet(text_style_semibold)
        self.ref_start_label.setText("Refrence<br> at Start:")
        
        self.ref_end_rb = QtWidgets.QRadioButton(refrence_tab)
        self.ref_end_rb.setGeometry(QtCore.QRect(150, 330, 40, 50))
        self.ref_end_rb.setObjectName("ref_end_rb")
        self.ref_end_rb.setStyleSheet(radio_button)
        
        self.ref_start_rb = QtWidgets.QRadioButton(refrence_tab)
        self.ref_start_rb.setGeometry(QtCore.QRect(150, 400, 40, 50))
        self.ref_start_rb.setObjectName("ref_start_rb")
        self.ref_start_rb.setStyleSheet(radio_button)
        self.ref_start_rb.setChecked(True)    
        
        self.ref_both_rb = QtWidgets.QRadioButton(refrence_tab)
        self.ref_both_rb.setGeometry(QtCore.QRect(150, 450, 40, 50))
        self.ref_both_rb.setObjectName("ref_both_rb")
        self.ref_both_rb.setStyleSheet(radio_button)
        
        self.ref_both_label = QtWidgets.QLabel(refrence_tab)
        self.ref_both_label.setGeometry(QtCore.QRect(10, 470, 130, 30))
        self.ref_both_label.setObjectName("ref_both_label")
        self.ref_both_label.setStyleSheet(text_style_semibold)
        self.ref_both_label.setText("Both:")
        
        self.ref_rb_group = QtWidgets.QButtonGroup()
        self.ref_rb_group.addButton(self.ref_end_rb)
        self.ref_rb_group.addButton(self.ref_start_rb)
        self.ref_rb_group.addButton(self.ref_both_rb)
    
        #z first and z last
        self.z_first_label = QtWidgets.QLabel(refrence_tab)
        self.z_first_label.setGeometry(QtCore.QRect(10, 520, 150, 30))
        self.z_first_label.setObjectName("z_first_label")
        self.z_first_label.setStyleSheet(text_style_semibold)
        self.z_first_label.setText("Z First:")
        
        self.z_first_rb = QtWidgets.QRadioButton(refrence_tab)
        self.z_first_rb.setGeometry(QtCore.QRect(150, 520, 40, 50))
        self.z_first_rb.setObjectName("z_first_rb")
        self.z_first_rb.setStyleSheet(radio_button)
        
        
        self.z_last_label = QtWidgets.QLabel(refrence_tab)
        self.z_last_label.setGeometry(QtCore.QRect(10, 570, 150, 30))
        self.z_last_label.setObjectName("z_last_label")
        self.z_last_label.setStyleSheet(text_style_semibold)
        self.z_last_label.setText("Z Last:")
        
        self.z_last_rb = QtWidgets.QRadioButton(refrence_tab)
        self.z_last_rb.setGeometry(QtCore.QRect(150, 570, 40, 50))
        self.z_last_rb.setObjectName("z_last_rb")
        self.z_last_rb.setStyleSheet(radio_button)
        self.z_last_rb.setChecked(True)
        
        self.z_rb_group = QtWidgets.QButtonGroup()
        self.z_rb_group.addButton(self.z_first_rb)
        self.z_rb_group.addButton(self.z_last_rb)
        
        
        #pump tab
        self.pump_baudrate_label = QtWidgets.QLabel(pump_tab)
        self.pump_baudrate_label.setGeometry(QtCore.QRect(10, 10, 100, 30))
        self.pump_baudrate_label.setObjectName("pump_baudrate_label")
        self.pump_baudrate_label.setStyleSheet(text_style_semibold)
        self.pump_baudrate_label.setText("Baudrate:")
        
        self.pump_baud_sel = QtWidgets.QComboBox(pump_tab)
        self.pump_baud_sel.setGeometry(QtCore.QRect(130, 10, 100, 30))
        self.pump_baud_sel.setObjectName("pump_baud_sel")
        self.pump_baud_sel.setStyleSheet(clear_combobox)
        
        self.pump_port_label = QtWidgets.QLabel(pump_tab)
        self.pump_port_label.setGeometry(QtCore.QRect(10, 50, 100, 30))
        self.pump_port_label.setObjectName("pump_port_label")
        self.pump_port_label.setStyleSheet(text_style_semibold)
        self.pump_port_label.setText("Port:")
        
        self.pump_com_sel = QtWidgets.QComboBox(pump_tab)
        self.pump_com_sel.setGeometry(QtCore.QRect(130, 50, 100, 30))
        self.pump_com_sel.setObjectName("pump_com_sel")
        self.pump_com_sel.setStyleSheet(clear_combobox)
        
        self.pump_con_btn = QtWidgets.QPushButton(pump_tab)
        self.pump_con_btn.setGeometry(QtCore.QRect(260, 10, 120, 30))
        self.pump_con_btn.setObjectName("pump_con_btn")
        self.pump_con_btn.setStyleSheet(blue_button)
        self.pump_con_btn.setText("Connect")
        
        self.pump_discon_btn = QtWidgets.QPushButton(pump_tab)    
        self.pump_discon_btn.setGeometry(QtCore.QRect(260, 50, 120, 30))
        self.pump_discon_btn.setObjectName("pump_discon_btn") 
        self.pump_discon_btn.setStyleSheet(blue_button)
        self.pump_discon_btn.setText("Disconnect")
        
        self.flowrate_label = QtWidgets.QLabel(pump_tab)
        self.flowrate_label.setGeometry(QtCore.QRect(10, 90, 100, 30))
        self.flowrate_label.setObjectName("flowrate_label")
        self.flowrate_label.setStyleSheet(text_style_semibold)
        self.flowrate_label.setText("FlowRate:")
        
        self.pump_flowrate_sel = QtWidgets.QDoubleSpinBox(pump_tab)
        self.pump_flowrate_sel.setGeometry(QtCore.QRect(130, 90, 100, 30))
        self.pump_flowrate_sel.setObjectName("pump_flowrate_sel")
        self.pump_flowrate_sel.setStyleSheet(doubleSpinBox)
        
        self.pump_setq_btn = QtWidgets.QPushButton(pump_tab)
        self.pump_setq_btn.setGeometry(QtCore.QRect(260, 90, 150, 30))
        self.pump_setq_btn.setObjectName("pump_setq_btn")
        self.pump_setq_btn.setStyleSheet(clear_button)
        self.pump_setq_btn.setText("Set FlowRate")
        
        self.pump_setq_unit_label = QtWidgets.QLabel(pump_tab)
        self.pump_setq_unit_label.setGeometry(QtCore.QRect(415, 90, 70, 30))
        self.pump_setq_unit_label.setObjectName("pump_setq_unit_label")
        self.pump_setq_unit_label.setStyleSheet(text_style_regular)
        self.pump_setq_unit_label.setText("µL/min")
        
        self.syringe_size_label = QtWidgets.QLabel(pump_tab)
        self.syringe_size_label.setGeometry(QtCore.QRect(10, 130, 100, 30))
        self.syringe_size_label.setObjectName("syringe_size_label")
        self.syringe_size_label.setStyleSheet(text_style_semibold)
        self.syringe_size_label.setText("Syringe Size:")
        
        self.pump_syringed_sel = QtWidgets.QDoubleSpinBox(pump_tab)
        self.pump_syringed_sel.setGeometry(QtCore.QRect(130, 130, 100, 30))
        self.pump_syringed_sel.setObjectName("pump_syringed_sel")
        self.pump_syringed_sel.setStyleSheet(doubleSpinBox)
        
        self.con_connect_bt_4 = QtWidgets.QPushButton(pump_tab)
        self.con_connect_bt_4.setGeometry(QtCore.QRect(260, 130, 150, 30))
        self.con_connect_bt_4.setObjectName("con_connect_bt_4")
        self.con_connect_bt_4.setStyleSheet(clear_button)
        self.con_connect_bt_4.setText("Set Size")
        
        self.syringe_size_unit_label = QtWidgets.QLabel(pump_tab)
        self.syringe_size_unit_label.setGeometry(QtCore.QRect(415, 130, 50, 30))
        self.syringe_size_unit_label.setObjectName("syringe_size_unit_label")
        self.syringe_size_unit_label.setStyleSheet(text_style_regular)
        self.syringe_size_unit_label.setText("mm")
        
        self.pump_volume_label = QtWidgets.QLabel(pump_tab)
        self.pump_volume_label.setGeometry(QtCore.QRect(10, 170, 100, 30))
        self.pump_volume_label.setObjectName("pump_volume_label")
        self.pump_volume_label.setStyleSheet(text_style_semibold)
        self.pump_volume_label.setText("Volume:")
        
        self.volume_unit_label = QtWidgets.QLabel(pump_tab)
        self.volume_unit_label.setGeometry(QtCore.QRect(415, 170, 50, 30))
        self.volume_unit_label.setObjectName("volume_unit_label")
        self.volume_unit_label.setStyleSheet(text_style_regular)
        self.volume_unit_label.setText("µL")
        
        self.pump_v_sel = QtWidgets.QDoubleSpinBox(pump_tab)
        self.pump_v_sel.setGeometry(QtCore.QRect(130, 170, 100, 30))
        self.pump_v_sel.setObjectName("pump_v_sel")
        self.pump_v_sel.setStyleSheet(doubleSpinBox)
        
        self.con_connect_bt_5 = QtWidgets.QPushButton(pump_tab)
        self.con_connect_bt_5.setGeometry(QtCore.QRect(260, 170, 150, 30))
        self.con_connect_bt_5.setObjectName("con_connect_bt_5")
        self.con_connect_bt_5.setStyleSheet(clear_button)
        self.con_connect_bt_5.setText("Set Volume")
        
        self.constant_flowrate_rb = QtWidgets.QRadioButton(pump_tab)
        self.constant_flowrate_rb.setGeometry(QtCore.QRect(10, 210, 40, 30))
        self.constant_flowrate_rb.setObjectName("constant_flowrate_rb")
        self.constant_flowrate_rb.setStyleSheet(radio_button)
        self.constant_flowrate_rb.setChecked(True)
        
        self.constant_flowrate_label = QtWidgets.QLabel(pump_tab)
        self.constant_flowrate_label.setGeometry(QtCore.QRect(50, 210, 200, 30))
        self.constant_flowrate_label.setObjectName("constant_flowrate_label")
        self.constant_flowrate_label.setStyleSheet(text_style_semibold)
        self.constant_flowrate_label.setText("Constant FlowRate")
        
        self.flowrate_program_rb = QtWidgets.QRadioButton(pump_tab)
        self.flowrate_program_rb.setGeometry(QtCore.QRect(10, 250, 40, 30))
        self.flowrate_program_rb.setObjectName("flowrate_program_rb")
        self.flowrate_program_rb.setStyleSheet(radio_button)
        
        self.flowrate_program_label = QtWidgets.QLabel(pump_tab)
        self.flowrate_program_label.setGeometry(QtCore.QRect(50, 250, 200, 30))
        self.flowrate_program_label.setObjectName("flowrate_program_label")
        self.flowrate_program_label.setStyleSheet(text_style_semibold)
        self.flowrate_program_label.setText("FlowRate Program")
        
        self.sampling_flowrate_label = QtWidgets.QLabel(pump_tab)
        self.sampling_flowrate_label.setGeometry(QtCore.QRect(10, 290, 200, 30))
        self.sampling_flowrate_label.setObjectName("sampling_flowrate_label")
        self.sampling_flowrate_label.setStyleSheet(text_style_semibold)
        self.sampling_flowrate_label.setText("Sampling Rate:")
        
        self.pump_samplingq_sel = QtWidgets.QDoubleSpinBox(pump_tab)
        self.pump_samplingq_sel.setGeometry(QtCore.QRect(230, 290, 100, 30))
        self.pump_samplingq_sel.setObjectName("pump_samplingq_sel")
        self.pump_samplingq_sel.setStyleSheet(doubleSpinBox)
        
        self.pump_sampling_unit_label = QtWidgets.QLabel(pump_tab)
        self.pump_sampling_unit_label.setGeometry(QtCore.QRect(335, 290, 30, 30))
        self.pump_sampling_unit_label.setObjectName("pump_sampling_unit_label")
        self.pump_sampling_unit_label.setStyleSheet(text_style_regular)
        self.pump_sampling_unit_label.setText("µL")
        
        self.dwell_flowrate_label = QtWidgets.QLabel(pump_tab)
        self.dwell_flowrate_label.setGeometry(QtCore.QRect(10, 330, 100, 30))
        self.dwell_flowrate_label.setObjectName("dwell_flowrate_label")
        self.dwell_flowrate_label.setStyleSheet(text_style_semibold)
        self.dwell_flowrate_label.setText("Dwell Time:")
        
        self.pump_dwellq_sel = QtWidgets.QDoubleSpinBox(pump_tab)
        self.pump_dwellq_sel.setGeometry(QtCore.QRect(230, 330, 100, 30))
        self.pump_dwellq_sel.setObjectName("pump_dwellq_sel")
        self.pump_dwellq_sel.setStyleSheet(doubleSpinBox)
        
        self.pump_dwellq_unit_label = QtWidgets.QLabel(pump_tab)
        self.pump_dwellq_unit_label.setGeometry(QtCore.QRect(335, 330, 30, 30))
        self.pump_dwellq_unit_label.setObjectName("pump_dwellq_unit_label")
        self.pump_dwellq_unit_label.setStyleSheet(text_style_regular)
        self.pump_dwellq_unit_label.setText("µL")
        
        self.pump_start_btn = QtWidgets.QPushButton(pump_tab)
        self.pump_start_btn.setGeometry(QtCore.QRect(10, 370, 200, 30))
        self.pump_start_btn.setObjectName("pump_start_btn")
        self.pump_start_btn.setStyleSheet(blue_button)
        self.pump_start_btn.setText("Start")
        
        self.pump_stop_btn = QtWidgets.QPushButton(pump_tab)
        self.pump_stop_btn.setGeometry(QtCore.QRect(230, 370, 200, 30))
        self.pump_stop_btn.setObjectName("pump_stop_btn")
        self.pump_stop_btn.setStyleSheet(blue_button)
        self.pump_stop_btn.setText("Stop")
        
        self.prt_send_text_label = QtWidgets.QLabel(terminal_tab)
        self.prt_send_text_label.setGeometry(QtCore.QRect(10, 570, 400, 30))
        self.prt_send_text_label.setObjectName("prt_send_text_label")
        self.prt_send_text_label.setStyleSheet("font: 20pt ; font-weight: semi-bold; color: white;")
        self.prt_send_text_label.setText("Send Gcode:")
        self.prt_send_text_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.prt_send_btn = QtWidgets.QPushButton(terminal_tab)
        self.prt_send_btn.setGeometry(QtCore.QRect(420, 600, 100, 30))
        self.prt_send_btn.setObjectName("prt_send_btn")
        self.prt_send_btn.setStyleSheet(blue_button)
        self.prt_send_btn.setText("Send")

        self.prt_send_txt = QtWidgets.QLineEdit(terminal_tab)
        self.prt_send_txt.setGeometry(QtCore.QRect(10, 600, 400, 30))
        self.prt_send_txt.setObjectName("prt_send_txt")
        self.prt_send_txt.setStyleSheet("background-color: white; color: black; border: 1px solid black; border-radius: 5px;")
        
    
        self.terminal_output = QtWidgets.QTextEdit(terminal_tab)
        self.terminal_output.setGeometry(QtCore.QRect(10, 10, 510, 550))
        self.terminal_output.setObjectName("terminal_output")
        self.terminal_output.setStyleSheet("background-color: white; color: black; border: 1px solid black; border-radius: 5px;")
        self.terminal_output.setReadOnly(True)
        
        self.scroll_area = QtWidgets.QScrollArea(terminal_tab)
        self.scroll_area.setGeometry(QtCore.QRect(10, 10, 510, 550))
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_content = QtWidgets.QWidget()
        self.scroll_area_content.setGeometry(QtCore.QRect(0, 0, 510, 550))
        self.scroll_area_content.setObjectName("scroll_area_content")

        self.scroll_area_layout = QtWidgets.QVBoxLayout(self.scroll_area_content)
        self.scroll_area_layout.setObjectName("scroll_area_layout")

        self.terminal_output.setParent(None)
        self.scroll_area_layout.addWidget(self.terminal_output)
        self.scroll_area.setWidget(self.scroll_area_content)
    
    

        
        self.configure_buttons()

        
        
        
    
    def configure_buttons(self):
        if os.name == 'nt':
            # self.con_connect_bt.setText("Connect"))
            # self.con_com_sel.setCurrentText("COM1")) 
            # self.con_com_sel.setItemText(0, "COM1")) #sets item text to COM1
            # self.con_com_sel.setItemText(1, "COM2"))
            # self.con_com_sel.setItemText(2, "COM3"))
            # self.con_com_sel.setItemText(3, "COM4"))
            # self.con_com_sel.setItemText(4, "COM5"))
            # self.con_com_sel.setItemText(5, "COM6"))
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
        else:
            # Set options for macOS
            
            serial_ports = list(list_ports.comports())
            
            
            #take off the everything after " - " in the port name
            extracted_ports = [str(port).split(' - ')[0] for port in serial_ports]
            extracted_name = [str(port).split(' - ')[1] for port in serial_ports]
            
            
            
            con_com_size = 0
            pump_com_size = 0
            prt_com_size = 0
            
            self.con_com_sel.setCurrentText(str(extracted_ports[0]))
            #go through ports and add them to the dropdown
            for count, p in enumerate(extracted_ports):
                self.con_com_sel.addItem("")
                self.con_com_sel.setItemData(count, p)
                self.con_com_sel.setItemText(count, str(extracted_name[count]))
                
                
                self.pump_com_sel.addItem("")
                self.pump_com_sel.setItemData(count, p)
                self.pump_com_sel.setItemText(count, str(extracted_name[count]))
                
                self.prt_com_sel.addItem("")
                self.prt_com_sel.setItemData(count, p)
                self.prt_com_sel.setItemText(count, str(extracted_name[count]))
                
            self.setComboBoxSize(self.con_com_sel)
            self.setComboBoxSize(self.pump_com_sel) 
            self.setComboBoxSize(self.prt_com_sel)
            
                
                    


        
        #set camera
            
        #baud rate
        
        self.con_baud_sel.addItem("9600")
        self.con_baud_sel.addItem("19200")

        self.setComboBoxSize(self.con_baud_sel)
    

        self.pump_baud_sel.addItem("38400")
        self.pump_baud_sel.addItem("19200")
        self.pump_baud_sel.addItem("9600")

        self.setComboBoxSize(self.pump_baud_sel)
        
        self.prt_baud_sel.addItem("9600")
        self.prt_baud_sel.addItem("115200")
        self.prt_baud_sel.setCurrentText("115200")
        
        
        
        
        
        self.setComboBoxSize(self.prt_baud_sel)
        self.prt_baud_sel.setItemData(0, "9600")
        self.prt_baud_sel.setItemData(1, "115200")
        

        self.prt_baud_sel.setItemText(0, "9600 (mini)")
        self.prt_baud_sel.setItemText(1, "115200 (full)")

       
                
            
        #camera
        

        self.cam_no_sel.setCurrentText("1")
        self.cam_no_sel.setItemText(0, "1")
        self.cam_no_sel.setItemText(1, "2")
        self.cam_no_sel.setItemText(2, "3")
        
        #exposure
        # self.cam_exp_sel.setCurrentText("0 (auto)")
        # self.cam_exp_sel.setItemText(0,  "0 (auto)")
        # self.cam_exp_sel.setItemText(1,  "-1 (640ms)")
        # self.cam_exp_sel.setItemText(2,  "-2 (320ms)")
        # self.cam_exp_sel.setItemText(3,  "-3 (160ms)")
        # self.cam_exp_sel.setItemText(4,  "-4 (80ms)")
        # self.cam_exp_sel.setItemText(5,  "-5 (40ms)")
        # self.cam_exp_sel.setItemText(6,  "-6 (20ms)")
        # self.cam_exp_sel.setItemText(7,  "-7 (10ms)")
        # self.cam_exp_sel.setItemText(8,  "-8 (5ms)")
        # self.cam_exp_sel.setItemText(9,  "-9 (2.5ms)")
        
        

      
        
        
        
        
                   
        
        ##TODO: could be error here
        self.con_threshold_sp.setValue(100)
        
        self.con_threshold_sp.setMaximum(1023)
        self.con_threshold_sp.setMinimum(0)

        #set value of gc_lz_sel
        self.gc_lz_sel.setValue(50.0)
        
   
        
        
        self.gc_startz_sel.setMaximum(250.0)
        self.gc_startz_sel.setValue(150.0)
        
        self.gc_starty_sel.setMaximum(250.0)
        
        
        


        
        self.gc_startx_sel.setMaximum(250.0)
        

        self.gc_resx_sel.setValue(2)
        self.gc_resx_sel.setMaximum(250)

        self.gc_resy_sel.setValue(2)
        self.gc_resy_sel.setMaximum(250)
        
        self.gc_zspeedup_sel.setMaximum(10000)
        self.gc_zspeedup_sel.setValue(725)
        
        self.gc_speedxy_sel.setMinimum(1)
        self.gc_speedxy_sel.setMaximum(20800)
        self.gc_speedxy_sel.setValue(5000)
        
        self.gc_st_sel.setMaximum(250)
        self.gc_st_sel.setValue(2)
        
        self.gc_pause_sel.setMaximum(250)
        self.gc_pause_sel.setValue(2)
        
        self.gc_step_sel.setDecimals(3)
        self.gc_step_sel.setMaximum(5)
        self.gc_step_sel.setMinimum(0.001)
        self.gc_step_sel.setValue(0.05)
        self.gc_step_sel.setSingleStep(0.001)
        
        self.pump_samplingq_sel.setMaximum(1000)
        self.pump_samplingq_sel.setSingleStep(5)
        self.pump_samplingq_sel.setValue(150)
        
        self.pump_flowrate_sel.setMaximum(999)
        self.pump_flowrate_sel.setSingleStep(5)
        self.pump_flowrate_sel.setValue(80)
        
        self.pump_v_sel.setMaximum(999)
        self.pump_v_sel.setSingleStep(5)
        self.pump_v_sel.setValue(10)
        
        self.pump_syringed_sel.setValue(14.57)
        
        self.prt_stop_btn.setText("Stop")
        self.prt_pause_btn.setText("Pause")
        self.prt_update_btn.setText("Update")
        self.con_update_btn.setText("Update")
        self.con_zero_btn.setMaximum(1023)
        self.con_zero_btn.setMinimum(0)
        self.con_zero_btn.setValue(0)
        
       
        
        
        
        self.prt_nozzel_temp_sb.setMaximum(250)
        self.prt_nozzel_temp_sb.setMinimum(0)
        self.prt_nozzel_temp_sb.setValue(0)
        
        self.ref_x_pos.setMaximum(300)
        self.ref_y_pos.setMaximum(300)
    
        
        self.send_btn.setText("Send Absolute Coordinates")
        


        
    def setComboBoxSize(self, combobox):
        # Set the view and adjust dropdown width
        combobox.setView(QtWidgets.QListView(combobox))
        
        item_height = combobox.view().sizeHintForRow(0)
        num_items = combobox.count()
        
        font_metrics = QtGui.QFontMetrics(combobox.font())
        if combobox.count() >0:
            max_width = max(font_metrics.width(combobox.itemText(i)) for i in range(combobox.count()))
            max_width += 20
        
            combobox.view().setMinimumWidth(max_width)
            combobox.view().setMinimumHeight(num_items*item_height +15)
                        

    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
    
