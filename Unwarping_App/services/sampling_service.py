import json
import numpy as np
import cv2
from collections import defaultdict

import time

from Unwarping_App.services import calibration_service


class SamplingItem():
    def __init__(self):
        super().__init__()

        self.rectangle = None
        self.drawn = None
        self.dot = None


        self.total_points = None
        self.sampled_points = None
        
        self.estimated_time = None

        self.gcodes = []
        self.timestamps = []
        self.readable_timestamps = []
        self.completed_gcodes = 0
        


def setTransformation(transformation, path, valid):

    try:
        # Parse transformatio. file
        with open(path, 'r') as file:
            data = json.load(file)

        
        # Set relevant values
        transformation.mtx1 = np.array(data["unwarping"][0]["mtx1"])
        transformation.dist1 = np.array(data["unwarping"][0]["dist1"])

        transformation.mtx2 = np.array(data["unwarping"][0]["mtx2"])
        transformation.dist2 = np.array(data["unwarping"][0]["dist2"])

        transformation.height = data["unwarping"][0]["height"]

        transformation.offset_x = data["offset_X"]
        transformation.offset_y = data["offset_Y"]

        valid = True
        file.close()
    
    except:
        valid = False

    return valid



# TODO fix bugginess ? why not working properly
def findLocations(transformation, sampling, img):
    print("working!")

    rectangle = img.rectangle
    dot = img.dot

    if not dot or not rectangle:
        print("NO DOT/ROI")
        return

    start_point = rectangle.topLeft()
    end_point = rectangle.bottomRight()

    print(start_point, end_point)
    print(dot)

    # Process original image (not scaled!)
    image = cv2.cvtColor(img.original_pixmap, cv2.COLOR_RGBA2GRAY)

    # Get printer position from photo
    pos = transformation.photo_loc

    # cv2.imshow("wat", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    mtx1 = transformation.mtx1
    mtx1[0][0] = mtx1[0][0] * 0.01
    mtx1[1][1] = mtx1[1][1] * 0.01

    dist1 = np.array([[0,0,0,0,0]], dtype=np.float32) # Set to no distortion

    mtx2 = transformation.mtx2
    dist2 = transformation.dist2


    # Detect tag in the image
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    corners, ids, _ = detector.detectMarkers(image)
    if not corners or len(corners) == 0:
        print("CANT DETECT TAG")
        return

    image_points = corners[0].reshape(-1, 2).astype(np.float32)
    

    # Apply tag size
    tag_size = transformation.tag_size
    object_points = np.array([
        [tag_size, 0, 0], 
        [0, 0, 0],
        [0, tag_size, 0],
        [tag_size, tag_size, 0]], dtype=np.float32)

    t = transformation.tag_bottom_left
    tag_corner = np.array([t[0], t[1], 0], dtype=np.float32)

    print(tag_size, tag_corner)


    retval, rvec, tvec = cv2.solvePnP(object_points, image_points, mtx1, dist1, flags=cv2.SOLVEPNP_ITERATIVE)
    rvec, tvec = cv2.solvePnPRefineLM(object_points, image_points, mtx1, dist1, rvec, tvec)
    rvec, tvec = cv2.solvePnPRefineVVS(object_points, image_points, mtx1, dist1, rvec, tvec)
    R_tag2cam, _ = cv2.Rodrigues(rvec) # convert to matrix

    # Get camera to tag (invert transformation)
    R_cam2tag = R_tag2cam.T
    t_cam2tag = -R_tag2cam.T @ tvec

    # Get tag to base
    R_base2tag = np.eye(3)
    t_base2tag = tag_corner.reshape(-1, 1)

    # Get camera to tag, tag to base = camera to base
    R_cam2base_overlay = R_base2tag @ R_cam2tag
    t_cam2base_overlay = R_base2tag @ t_cam2tag + t_base2tag

    R_base2cam = R_cam2base_overlay.T
    t_base2cam = -R_cam2base_overlay.T @ t_cam2base_overlay


    scale = 0.7 # TODO undo scale based on resolution

    # PROCESS DOT ----------------------------------------------
    sampling.dot = processDot(scale, transformation, dot, pos, R_cam2base_overlay)
    

    # PROCESS RECTANGLE --------------------------------------
    sampling.rectangle = processRectangle(scale, transformation, rectangle, pos, R_cam2base_overlay)


    print(vars(sampling))



# Function to get the 3D location of the reference point from a 2D location
def processDot(scale, transformation, dot, pos, cam2base):
    dot_unscaled = (int(dot.x() / scale), int(dot.y() / scale))
    new_dot = calibration_service.undoSecondUnwarp(dot_unscaled, transformation.mtx2, transformation.dist2)

    dot_from_cam_principal = getDirectionFromPixel(new_dot[0], new_dot[1], transformation.mtx1)
    dot_in_base = cam2base @ dot_from_cam_principal

    dot_x = pos[0] + (dot_in_base[0] * 10)
    dot_y = pos[1] + (dot_in_base[1] * 10)
    
    # Add probe offset to dot position
    dot_x += transformation.offset_x
    dot_y += transformation.offset_y

    probe_dot = [float(dot_x.item()), float(dot_y.item())]

    return probe_dot


