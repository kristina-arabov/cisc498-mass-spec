import cv2
import os
import json
from datetime import datetime
import numpy as np
import time
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PyQt5.QtCore import Qt

from Unwarping_App.services import device_service


class Transformation():
    def __init__(self):
        super().__init__()

        # Chessboard
        self.mtx1 = None
        self.dist1 = None

        self.mtx2 = None
        self.dist2 = None

        self.chessboard_img = None
        self.chessboard_loc = None
        self.chessboard_size = None
        self.height = None

        # AprilTags
        self.loc1 = None
        self.loc2 = None
        self.loc3 = None
        self.loc4 = None

        self.img1 = None
        self.img2 = None
        self.img3 = None
        self.img4 = None

        self.tag_bottom_left = [None, None]
        self.tag_size = None


        # Probe-to-camera offset
        self.offset_x = None
        self.offset_y = None

        # Sampling loc
        self.photo_loc = [0, 0, 0]


    # Function to reset all properties if cleared
    def resetVals(self):
        for attr in self.__dict__:
            if attr == "tag_bottom_left":
                setattr(self, attr, [None, None])
            else:
                setattr(self, attr, None)


# Function to check chessboard readability for initial unwarp
def checkFishReadability(img, checkerboard, objp, flags):
    msg = None
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, checkerboard, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)
    else:
        msg = "Chessboard is unreadable. Issue may be caused by:\n- Incorrect board dimensions\n- Obscured board"

    K = np.zeros((3, 3)) # intrinsic matrix
    D = np.zeros((4, 1)) # distortion coefficients
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64)] # rotation vectors
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64)] # translation vectors

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
        # TODO correct message?
        msg = "Chessboard is unreadable. Issue may be caused by:\n- Lighting\n- Camera focus\n- Board position\n- Incorrect board dimensions"
        retval = False
        return retval, K, D, msg
    
    print(K, D)


    error = fisheyeRMS(objpoints, imgpoints, rvecs, tvecs, K, D) * 0.1
    print(error)
    
    # Error should not be greater than 0.6 (safest bet since we're only using one image)
    if error <= 0.6:
        objpoints = np.asarray(objpoints, dtype=np.float32).reshape(-1, 3)
        imgpoints = np.asarray(imgpoints, dtype=np.float32).reshape(-1, 2)

        stability_vals = poseStability(objpoints, imgpoints, K, D)   

        # # TODO is this super necessary?
        # if (stability_vals["translation_std"] > 0.0015 and 
        #     stability_vals["translation_max"] > 0.005 and 
        #     stability_vals["rotation_max_deg"] > 0.05):
        #     msg = "?"
        #     retval = False

    else:
        msg = "RMS error is too high to accurately calculate the probe-to-camera offset."
        retval = False

    return retval, K, D, msg


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
def getCheckerboardUnwarp(camera, columns, rows, result, transformation, printer=None):
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

    # Set values
    start = time.time()
    end = start + 3 # Run for 3 seconds max
    
    retval = False
    msg = "Board was unreadable. Ensure the correct dimensions are used and the entire board is visible."

    # Actual checking and unwarping
    # Loop here, run until end condition or until retval is true.
    while time.time() < end and not retval:
        img = camera.frame.copy()
        retval, K, D, msg = checkFishReadability(img, CHECKERBOARD, objp, calibration_flags)
        if retval:
            image = fisheyeUnwarp(img, K, D)
            retval, mtx, dist = checkSecondReadability(image, CHECKERBOARD, objp, subpix_criteria)
            
            if retval:
                final = secondUnwarp(image, mtx, dist)

                # Update transformation vars for chessboard
                transformation.mtx1 = K
                transformation.dist1 = D

                transformation.mtx2 = mtx
                transformation.dist2 = dist

                transformation.chessboard_loc = device_service.getPrinterPosition(printer)
                transformation.height = transformation.chessboard_loc[2]
                transformation.chessboard_size = CHECKERBOARD
                transformation.chessboard_img = img

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
                updateResult(final, result)

    result.image_label.setText(msg)

