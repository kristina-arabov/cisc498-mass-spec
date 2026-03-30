$version: "2.0"

namespace msrobot.domain.calibration

use msrobot.core.common#FilePath
use msrobot.core.common#Timestamp
use msrobot.core.geometry#FloatList
use msrobot.core.geometry#Matrix3x3

/// Calibration file path used as the effective identifier (e.g. transformations/data_03-27-2026_14-35-22.json).
string CalibrationId

/// Unwarp pipeline parameters — the sole element of the "unwarping" array in the calibration JSON.
/// Two-pass pipeline: fisheye (cv2.fisheye → mtx1/dist1) then perspective correction (cv2.calibrateCamera → mtx2/dist2).
structure UnwarpingParams {
    /// Fisheye intrinsic matrix (3×3). JSON key: "mtx1"
    @required
    mtx1: Matrix3x3

    /// Fisheye distortion coefficients [k1, k2, k3, k4]. JSON key: "dist1"
    @required
    dist1: FloatList

    /// Perspective correction matrix (3×3). JSON key: "mtx2"
    @required
    mtx2: Matrix3x3

    /// Perspective correction distortion coefficients. JSON key: "dist2"
    @required
    dist2: FloatList

    /// Stage position [x, y, z] in mm when the chessboard image was captured. JSON key: "loc"
    @required
    loc: FloatList

    /// Z height of the calibration chessboard in mm. JSON key: "height"
    @required
    height: Float
}

/// Always contains exactly one UnwarpingParams element.
list UnwarpingParamsList {
    member: UnwarpingParams
}

/// Complete calibration data. Written by calibration_service.createTransformationFile(),
/// read by sampling_service.setTransformation(). Saved to transformations/data_MM-DD-YYYY_HH-MM-SS.json.
structure Calibration {
    /// JSON key: "unwarping" (always one element)
    @required
    unwarping: UnwarpingParamsList

    /// Camera-to-probe X offset in mm. JSON key: "offset_X"
    @required
    offsetX: Float

    /// Camera-to-probe Y offset in mm. JSON key: "offset_Y"
    @required
    offsetY: Float

    @required
    filePath: FilePath

    /// Parsed from the filename (data_MM-DD-YYYY_HH-MM-SS.json).
    @required
    createdAt: Timestamp
}
