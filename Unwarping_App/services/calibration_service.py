import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PyQt5.QtCore import Qt


# Function to check chessboard readability for initial unwarp
def checkFishReadability(img, checkerboard, objp, flags):
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, checkerboard, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

    K = np.zeros((3, 3)) # intrinsic matrix
    D = np.zeros((4, 1)) # distortion coefficients
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64)] # rotation vectors
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64)] # translation vectors

    # usually where the issue of folder readability happens, will not run if it can't get one of these parameters
    try:
        retval, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
            objpoints,
            imgpoints,
            gray.shape[::-1],
            K,
            D,
            rvecs,
            tvecs,
            flags,
            (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 300, 1e-6)
        )
    except:
        retval = False
    
    print(K, D)
    return retval, K, D


# Check that the checkerboard is readable and can generate unwarping variables for the second unwarping
def checkSecondReadability(image, checkerboard, objp, subpix):
    objpoints = []
    imgpoints = []

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, checkerboard, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE)

    if ret:
        objpoints.append(objp)
        cv2.cornerSubPix(gray,corners,(3,3),(-1,-1), subpix)
        imgpoints.append(corners)
    
    try:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        return ret, mtx, dist
    except:
        return False, None, None
    

# Perform fisheye unwarping
def fisheyeUnwarp(image, mtx, dist):
    img_shape = image.shape[:2][::-1]

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(mtx, dist, np.eye(3), mtx, img_shape, cv2.CV_16SC2)
    undist_image = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    return undist_image


# Perform second unwarping
def secondUnwarp(image, mtx, dist):
    h, w = image.shape[:2]
    newmatx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    undist_image = cv2.undistort(image, mtx, dist, None, newmatx)
    return undist_image


# Unwarp current view
def getCheckerboardUnwarp(img, columns, rows, result, printer=None):
    # First check that dimensions are provided
    if not columns or not rows or int(columns) <= 1 or int(rows) <= 1:
        result.image_label.clear()
        result.image_label.setText("Cannot unwarp with missing or negative board dimensions.")
        return

    # Initialize constant stuff
    CHECKERBOARD = (int(columns) - 1, int(rows) - 1) # index to 0
    
    objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

    subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 300, 0.1)
    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_FIX_SKEW

    # Actual checking and unwarping
    retval, K, D = checkFishReadability(img, CHECKERBOARD, objp, calibration_flags)
    if retval:
        image = fisheyeUnwarp(img, K, D)
        retval, mtx, dist = checkSecondReadability(image, CHECKERBOARD, objp, subpix_criteria)
        
        if retval:
            final = secondUnwarp(image, mtx, dist)

            # # Save params and image of successful unwarping
            # unwarping_vars = temp_vars["checkerboard"]
            # unwarping_vars["mtx1"] = K
            # unwarping_vars["dist1"] = D

            # unwarping_vars["mtx2"] = mtx
            # unwarping_vars["dist2"] = dist

            # unwarping_vars["size"] = CHECKERBOARD
            # unwarping_vars["location"] = getPrinterPosition(printer)
            # unwarping_vars["image"] = img

            # Display unwarping results on result feed
            rgb_image = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled = q_img.scaled(result.feed_width, result.feed_height, Qt.KeepAspectRatio)
            result.image_label.setPixmap(QPixmap.fromImage(scaled))