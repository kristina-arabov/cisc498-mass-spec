from PyQt5.QtWidgets import QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PyQt5.QtCore import Qt

import itertools

import cv2
import numpy as np

import os
import re
import glob
import time

import json
import pprint

from datetime import datetime

from Unwarping_App.components.gcodeObject import gcodes


global temp_vars
temp_vars = {
    "checkerboard": {
        "mtx1": None,
        "dist1": None,

        "mtx2": None,
        "dist2": None,

        "size": None,
        "location": None,
        "image": None,
    },
    "tags": {
        "loc0": None,
        "loc1": None,
        "loc2": None,
        "loc3": None,

        "img0": None,
        "img1": None,
        "img2": None,
        "img3": None,

        "bottom_left": None,
        "top_right": None,

        "size": None
    },
    "probe_offset": None
}

R_cam2base_overlay = None
t_cam2base_overlay = None


# General function to add a bunch of widgets in an horizontal/vertical layout
def addAllWidgets(layout, widgets):
    for i in range(len(widgets)):
        if isinstance(widgets[i], QVBoxLayout):
            layout.addLayout(widgets[i], i)
        else:
            layout.addWidget(widgets[i], i, alignment=Qt.AlignCenter)
    
    return layout

# Toggle for dropdowns
def controlToggle(checked, toggle, inner, outer, height):
    if not checked:
        toggle.setArrowType(Qt.DownArrow)
        inner.hide()
        outer.setFixedHeight(40)
    else:
        toggle.setArrowType(Qt.UpArrow)
        inner.show()
        outer.setFixedHeight(height)


