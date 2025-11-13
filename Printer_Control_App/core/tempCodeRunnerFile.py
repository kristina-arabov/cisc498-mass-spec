     # Resize the frame to fit the QLabel size
        label_width = self.video_label.width()
        label_height = self.video_label.height()
        
        # Resize the frame to match the QLabel dimensions while keeping the aspect ratio
        resized_frame = cv2.resize(frame, (label_width, label_height), interpolation=cv2.INTER_AREA)
        
        # Convert the frame to QImage and display it
        height, width, channel = resized_frame.shape
        bytes_per_line = 3 * width
        q_img = QtGui.QImage(resized_frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(q_img)
        self.video_label.setPixmap(pixmap)