# Function to get the 3D range of the rectangle from 2D points
def processRectangle(scale, transformation, rectangle, pos, cam2base):
    start_point = rectangle.topRight()
    end_point = rectangle.bottomLeft()

    start_unscaled = (int(start_point.x() / scale), int(start_point.y() / scale))
    end_unscaled = (int(end_point.x() / scale), int(end_point.y() / scale))

    start_point = calibration_service.undoSecondUnwarp(start_unscaled, transformation.mtx2, transformation.dist2)
    end_point = calibration_service.undoSecondUnwarp(end_unscaled, transformation.mtx2, transformation.dist2)

    start_point_from_cam_principal = getDirectionFromPixel(start_point[0], start_point[1], transformation.mtx1)
    end_point_from_cam_principal = getDirectionFromPixel(end_point[0], end_point[1], transformation.mtx1)

    start_point_in_base = cam2base @ start_point_from_cam_principal
    end_point_in_base = cam2base @ end_point_from_cam_principal

    # 3D start position
    start_x = pos[0] + (start_point_in_base[0] * 10)
    start_y = pos[1] + (start_point_in_base[1] * 10)

    start_x += transformation.offset_x
    start_y += transformation.offset_y

    # 3D end position
    end_x = pos[0] + (end_point_in_base[0] * 10)
    end_y = pos[1] + (end_point_in_base[1] * 10)

    end_x += transformation.offset_x
    end_y += transformation.offset_y


    probe_rectangle = [float(end_x.item()), float(end_y.item()), float(start_x.item()), float(start_y.item())]

    return probe_rectangle


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



def getSampling(sampling):
    # All sampling points + reference

    # Convert to serpentine pattern
    locations = [(100, 5), (110, 5), (120, 5), (100, 0), (110, 0), (120, 0), (100, -5), (110, -5), (120, -5)]
    locations = serpentinePath(locations)
    

    sampling.gcodes.append("G90")

    for i in locations:
        # Command: Go to (X, Y) location
        sampling.gcodes.append("G0 X"+str(round(i[0], 2))+" Y"+str(round(i[1], 2)))
        
        # Command: Go to Z sampling height
        sampling.gcodes.append("G0 Z"+ str(-5)) # TODO temp height

        # Command: Dwell for __ milliseconds
        dwell_time = int(6) * 1000 # TODO temp time
        sampling.gcodes.append(f"G4 P{str(dwell_time)}")

        # Command: Return to Z ransit height
        sampling.gcodes.append("G0 Z"+ str(0)) # TODO temp height


    sampling.completed_gcodes = 0
    sampling.timestamps = []
    sampling.readable_timestamps = [0]

    # Start timer
    sampling.timestamps.append(time.time())

    # print(sampling.gcodes)