def rvec_tvec_to_transform(rvec, tvec):
    R, _ = cv2.Rodrigues(rvec)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = tvec.reshape(3)
    return T


def rotation_angle_deg(R):
    angle = np.arccos(
        np.clip((np.trace(R) - 1) / 2.0, -1.0, 1.0)
    )
    return np.degrees(angle)


def poseStability(objpoints, imgpoints, K, D, noise_std=0.2, trials=50):

    objpoints = objpoints.astype(np.float32)
    imgpoints = imgpoints.astype(np.float32)

    # Undistort once (fisheye-safe)
    undistorted = cv2.fisheye.undistortPoints(
        imgpoints.reshape(-1, 1, 2),
        K, D, P=K
    ).reshape(-1, 2)

    Ts = []

    for _ in range(trials):
        noise = np.random.normal(0, noise_std, undistorted.shape)
        noisy_pts = undistorted + noise

        _, rvec, tvec = cv2.solvePnP(
            objpoints,
            noisy_pts,
            K,
            None,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        Ts.append(rvec_tvec_to_transform(rvec, tvec))

    T_ref = Ts[0]

    t_errors = []
    r_errors = []

    for T in Ts[1:]:
        dt = np.linalg.norm(T[:3, 3] - T_ref[:3, 3])
        dR = T[:3, :3] @ T_ref[:3, :3].T
        da = rotation_angle_deg(dR)

        t_errors.append(dt)
        r_errors.append(da)

    return {
        "translation_std": np.std(t_errors),
        "rotation_std_deg": np.std(r_errors),
        "translation_max": np.max(t_errors),
        "rotation_max_deg": np.max(r_errors)
    }


def fisheyeRMS(objpoints, imgpoints, rvecs, tvecs, K, D):
    total_error_sq = 0.0
    total_points = 0

    for i in range(len(objpoints)):
        # Project 3D object points to image points
        projected_points, _ = cv2.fisheye.projectPoints(
            objpoints[i],
            rvecs[i],
            tvecs[i],
            K,
            D
        )

        projected_points = projected_points.reshape(-1, 2)
        observed_points = imgpoints[i].reshape(-1, 2)

        # Per-point squared error
        error = observed_points - projected_points
        error_sq = np.sum(error ** 2, axis=1)

        total_error_sq += np.sum(error_sq)
        total_points += len(objpoints[i])

    rms_error = np.sqrt(total_error_sq / total_points)
    return rms_error

def updateResult(img, result):
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    scaled = q_img.scaled(result.feed_width, result.feed_height, Qt.KeepAspectRatio)
    result.image_label.setPixmap(QPixmap.fromImage(scaled))


def updateTag(transformation, val, type):
    print(val)
    # Update X coordinate
    if type == "X":
        transformation.tag_bottom_left[0] = float(val)
    
    # Update Y coordinate
    elif type == "Y":
        transformation.tag_bottom_left[1] = float(val)

    # Update tag size (mm)
    elif type == "size":
        transformation.tag_size = float(val)



def createTransformationFile(transformation):
    # Create a JSON file containing relevant transformation data
    json_data = {
        "unwarping": [{
            "mtx1": transformation.mtx1.tolist(),
            "dist1": transformation.dist1.tolist(),

            "mtx2": transformation.mtx2.tolist(),
            "dist2": transformation.dist2.tolist(), 

            "loc": transformation.chessboard_loc,
            "height": transformation.height,
        }],

        "offset_X": transformation.offset_x,
        "offset_Y": transformation.offset_y
    }

    timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")

    with open(os.path.join(f"transformations/") + f"data_{timestamp}.json", "w") as json_file:
        json.dump(json_data, json_file, indent=3)

    # Return name for user to see
    name = f"data_{timestamp}.json"
    return name

def calculateOffset(transformation):
    mtx1 = transformation.mtx1
    dist1 = np.array([[0, 0, 0, 0, 0]], dtype=np.float32)

    mtx2 = transformation.mtx2
    dist2 = transformation.dist2

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    tag_size = transformation.tag_size
    
    if not tag_size or tag_size <= 0:
        msg = "Unavailable due to incorrect or missing data. (Tag size is invalid)"
        return msg
   
    object_points = np.array([
        [tag_size, 0, 0], 
        [0, 0, 0],
        [0, tag_size, 0],
        [tag_size, tag_size, 0],
        [tag_size/2, tag_size/2, 0]], dtype=np.float32)

    corner_x = transformation.tag_bottom_left[0]
    corner_y = transformation.tag_bottom_left[1]
    known_tag_corner = np.array([corner_x, corner_y, 0], dtype=np.float32)

    # Tag to Camera
    R_tag2cam_all = []
    t_tag2cam_all = []

    # Store all calculations to be averaged later
    probe_offset = []

    # Process images with known coordinates
    for i in range(4):
        img = getattr(transformation, f"img{i}")
        current_point = getattr(transformation, f"loc{i}")

        current_point = np.array([current_point[0], current_point[1], current_point[2]], dtype=np.float32)

        # Convert image to greyscale
        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find tag in image
        corners, ids, _ = detector.detectMarkers(image)
        if corners:
            corner_set = corners[0][0]
            centre = np.array([(corner_set[0][0]+corner_set[1][0])/2, (corner_set[0][1]+corner_set[3][1])/2], dtype=np.float32)
            corners = np.vstack([corners[0][0], centre])

            for j in range(len(corners)):
                corners[j] = undoSecondUnwarp(corners[j], mtx2, dist2)

            image_points = corners

            # Get extrinsic parameters for target to camera
            retval, rvec, tvec = cv2.solvePnP(object_points, image_points, mtx1, dist1, flags=cv2.SOLVEPNP_ITERATIVE)
            rvec, tvec = cv2.solvePnPRefineLM(object_points, image_points, mtx1, dist1, rvec, tvec)
            rvec, tvec = cv2.solvePnPRefineVVS(object_points, image_points, mtx1, dist1, rvec, tvec)

            R_tag2cam, _ = cv2.Rodrigues(rvec) # Convert to matrix

            # R_tag2cam = R, tvec = t for tag to camera
            R_tag2cam_all.append(R_tag2cam)
            t_tag2cam_all.append(tvec)

            # Get camera to tag (invert transformation)
            R_cam2tag = R_tag2cam.T
            t_cam2tag = -R_tag2cam.T @ tvec

            R_tag2base = np.eye(3) # No roation (move the same)
            t_tag2base = known_tag_corner.reshape(-1, 1)

            # Get camera to tag, tag to base = camera to base
            R_cam2base = R_tag2base @ R_cam2tag
            t_cam2base = R_tag2base @ t_cam2tag + t_tag2base

            # Get base to camera
            R_base2cam = R_cam2base.T
            t_base2cam = -R_cam2base.T @ t_cam2base

            # Get probe to base
            R_probe2base = np.eye(3)
            t_probe2base = current_point.reshape(-1, 1)

            # Get probe to base, base to camera = probe to camera
            R_probe2cam = R_base2cam @ R_probe2base
            t_probe2cam = R_base2cam @ t_probe2base + t_base2cam


            # Append calculated offset
            probe_offset.append(t_probe2cam)


    probe_locations_to_cam = np.array(probe_offset)
    probe_locations_to_cam_mean = np.mean(probe_locations_to_cam, axis=0)

    # Save output
    output = probe_locations_to_cam_mean.reshape(1, -1)[0]
    print(output)


    # Update transformation object
    transformation.offset_x = output[0]
    transformation.offset_y = output[1]


    # Update offset result in label
    msg = f"X: {round(output[0], 3)} mm, Y: {round(output[1], 3)} mm"
    return msg



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

def unwarpPhoto(img, transformation):

    img = fisheyeUnwarp(img, transformation.mtx1, transformation.dist1)
    img = secondUnwarp(img, transformation.mtx2, transformation.dist2)

    return img
