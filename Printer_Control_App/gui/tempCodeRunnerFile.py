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
        self.z_last_label.setGeometry(QtCore.QRect(10, 470, 150, 30))
        self.z_last_label.setObjectName("z_last_label")
        self.z_last_label.setStyleSheet(text_style_semibold)
        self.z_last_label.setText("Z Last:")
        
        self.z_last_rb = QtWidgets.QRadioButton(refrence_tab)
        self.z_last_rb.setGeometry(QtCore.QRect(150, 470, 40, 50))
        self.z_last_rb.setObjectName("z_last_rb")
        self.z_last_rb.setStyleSheet(radio_button)
        self.z_last_rb.setChecked(True)
        
        self.z_rb_group = QtWidgets.QButtonGroup()
        self.z_rb_group.addButton(self.z_first_rb)
        self.z_rb_group.addButton(self.z_last_rb)