# Update the front-end view to show the live camera feed
def updateFrame(container, frame, crosshair=False):
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

    scaled = q_img.scaled(
        container.image_label.size(),
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )

    # Crosshair for probe detection page
    if crosshair:
        pixmap = QPixmap.fromImage(scaled)

        painter = QPainter(pixmap)
        pen = QPen(QColor(0, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        label_w = pixmap.width()
        label_h = pixmap.height()

        center_x = label_w // 2
        center_y = label_h // 2
        crosshair_length = 10

        # Horizontal
        painter.drawLine(
            center_x - crosshair_length, center_y,
            center_x + crosshair_length, center_y
        )

        # Vertical
        painter.drawLine(
            center_x, center_y - crosshair_length,
            center_x, center_y + crosshair_length
        )

        painter.end()

        container.image_label.setPixmap(pixmap)
    
    else:
        container.image_label.setPixmap(QPixmap.fromImage(scaled))

def processUpload(item, type):
    if type == 'folder':
        path = QFileDialog.getExistingDirectory(caption="Select Folder")
        
    if type == 'file':
        path, _ = QFileDialog.getOpenFileName(caption="Select File", filter="Image Files (*.jpg *.jpeg *.png)")

    item.path.setText(path if path else "")

def setBrightness(dropdown, connection):
    percent = dropdown.slider.value() / 100
    brightness = int(percent * 255)
    try:
        if 0 <= brightness <= 255:
            connection.serial_conn.write(str(brightness).encode())
            connection.serial_conn.write(b'\n')
    except:
        print("didnt work!")


'''
    Functions for unwarping
'''
# Check that the checkerboard is readable and can generate unwarping variables for fisheye
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
def getCheckerboardUnwarp(img, columns, rows, result, printer):
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

            # Save params and image of successful unwarping
            unwarping_vars = temp_vars["checkerboard"]
            unwarping_vars["mtx1"] = K
            unwarping_vars["dist1"] = D

            unwarping_vars["mtx2"] = mtx
            unwarping_vars["dist2"] = dist

            unwarping_vars["size"] = CHECKERBOARD
            unwarping_vars["location"] = getPrinterPosition(printer)
            unwarping_vars["image"] = img

            # Display unwarping results on result feed
            rgb_image = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled = q_img.scaled(result.feed_width, result.feed_height, Qt.KeepAspectRatio)
            result.image_label.setPixmap(QPixmap.fromImage(scaled))
    else:
        result.image_label.clear()
        result.image_label.setText("Unwarping failed since checkerboard could not be read. Please retake the image or edit the board dimensions.")


def saveUnwarping(vars):
    checkerboard = temp_vars["checkerboard"]
    vars["mtx1"] = checkerboard["mtx1"]
    vars["dist1"] = checkerboard["dist1"]

    vars["mtx2"] = checkerboard["mtx2"]
    vars["dist2"] = checkerboard["dist2"]

    vars["size"] = checkerboard["size"]
    vars["location"] = checkerboard["location"]
    vars["image"] = checkerboard["image"]

def getPrinterPosition(printer):
    while True:
        if printer.line.find('Count') != -1:
            line = printer.line.split()
            pos = [float(line[0][2:]), float(line[1][2:]), float(line[2][2:])]
            break
    
    return pos

def unwarpPhoto(img, vars):
    # Can't save numpy arrays in json, so convert lists to numpy arrays
    mtx1 = np.asarray(vars["mtx1"], dtype=np.float32)
    dist1 = np.asarray(vars["dist1"], dtype=np.float32)
    mtx2 = np.asarray(vars["mtx2"], dtype=np.float32)
    dist2 = np.asarray(vars["dist2"], dtype=np.float32)

    # Unwarp image (first step)
    img = fisheyeUnwarp(img, mtx1, dist1)
    img = secondUnwarp(img, mtx2, dist2)

    return img


# TODO implement permutations
def calculateOffset(vars, result_label):
    ''' #uncomment to test :) 
    image_folder = "UNWARPED_all"
    image_files = glob.glob(os.path.join(image_folder, r"*.*g"))

    mtx = np.array([[196.967008, 0, 645.54331595],[0, 197.70493259, 478.54245571],[0,0,1]], dtype=np.float32)
    dist = np.array([[0, 0, 0, 0, 0]], dtype=np.float32)

    tag_size = 10
    known_tag_corner = np.array([221.9, 9, 0], dtype=np.float32)
    
    # loop for file in image_files, stuff for loop below
        base_name = os.path.basename(file)
        match = re.search(r'(-?\d+\.?\d*)_(-?\d+\.?\d*)_(-?\d+\.?\d*)\.png$', base_name)
        current_point = np.array([[match.group(1)], [match.group(2)], [match.group(3)]], dtype=np.float32)

        image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    '''
    # mtx = np.array([[-17128.18759580409, 0.0, 631.7240564389283],[0.0, -13623.470268100988, 408.4061865406018],[0,0,1]], dtype=np.float32)
    # dist = np.array([[0,0,0,0,0]], dtype=np.float32)

    # mtx2 = np.array([[1147.0279321355567, 0.0, 652.5268735204457],[0.0, 1149.366948138077, 412.2098448497876], [0.0, 0.0,1.0]], dtype=np.float32)
    # dist2 = np.array([[-0.47232781654533984, -0.168810714709961, 0.02606485303867365, -0.012464771958492637, 1.7877475420492845]], dtype=np.float32)

    mtx1 = vars["checkerboard"]["mtx1"]
    dist1 = np.array([[0, 0, 0, 0, 0]], dtype=np.float32)

    mtx2 = vars["checkerboard"]["mtx2"]
    dist2 = vars["checkerboard"]["dist2"]

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    tag_size = vars["tags"]["size"]
    
    if not tag_size or tag_size <= 0:
        print("invalid tag size")
        return
   
    object_points = np.array([
        [tag_size, 0, 0], 
        [0, 0, 0],
        [0, tag_size, 0],
        [tag_size, tag_size, 0],
        [tag_size/2, tag_size/2, 0]], dtype=np.float32)

    corner_x = vars["tags"]["bottom_left"][0]
    corner_y = vars["tags"]["bottom_left"][1]
    known_tag_corner = np.array([corner_x, corner_y, 0], dtype=np.float32)
    print(known_tag_corner)

    # tag to camera
    R_tag2cam_all = []
    t_tag2cam_all = []

    # camera to tag
    # R_cam2tag_all = []
    # t_cam2tag_all = []

    # store all calculations for average
    probe_offset = []

    # process images with known coordinates
    for i in range(4):
        img = vars["tags"]["img" + str(i)]
        current_point = vars["tags"]["loc" + str(i)]
        current_point = np.array([current_point[0], current_point[1], current_point[2]], dtype=np.float32)

        # convert image to greyscale
        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # for file in image_files:
    #     base_name = os.path.basename(file)
    #     match = re.search(r'(-?\d+\.?\d*)_(-?\d+\.?\d*)_(-?\d+\.?\d*)\.png$', base_name)
    #     current_point = np.array([[match.group(1)], [match.group(2)], [match.group(3)]], dtype=np.float32)

    #     img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

        # find tag in image
        corners, ids, _ = detector.detectMarkers(image)
        if corners:
            corner_set = corners[0][0]
            centre = np.array([(corner_set[0][0]+corner_set[1][0])/2, (corner_set[0][1]+corner_set[3][1])/2], dtype=np.float32)
            corners = np.vstack([corners[0][0], centre])

            for j in range(len(corners)):
                corners[j] = undoSecondUnwarp(corners[j], mtx2, dist2)

            image_points = corners
            print(corners)
            print(image_points)
            # print(corners, image_points)

            # cv2.circle(img, (int(image_points[0][0]), int(image_points[0][1])), 3, (255, 0, 0), -1) # blue
            # cv2.circle(img, (int(image_points[1][0]), int(image_points[1][1])), 3, (255, 255, 0), -1) # cyan
            # cv2.circle(img, (int(image_points[2][0]), int(image_points[2][1])), 3, (255, 0, 255), -1) # pink
            # cv2.circle(img, (int(image_points[3][0]), int(image_points[3][1])), 3, (0, 0, 255), -1) # red

            # get extrinsic parameters for target to camera
            retval, rvec, tvec = cv2.solvePnP(object_points, image_points, mtx1, dist1, flags=cv2.SOLVEPNP_ITERATIVE)
            rvec, tvec = cv2.solvePnPRefineLM(object_points, image_points, mtx1, dist1, rvec, tvec)
            rvec, tvec = cv2.solvePnPRefineVVS(object_points, image_points, mtx1, dist1, rvec, tvec)

            R_tag2cam, _ = cv2.Rodrigues(rvec) # convert to matrix

            # R_tag2cam = R, tvec = t for tag to camera
            R_tag2cam_all.append(R_tag2cam)
            t_tag2cam_all.append(tvec)

            # get camera to tag (invert transformation)
            R_cam2tag = R_tag2cam.T
            t_cam2tag = -R_tag2cam.T @ tvec
            print("cam2tag: ", t_cam2tag)

            R_tag2base = np.eye(3) # no roation (move the same)
            t_tag2base = known_tag_corner.reshape(-1, 1)
            print("tag2base", t_tag2base)

            # get camera to tag, tag to base = camera to base
            R_cam2base = R_tag2base @ R_cam2tag
            t_cam2base = R_tag2base @ t_cam2tag + t_tag2base

            print("cam2base", t_cam2base)

            # get base to camera
            R_base2cam = R_cam2base.T
            t_base2cam = -R_cam2base.T @ t_cam2base

            print("base2cam", t_base2cam)

            # get probe to base
            R_probe2base = np.eye(3)
            t_probe2base = current_point.reshape(-1, 1)

            print("probe2base:", t_probe2base)

            # get probe to base, base to camera = probe to camera
            R_probe2cam = R_base2cam @ R_probe2base
            t_probe2cam = R_base2cam @ t_probe2base + t_base2cam

            print("probe2cam", t_probe2cam)

            probe_offset.append(t_probe2cam)

            # cv2.drawFrameAxes(img, mtx, dist, rvec, tvec, 5)
            # cv2.imshow("IDK", img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

    probe_locations_to_cam = np.array(probe_offset)
    probe_locations_to_cam_mean = np.mean(probe_locations_to_cam, axis=0)

    vars["probe_offset"] = probe_locations_to_cam_mean
    output = probe_locations_to_cam_mean.reshape(1, -1)[0]
    print(output)

    # update offset result in label
    result_label.setText(f"X: {round(output[0], 3)} mm, Y: {round(output[1], 3)} mm")


def generateTransformationFolder(vars):
    checkerboard_data = vars["checkerboard"]
    probe_detection_data = vars["tags"]

    checkerboard_img = checkerboard_data["image"]
    checkerboard_location = checkerboard_data["location"]

    json_data = {
        "checkerboard": [{
            "mtx1": checkerboard_data["mtx1"].tolist(),
            "dist1": checkerboard_data["dist1"].tolist(),

            "mtx2": checkerboard_data["mtx2"].tolist(),
            "dist2": checkerboard_data["dist2"].tolist(),

            "size": checkerboard_data["size"],
            "location": checkerboard_location
        }],
        "tags": [{
            "loc0": probe_detection_data["loc0"],
            "loc1": probe_detection_data["loc1"],
            "loc2": probe_detection_data["loc2"],
            "loc3": probe_detection_data["loc3"],

            "bottom_left": probe_detection_data["bottom_left"],
            "top_right": probe_detection_data["top_right"],

            "size": probe_detection_data["size"]
        }],
        "probe_offset": vars["probe_offset"].tolist()
    }

    checkerboard_file = "checkerboard_{0}_{1}_{2}.jpg".format(str(checkerboard_location[0]), str(checkerboard_location[1]), str(checkerboard_location[2]))

    # Timestamp for transformation folder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(f"transformations/{timestamp}", exist_ok=True)

    # Add images and json to folder
    cv2.imwrite(os.path.join(f"transformations/{timestamp}/") + checkerboard_file, checkerboard_img)

    for i in range(4):
        location = probe_detection_data["loc" + str(i)]
        tag_file = "tag_{0}_{1}_{2}.jpg".format(str(location[0]), str(location[1]), str(location[2]))

        cv2.imwrite(os.path.join(f"transformations/{timestamp}/") + tag_file, vars["tags"]["img" + str(i)])

    with open(os.path.join(f"transformations/{timestamp}/") + "data.json", "w") as json_file:
        json.dump(json_data, json_file, indent=3)

def verifyTransformation(path, json_path):
    json_file = glob.glob(os.path.join(path, r"*.json"))
    json_path["json"] = json_file[0]

    print(json_path)

    # checkerboard_passed = False
    # tag_passed = False
    # json_passed = False

    # contents = os.listdir(path)

    # # verify checkerboard exists
    # verify_checkerboard = any(re.match(r"^checkerboard_\d+_\d+_\d+\.jp*$", fname) for fname in contents)
    # if verify_checkerboard:
    #     checkerboard_passed = True
    #     print("Not in thing") # 

    # # verify tags exist
    # verify_tags = any(re.match(r"^tag_\d+_\d+_\d+\.jp*$", fname) for fname in contents)
    # if verify_tags:
    #     tag_passed = True
    #     print("Not in thing")

    # # verify json exists and has all info

    # # if everything passes, overwrite vars to use this? or just read params in the json file?
    # json_file = glob.glob(os.path.join(path, r"*.json"))
    # json_passed = True

    # if checkerboard_passed and tag_passed and json_passed:
    #     json = json_file[0]

    # print(json)

def updateDropdownIndex(connection, index):
    connection.idx = index

def generateProbeAcquisition(dot, rectangle, json_file, printer, result, corner):
    start_point = rectangle.topLeft()
    end_point = rectangle.bottomRight()

    if not dot or not rectangle:
        print("Nothing to sample or missing location for dot/rectangle.")
        return

    # Process original image (not scaled!)
    image = cv2.cvtColor(result.original_pixmap, cv2.COLOR_RGBA2GRAY)

    if printer is None:
        print("Printer not connected, cannot generate probe locations without knowing the current position.")
        return
    
    current_position = getPrinterPosition(printer)
    current_position = np.array([current_position[0], current_position[1], current_position[2]], dtype=np.float32) # current position

    # Open and read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    unwarping = data["checkerboard"][0]
    mtx1 = np.asarray(unwarping["mtx1"], dtype=np.float32)
    mtx1[0][0] = mtx1[0][0] * 0.01
    mtx1[1][1] = mtx1[1][1] * 0.01
    dist1 = np.array([[0,0,0,0,0]], dtype=np.float32) # Set to no distortion

    mtx2 = np.asarray(unwarping["mtx2"], dtype=np.float32)
    dist2 = np.asarray(unwarping["dist2"], dtype=np.float32)

    # Need tag in the image
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    corners, ids, _ = detector.detectMarkers(image)
    if not corners or len(corners) == 0:
        print("Cannot generate probe locations without tag")
        return

    tag_size = data["tags"][0]["size"]
    object_points = np.array([
        [tag_size, 0, 0], 
        [0, 0, 0],
        [0, tag_size, 0],
        [tag_size, tag_size, 0]], dtype=np.float32)
    
    # json_corner = data["tags"][0]["corner1"]
    # known_tag_corner = np.array([json_corner[0], json_corner[1], 0], dtype=np.float32)

    known_tag_corner = np.array([float(corner.input.text()), float(corner.input2.text()), 0], dtype=np.float32)

    image_points = corners[0].reshape(-1, 2).astype(np.float32)

    for i in image_points:
        cv2.circle(image, (int(i[0]), int(i[1])), 5, (255, 255, 255), -1)

    retval, rvec, tvec = cv2.solvePnP(object_points, image_points, mtx1, dist1, flags=cv2.SOLVEPNP_ITERATIVE)
    rvec, tvec = cv2.solvePnPRefineLM(object_points, image_points, mtx1, dist1, rvec, tvec)
    rvec, tvec = cv2.solvePnPRefineVVS(object_points, image_points, mtx1, dist1, rvec, tvec)
    R_tag2cam, _ = cv2.Rodrigues(rvec) # convert to matrix

    # get camera to tag (invert transformation)
    R_cam2tag = R_tag2cam.T
    t_cam2tag = -R_tag2cam.T @ tvec

    # get tag to base
    R_base2tag = np.eye(3)
    t_base2tag = known_tag_corner.reshape(-1, 1)

    # get camera to tag, tag to base = camera to base
    global R_cam2base_overlay, t_cam2base_overlay
    R_cam2base_overlay = R_base2tag @ R_cam2tag
    t_cam2base_overlay = R_base2tag @ t_cam2tag + t_base2tag


    R_base2cam = R_cam2base_overlay.T
    t_base2cam = -R_cam2base_overlay.T @ t_cam2base_overlay

    print(R_base2cam, t_base2cam)

    '''
        Process dot
    '''
    dot_unscaled = (int(dot.x() / 0.7), int(dot.y() / 0.7))
    new_dot = undoSecondUnwarp(dot_unscaled, mtx2, dist2)

    dot_from_cam_principal = getDirectionFromPixel(new_dot[0], new_dot[1], mtx1)
    dot_in_base = R_cam2base_overlay @ dot_from_cam_principal

    dot_x = current_position[0] + (dot_in_base[0] * 10)
    dot_y = current_position[1] + (dot_in_base[1] * 10)
    
    # Add probe offset to dot position
    dot_x += data["probe_offset"][0]
    dot_y += data["probe_offset"][1]

    probe_dot = (float(dot_x.item()), float(dot_y.item()))

    '''
        Process rectangle 
    '''
    # Start and end points will be diagonal to each other?
    start_point = rectangle.topRight()
    end_point = rectangle.bottomLeft()
    start_unscaled = (int(start_point.x() / 0.7), int(start_point.y() / 0.7))
    end_unscaled = (int(end_point.x() / 0.7), int(end_point.y() / 0.7))

    start_point = undoSecondUnwarp(start_unscaled, mtx2, dist2)
    end_point = undoSecondUnwarp(end_unscaled, mtx2, dist2)

    start_point_from_cam_principal = getDirectionFromPixel(start_point[0], start_point[1], mtx1)
    end_point_from_cam_principal = getDirectionFromPixel(end_point[0], end_point[1], mtx1)

    start_point_in_base = R_cam2base_overlay @ start_point_from_cam_principal
    end_point_in_base = R_cam2base_overlay @ end_point_from_cam_principal


    start_x = current_position[0] + (start_point_in_base[0] * 10)
    start_y = current_position[1] + (start_point_in_base[1] * 10)

    start_x += data["probe_offset"][0]
    start_y += data["probe_offset"][1]


    end_x = current_position[0] + (end_point_in_base[0] * 10)
    end_y = current_position[1] + (end_point_in_base[1] * 10)

    end_x += data["probe_offset"][0]
    end_y += data["probe_offset"][1]


    probe_rectangle = [float(end_x.item()), float(end_y.item()), float(start_x.item()), float(start_y.item())]

    print("DOT --> ", probe_dot)
    print("RECTANGLE --> ", probe_rectangle)
    result.probe_dot = probe_dot
    result.probe_rectangle = probe_rectangle

# Returns direction for a location from the camera principal point
def getDirectionFromPixel(u, v, mtx):
    # (u, v) are pixel coordinates in the image
    fx = mtx[0, 0]
    fy = mtx[1, 1]
    cx = mtx[0, 2]
    cy = mtx[1, 2]

    x = (u - cx) / fx
    y = (v - cy) / fy
    z = 1.0

    direction = np.array([x, y, z])
    return direction

def getPixelFromDirection(x, y, mtx):
    # Extract camera intrinsic parameters
    fx = mtx[0, 0]
    fy = mtx[1, 1]
    cx = mtx[0, 2]
    cy = mtx[1, 2]

    # Reverse the normalization to get pixel coordinates
    u = (x * fx) + cx
    v = (y * fy) + cy

    return (u, v)


def undoSecondUnwarp(point, mtx, dist):
    current = np.array(point, dtype=np.float32).reshape(1, 1, 2)

    # Convert rectified pixel to normalized image coordinates
    x = (current[0,0,0] - mtx[0,2]) / mtx[0,0]
    y = (current[0,0,1] - mtx[1,2]) / mtx[1,1]
    normalized = np.array([[[x, y, 1.0]]], dtype=np.float32)

    # Apply distortion model to normalized point
    previous = cv2.projectPoints(
        normalized,
        rvec=np.zeros(3),
        tvec=np.zeros(3),
        cameraMatrix=mtx,
        distCoeffs=dist
    )[0]

    return tuple(previous[0, 0])

def redoSecondUnwarp(point, mtx, dist):
    # Convert the input point to the required format for undistortion
    distorted = np.array([[[point[0], point[1]]]], dtype=np.float32)

    # Reverse the distortion model using cv2.undistortPoints
    normalized = cv2.undistortPoints(distorted, cameraMatrix=mtx, distCoeffs=dist)

    # Reverse normalization to get rectified pixel coordinates
    x = normalized[0, 0, 0] * mtx[0, 0] + mtx[0, 2]
    y = normalized[0, 0, 1] * mtx[1, 1] + mtx[1, 2]

    return (x, y)

def updatePixelOverlay(result, resolution, json_file):
    x0, y0, x1, y1 = result.probe_rectangle

    x_range = np.arange(x0, x1, float(resolution))
    y_range = np.arange(y0, y1, float(resolution))

    result.sample_overlay_x = len(x_range)
    result.sample_overlay_y = len(y_range)

    combinations = [(x, y) for x in x_range for y in y_range]
    print(combinations)

    result.real_points = combinations
    result.real_points.append(result.probe_dot)
    print(result.real_points)

    # generatePixelOverlay(result, combinations, json_file)

# Don't actually need this right now...
def generatePixelOverlay(result, locations, json_file):
    pixels = []
    # Open and read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    unwarping = data["checkerboard"][0]
    mtx1 = np.asarray(unwarping["mtx1"], dtype=np.float32)
    dist1 = np.array(unwarping["dist1"], dtype=np.float32) # Set to no distortion

    mtx2 = np.asarray(unwarping["mtx2"], dtype=np.float32)
    dist2 = np.asarray(unwarping["dist2"], dtype=np.float32)

    print("HERE --->", R_cam2base_overlay)
    current_position = np.array([176.95, -5.5, 0], dtype=np.float32) # current position

    # TODO Not working properly, fix
    for i in locations:
        # Remove offset to get camera location
        dot_x_no_offset = i[0] - data["probe_offset"][0]
        dot_y_no_offset = i[1] - data["probe_offset"][1]

        # Reverse cam2base
        dot_in_base = np.array([(dot_x_no_offset - current_position[0]).item(),
                                (dot_y_no_offset - current_position[1]).item(), 1.0]) / 10
        dot_from_cam_principal = np.linalg.inv(R_cam2base_overlay) @ dot_in_base

        # Get pixel from direction to point
        new_dot = (dot_from_cam_principal[0], dot_from_cam_principal[1])
        original_pixel = getPixelFromDirection(new_dot[0], new_dot[1], mtx1)

        # Apply second unwarp
        original_pixel = redoSecondUnwarp(original_pixel, mtx2, dist2)

        # Scale
        original_x = original_pixel[0] * 0.7
        original_y = original_pixel[1] * 0.7

        print((int(original_x), int(original_y)))
        pixels.append((int(original_x), int(original_y)))

    # result.sample_overlay = pixels

def sendLocations(locations, dwell, transit):
    # Create GCodes then send to main
    # TODO temp values for now
    locations = [(181.4, -2),
                (182.4, -2),
                (181.4, -1),
                (182.4, -1)]

    gcodes.gcode_list.append("G90")

    for i in locations:
        # Command to go to location
        gcodes.gcode_list.append("G0 X"+str(round(i[0], 2))+" Y"+str(round(i[1], 2)))
        gcodes.gcode_list.append("G0 Z"+ str(-5)) # TODO temp height

        # Command to dwell there (in milliseconds)
        dwell_time = int(dwell) * 1000
        gcodes.gcode_list.append(f"G4 P{str(dwell_time)}")

        # Command to return to transit height
        gcodes.gcode_list.append("G0 Z"+ str(transit))

    # Reset any pre-exisitng data
    gcodes.completed_gcodes = []
    gcodes.time_stamps = []
    gcodes.readable_time_stamps = []

    # Start the time stamp collection immediately once gcodes are ready
    gcodes.time_stamps.append(time.time())
    gcodes.readable_time_stamps.append(0)
    print(gcodes.gcode_list)
