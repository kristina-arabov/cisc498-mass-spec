import json
import re
import numpy as np
import cv2
from collections import defaultdict

import time

from Unwarping_App.services import calibration_service

import csv
from datetime import datetime


class SamplingItem():
    def __init__(self):
        super().__init__()

        self.rectangle = None
        self.drawn = None
        self.dot = None

        # Sampling parameters
        self.spatialRes_X = None
        self.spatialRes_Y = None

        self.dwellTime = None
        self.sampleTime = None

        self.transitHeight = None
        self.sampleHeight = None

        # Speed
        self.xy_speed = None
        self.z_down_speed = None
        self.z_up_speed = None


        self.startLoc = None
        self.originalLoc = [0, 0, 0]

        # TODO allow mode to change
        self.mode = None

        # Gcode info
        self.estimated_time = None

        self.gcodes = []
        self.completed_gcodes = []

        self.total_points = 0
        self.sampled_points = 0

        self.timestamps = []
        self.readable_timestamps = []
        
        self.moving = False
        self.paused = False

        # File info
        self.csv_filename = None
        self.csv_rows = []
        

samplingItem = SamplingItem()

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

    sampling.originalLoc = transformation.photo_loc

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
    # TODO change to real locations
    locations = [(180.4, 5), (182.4, 5), (184.4, 5), (180.4, 0), (182.4, 0), (184.4, 0), (178.4, -5), (180.4, -5), (182.4, -5)]

    # If using drag mode, locations will need to follow a serpentine pattern, but 
    # only move along the XY coordinates with no Z movement
    if sampling.mode == "drag":
        locations = serpentineDrag(locations)
    
    # Standard serpentine pattern for Constant Z and Conductance modes
    else:
        locations = serpentinePath(locations)

    # Reset values
    sampling.total_points = len(locations)
    sampling.sampled_points = 0

    sampling.completed_gcodes = []
    sampling.timestamps = []
    sampling.readable_timestamps = []

    print(f"path: {locations}")

    if sampling.mode == "constant":
        
        sampling.gcodes.append("G90") # Absolute positioning
        sampling.gcodes.append("G0 Z"+ str(sampling.transitHeight)) # Always go to transit height first

        for i in locations:
            # Command: Go to (X, Y) location
            sampling.gcodes.append("G0 X"+str(round(i[0], 2))+" Y"+str(round(i[1], 2)))
            
            # Command: Go to Z sampling height
            sampling.gcodes.append("G0 Z"+ str(sampling.sampleHeight))

            # Command: Sample for __ milliseconds
            sample_time = int(sampling.sampleTime) * 1000 
            sampling.gcodes.append(f"G4 P{str(sample_time)}")

            # Command: Return to Z transit height
            sampling.gcodes.append("G0 Z"+ str(sampling.transitHeight))

            # Command: Dwell for __ milliseconds
            dwell_time = int(sampling.dwellTime) * 1000
            sampling.gcodes.append(f"G4 P{str(dwell_time)}")


    # elif sampling.mode == "conductive":
    #     print("conductive selected")

    #     sampling.gcodes.append("G90") # Absolute positioning
    #     sampling.gcodes.append("G0 Z"+ str(sampling.transitHeight)) # Always go to transit height first

    #     for i in locations:
    #         # Command: Go to (X, Y) location
    #         sampling.gcodes.append("G0 X"+str(round(i[0], 2))+" Y"+str(round(i[1], 2)))

    #         # Command: Move down until conductance detected
    #         # TODO... how to move down until detected?
    #         sampling.gcodes.append("G91")
    #         sampling.gcodes.append(f"G0 Z-{0.5} F{10}")
    #         sampling.gcodes.append("G90")

    #         # Command: Sample for __ milliseconds
    #         sample_time = int(sampling.sampleTime) * 1000 
    #         sampling.gcodes.append(f"G4 P{str(sample_time)}")

    #         # Command: Return to transit height
    #         sampling.gcodes.append("G0 Z"+ str(sampling.transitHeight))

    #         # Command: Dwell for __ milliseconds
    #         dwell_time = int(sampling.dwellTime) * 1000
    #         sampling.gcodes.append(f"G4 P{str(dwell_time)}")


    # Drag sampling mode
    elif sampling.mode == "drag":
        initial = locations[0]

        sampling.gcodes.append("G90") # Absolute positioning

        # If current height is above transit height, use DOWN speed
        if sampling.originalLoc[2] >= sampling.transitHeight:
            sampling.gcodes.append(f"G0 Z{str(sampling.transitHeight)} F{str(sampling.z_down_speed)}")
        
        # Else if current height is below trasit height, use UP speed
        elif sampling.originalLoc[2] < sampling.transitHeight:
            sampling.gcodes.append(f"G0 Z{str(sampling.transitHeight)} F{str(sampling.z_up_speed)}")

        # Command: Move to first X, Y position
        sampling.gcodes.append(f"G0 X{str(round(initial[0], 2))} Y{str(round(initial[1], 2))} F{str(sampling.xy_speed)}") 

        # Command: # Lower to sampling height
        sampling.gcodes.append(f"G0 Z{str(sampling.sampleHeight)} F{str(sampling.z_down_speed)}") 

        locations.pop(0) # Remove first location since printer will start there

        for i in locations:
            # Move to each (X,Y) location at the specified XY speed, No Z movement
            sampling.gcodes.append(f"G0 X{str(round(i[0], 2))} Y{str(round(i[1], 2))} F{str(sampling.xy_speed)}")
            
        # Move back to transit height
        sampling.gcodes.append(f"G0 Z{str(sampling.transitHeight)} F{str(sampling.z_up_speed)}")

    # Return to original position
    # p = sampling.originalLoc
    p = [180.4, -3, 0]
    sampling.gcodes.append(f"G0 X{str(round(p[0], 2))} Y{str(round(p[1], 2))} F{str(sampling.xy_speed)}")
    sampling.gcodes.append(f"G0 Z{str(p[2])}")

    # Start timer to begin run
    sampling.timestamps.append(time.time())
    sampling.readable_timestamps.append(0)

    for row in sampling.gcodes:
        print(row)



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


