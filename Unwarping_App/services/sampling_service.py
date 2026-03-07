import json
import numpy as np

from Unwarping_App.services import calibration_service

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