# Function to sort 3D sampling locations into a serpentine pattern
def serpentinePath(locations):
    rows = defaultdict(list)

    for x, y in locations:
        rows[y].append((x, y))

    serpentine = []

    # Move down on Y and reverse X (alternating)
    for i, y in enumerate(sorted(rows, reverse=True)):
        row = sorted(rows[y])
        serpentine.extend(row if i % 2 == 0 else row[::-1])

    return serpentine


    # start_point = rectangle.topLeft()
    # end_point = rectangle.bottomRight()

    # if not dot or not rectangle:
    #     print("Nothing to sample or missing location for dot/rectangle.")
    #     return

    # # Process original image (not scaled!)
    # image = cv2.cvtColor(result.original_pixmap, cv2.COLOR_RGBA2GRAY)

    # if printer is None:
    #     print("Printer not connected, cannot generate probe locations without knowing the current position.")
    #     return
    
    # current_position = getPrinterPosition(printer)
    # current_position = np.array([current_position[0], current_position[1], current_position[2]], dtype=np.float32) # current position

    # # Open and read the JSON file
    # with open(json_file, 'r') as file:
    #     data = json.load(file)

    # unwarping = data["checkerboard"][0]
    # mtx1 = np.asarray(unwarping["mtx1"], dtype=np.float32)
    # mtx1[0][0] = mtx1[0][0] * 0.01
    # mtx1[1][1] = mtx1[1][1] * 0.01
    # dist1 = np.array([[0,0,0,0,0]], dtype=np.float32) # Set to no distortion

    # mtx2 = np.asarray(unwarping["mtx2"], dtype=np.float32)
    # dist2 = np.asarray(unwarping["dist2"], dtype=np.float32)

    # # Need tag in the image
    # dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    # parameters = cv2.aruco.DetectorParameters()
    # detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    # corners, ids, _ = detector.detectMarkers(image)
    # if not corners or len(corners) == 0:
    #     print("Cannot generate probe locations without tag")
    #     return

    # tag_size = data["tags"][0]["size"]
    # object_points = np.array([
    #     [tag_size, 0, 0], 
    #     [0, 0, 0],
    #     [0, tag_size, 0],
    #     [tag_size, tag_size, 0]], dtype=np.float32)
    
    # # json_corner = data["tags"][0]["corner1"]
    # # known_tag_corner = np.array([json_corner[0], json_corner[1], 0], dtype=np.float32)

    # known_tag_corner = np.array([float(corner.input.text()), float(corner.input2.text()), 0], dtype=np.float32)

    # image_points = corners[0].reshape(-1, 2).astype(np.float32)

    # for i in image_points:
    #     cv2.circle(image, (int(i[0]), int(i[1])), 5, (255, 255, 255), -1)

    # retval, rvec, tvec = cv2.solvePnP(object_points, image_points, mtx1, dist1, flags=cv2.SOLVEPNP_ITERATIVE)
    # rvec, tvec = cv2.solvePnPRefineLM(object_points, image_points, mtx1, dist1, rvec, tvec)
    # rvec, tvec = cv2.solvePnPRefineVVS(object_points, image_points, mtx1, dist1, rvec, tvec)
    # R_tag2cam, _ = cv2.Rodrigues(rvec) # convert to matrix

    # # get camera to tag (invert transformation)
    # R_cam2tag = R_tag2cam.T
    # t_cam2tag = -R_tag2cam.T @ tvec

    # # get tag to base
    # R_base2tag = np.eye(3)
    # t_base2tag = known_tag_corner.reshape(-1, 1)

    # # get camera to tag, tag to base = camera to base
    # global R_cam2base_overlay, t_cam2base_overlay
    # R_cam2base_overlay = R_base2tag @ R_cam2tag
    # t_cam2base_overlay = R_base2tag @ t_cam2tag + t_base2tag


    # R_base2cam = R_cam2base_overlay.T
    # t_base2cam = -R_cam2base_overlay.T @ t_cam2base_overlay

    # print(R_base2cam, t_base2cam)

    # '''
    #     Process dot
    # '''
    # dot_unscaled = (int(dot.x() / 0.7), int(dot.y() / 0.7))
    # new_dot = undoSecondUnwarp(dot_unscaled, mtx2, dist2)

    # dot_from_cam_principal = getDirectionFromPixel(new_dot[0], new_dot[1], mtx1)
    # dot_in_base = R_cam2base_overlay @ dot_from_cam_principal

    # dot_x = current_position[0] + (dot_in_base[0] * 10)
    # dot_y = current_position[1] + (dot_in_base[1] * 10)
    
    # # Add probe offset to dot position
    # dot_x += data["probe_offset"][0]
    # dot_y += data["probe_offset"][1]

    # probe_dot = (float(dot_x.item()), float(dot_y.item()))

    # '''
    #     Process rectangle 
    # '''
    # # Start and end points will be diagonal to each other?
    # start_point = rectangle.topRight()
    # end_point = rectangle.bottomLeft()
    # start_unscaled = (int(start_point.x() / 0.7), int(start_point.y() / 0.7))
    # end_unscaled = (int(end_point.x() / 0.7), int(end_point.y() / 0.7))

    # start_point = undoSecondUnwarp(start_unscaled, mtx2, dist2)
    # end_point = undoSecondUnwarp(end_unscaled, mtx2, dist2)

    # start_point_from_cam_principal = getDirectionFromPixel(start_point[0], start_point[1], mtx1)
    # end_point_from_cam_principal = getDirectionFromPixel(end_point[0], end_point[1], mtx1)

    # start_point_in_base = R_cam2base_overlay @ start_point_from_cam_principal
    # end_point_in_base = R_cam2base_overlay @ end_point_from_cam_principal


    # start_x = current_position[0] + (start_point_in_base[0] * 10)
    # start_y = current_position[1] + (start_point_in_base[1] * 10)

    # start_x += data["probe_offset"][0]
    # start_y += data["probe_offset"][1]


    # end_x = current_position[0] + (end_point_in_base[0] * 10)
    # end_y = current_position[1] + (end_point_in_base[1] * 10)

    # end_x += data["probe_offset"][0]
    # end_y += data["probe_offset"][1]


    # probe_rectangle = [float(end_x.item()), float(end_y.item()), float(start_x.item()), float(start_y.item())]

    # print("DOT --> ", probe_dot)
    # print("RECTANGLE --> ", probe_rectangle)
    # result.probe_dot = probe_dot
    # result.probe_rectangle = probe_rectangle