# Function to apply serpentine pathing for drag sampling
def serpentineDrag(locations):
    rows = defaultdict(list)

    # Group X values by Y
    for x, y in locations:
        rows[y].append(x)

    ys = sorted(rows, reverse=True)
    result = []

    for i in range(len(ys)):
        y = ys[i]
        row_min = min(rows[y])
        row_max = max(rows[y])

        # Last row
        if i == len(ys) - 1:
            if i % 2 == 0:
                # Left to right
                start = (row_min, y)
                end = (row_max, y)
            else:
                # Right to left
                start = (row_max, y)
                end = (row_min, y)

        else:
            next_y = ys[i + 1]
            next_min = min(rows[next_y])
            next_max = max(rows[next_y])

            if i % 2 == 0:
                # Left to right
                start = (row_min, y)
                end = (next_max, y)
            else:
                # Right to left
                start = (row_max, y)
                end = (next_min, y)

        # Add locations
        result.append(start)
        result.append(end)

    return result


# Function to get time stamp between operations
def getTime():
    samplingItem.timestamps.append(time.time())
    # print(samplingItem.timestamps)

    achieved_time = samplingItem.timestamps[-1] - samplingItem.timestamps[-2]
    samplingItem.readable_timestamps.append(samplingItem.readable_timestamps[-1] + achieved_time)

    # Return most recent timestamp to spreadsheet
    return samplingItem.readable_timestamps[-1]


# Function to send a GCode to the printer and remove it from the queue
def runGCode(printer):
    line = samplingItem.gcodes.pop(0)

    samplingItem.completed_gcodes.append(line)

    printer.cmd(line)

    # emit signal for completed points? time?


# Function to add a row containing time + position data to the spreadsheet
def addData(printer, conductance):
    # Get time and printer position at this moment
    time_val = int(getTime() * 1000)
    pos = printer.pos if printer.pos is not None else [0, 0, 0]
    c = conductance.connection.read() if conductance is not None else 0
    # pos = [1, 2, 3]

    # Open file and add row to it
    with open(samplingItem.csv_filename, "a", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([time_val, c, pos[0], pos[1], pos[2]])



# Function to create new CSV files
def createCSV():
    current_time = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    samplingItem.csv_filename = f"collectedData/sampleRun_{current_time}.csv"

    # Create and write to the CSV
    with open(samplingItem.csv_filename, "w", newline="") as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow(["Time (ms)", "Conductance", "X", "Y", "Z"])



def stop(printer):
    # Clear GCodes and sampling data
    samplingItem.csv_filename = None
    samplingItem.csv_rows = []

    samplingItem.estimated_time = None

    samplingItem.gcodes = []
    samplingItem.completed_gcodes = []

    samplingItem.total_points = 0
    samplingItem.sampled_points = 0

    samplingItem.timestamps = []
    samplingItem.readable_timestamps = []
    
    samplingItem.moving = False
    samplingItem.paused = False


    # Move printer to original position
    p = samplingItem.originalLoc

    # printer.cmd("G90")
    # printer.cmd("G0 X"+str(p[0])+" Y"+str(p[1]))
    # printer.cmd("G0 Z"+str(p[2]))

    


def pause(printer):
    printer.last_pos = printer.pos
    # if self.conductance_mode:
    #     self.cmd("G90")
    #     self.cmd("G0 Z100 F3000")
    #     self.cmd("G0 X10 Y10 Z100 F3000")
    #     self.cmd("G91")
    # else:
    # printer.cmd("G91")
    # printer.cmd("G0 Z15 F3000")
    # printer.cmd("G0 X10 Y10 F3000")
    # printer.cmd("G90")
    
    samplingItem.paused = True


def resume(printer):
    print("resuming")
    print("sending to", printer.last_pos)

    print(printer.last_pos)

    # if self.conductance_mode:
    #     self.cmd("G90")
    #     self.cmd("G0 X"+str(self.last_pos[0])+" Y"+str(self.last_pos[1])+ " Z"+str(self.last_pos[2])+" F2000")
    #     self.cmd("G91")

    samplingItem.paused = False

    printer.cmd("G90")
    printer.cmd("G0 X"+str(printer.last_pos[0])+" Y"+str(printer.last_pos[1])+ " Z"+str(printer.last_pos[2]))

    

    # Ensure file is saved

    # TODO Return to initial position? or emergency position?
    # Currently emergency position

    # printer.cmd("G0 Z100 F3000")
    # printer.cmd("G0 X10 Y10 Z100 F3000")


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
