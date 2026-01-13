$version: "2.0"

namespace msrobot.domain.calibration

use msrobot.core.common#FilePath
use msrobot.core.common#Timestamp
use msrobot.core.geometry#FloatList
use msrobot.core.geometry#Matrix3x3
use msrobot.core.geometry#Matrix4x4
use msrobot.core.geometry#Position3D
use msrobot.core.geometry#Quaternion
use msrobot.core.geometry#Resolution
use msrobot.core.geometry#Vector3D

/// Unique identifier for a calibration
string CalibrationId

/// Camera calibration type
enum CalibrationType {
    /// OpenCV standard distortion model
    STANDARD

    /// OpenCV fisheye distortion model
    FISHEYE

    /// Rational polynomial model
    RATIONAL
}

/// Hand-eye calibration method
enum HandEyeMethod {
    /// Tsai-Lenz method
    TSAI_LENZ

    /// Park-Martin method
    PARK_MARTIN

    /// Daniilidis method
    DANIILIDIS

    /// AprilTag-based calibration
    APRILTAG

    /// Manual calibration
    MANUAL
}

/// Camera hardware information
structure CameraInfo {
    /// Camera type identifier (e.g., "ELP_HD_FISHEYE")
    @required
    cameraType: String

    /// USB device index
    @required
    deviceIndex: Integer

    /// Camera resolution
    @required
    resolution: Resolution

    /// Frames per second
    @required
    fps: Integer

    /// Serial number if available
    serialNumber: String

    /// Firmware version if available
    firmwareVersion: String
}

/// Camera intrinsic calibration parameters
structure CameraIntrinsics {
    /// 3x3 camera intrinsic matrix (K)
    @required
    cameraMatrix: Matrix3x3

    /// Distortion coefficients
    @required
    distortionCoeffs: FloatList

    /// Type of calibration model
    @required
    calibrationType: CalibrationType

    /// Image size used for calibration
    @required
    imageSize: Resolution

    /// RMS reprojection error
    @required
    rmsError: Float

    /// Checkerboard pattern size (cols, rows)
    @required
    checkerboardCols: Integer

    /// Checkerboard rows
    @required
    checkerboardRows: Integer

    /// Checkerboard square size in mm
    @required
    squareSizeMm: Float
}

/// Hand-eye (arm-to-camera) calibration
structure HandEyeCalibration {
    /// 4x4 homogeneous transformation matrix
    @required
    transformMatrix: Matrix4x4

    /// Rotation as quaternion
    @required
    rotation: Quaternion

    /// Translation vector in mm
    @required
    translation: Vector3D

    /// Calibration method used
    @required
    method: HandEyeMethod

    /// Probe offset from end-effector in mm
    @required
    probeOffset: Vector3D

    /// Reprojection error in pixels
    @required
    reprojectionError: Float

    /// Position error in mm
    @required
    positionError: Float
}

/// Validation test point
structure ValidationPoint {
    /// Pixel coordinates
    @required
    pixelX: Integer

    /// Pixel Y coordinate
    @required
    pixelY: Integer

    /// Expected position in mm
    @required
    expectedPosition: Position3D

    /// Actual measured position in mm
    @required
    actualPosition: Position3D

    /// Error in mm
    @required
    errorMm: Float
}

/// List of validation points
list ValidationPointList {
    member: ValidationPoint
}

/// Calibration validation results
structure CalibrationValidation {
    /// Whether calibration is valid
    @required
    isValid: Boolean

    /// Test points used for validation
    @required
    testPoints: ValidationPointList

    /// Mean error in mm
    @required
    meanErrorMm: Float

    /// Maximum error in mm
    @required
    maxErrorMm: Float

    /// Validation timestamp
    @required
    validatedAt: Timestamp
}

/// Complete calibration aggregate
structure Calibration {
    /// Unique calibration identifier
    @required
    id: CalibrationId

    /// Auto-generated name from timestamp
    @required
    name: String

    /// Creation timestamp
    @required
    createdAt: Timestamp

    /// Camera hardware information
    @required
    cameraInfo: CameraInfo

    /// Camera intrinsic calibration
    @required
    intrinsics: CameraIntrinsics

    /// Hand-eye calibration (extrinsics)
    @required
    extrinsics: HandEyeCalibration

    /// Validation results
    @required
    validation: CalibrationValidation

    /// File path where calibration is stored
    @required
    filePath: FilePath
}

/// Summary of a calibration for listing
structure CalibrationSummary {
    /// Calibration ID
    @required
    id: CalibrationId

    /// Calibration name
    @required
    name: String

    /// Creation timestamp
    @required
    createdAt: Timestamp

    /// Whether calibration is valid
    @required
    isValid: Boolean

    /// Mean error in mm
    @required
    meanErrorMm: Float

    /// File path
    @required
    filePath: FilePath
}

/// List of calibration summaries
list CalibrationSummaryList {
    member: CalibrationSummary
}
