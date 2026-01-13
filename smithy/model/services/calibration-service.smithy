$version: "2.0"

namespace msrobot.services.calibration

use msrobot.core.common#FilePath
use msrobot.core.geometry#Position2D
use msrobot.core.geometry#Position3D
use msrobot.domain.calibration#Calibration
use msrobot.domain.calibration#CalibrationId
use msrobot.domain.calibration#CalibrationSummaryList
use msrobot.domain.calibration#CalibrationValidation

/// Service for managing calibrations (singleton repository)
@title("Calibration Service")
service CalibrationService {
    version: "2.0.0"
    operations: [
        RunCalibration
        CancelCalibration
        LoadCalibration
        SaveCalibration
        DeleteCalibration
        GetLatestCalibration
        ListCalibrations
        ValidateCalibration
        GetCalibrationStatus
        // Coordinate transformation
        TransformPixelToStage
        TransformStageToPixel
        TransformBatchPixelsToStage
    ]
}

/// Calibration status during automated calibration
enum CalibrationPhase {
    /// Not started
    NOT_STARTED

    /// Capturing checkerboard images
    CAPTURING_CHECKERBOARD

    /// Computing camera intrinsics
    COMPUTING_INTRINSICS

    /// Capturing probe/tag images
    CAPTURING_PROBE

    /// Computing hand-eye calibration
    COMPUTING_EXTRINSICS

    /// Validating calibration
    VALIDATING

    /// Calibration complete
    COMPLETED

    /// Calibration failed
    FAILED
}

/// Run automated calibration procedure
operation RunCalibration {
    input: RunCalibrationInput
    output: RunCalibrationOutput
}

@input
structure RunCalibrationInput {
    /// Checkerboard columns (inner corners)
    @required
    checkerboardCols: Integer

    /// Checkerboard rows (inner corners)
    @required
    checkerboardRows: Integer

    /// Checkerboard square size in mm
    @required
    squareSizeMm: Float

    /// Output directory for calibration file
    outputDirectory: FilePath
}

@output
structure RunCalibrationOutput {
    /// Created calibration
    @required
    calibration: Calibration
}

/// Load calibration from file
operation LoadCalibration {
    input: LoadCalibrationInput
    output: LoadCalibrationOutput
}

@input
structure LoadCalibrationInput {
    /// Calibration ID or file path
    @required
    calibrationId: String
}

@output
structure LoadCalibrationOutput {
    /// Loaded calibration
    @required
    calibration: Calibration
}

/// Save calibration to file
operation SaveCalibration {
    input: SaveCalibrationInput
    output: SaveCalibrationOutput
}

@input
structure SaveCalibrationInput {
    /// Calibration ID
    @required
    calibrationId: CalibrationId

    /// Calibration data
    @required
    calibration: Calibration
}

@output
structure SaveCalibrationOutput {
    /// Success response
    @required
    success: Boolean

    /// Saved file path
    @required
    filePath: FilePath
}

/// Get the most recent calibration
operation GetLatestCalibration {
    input: GetLatestCalibrationInput
    output: GetLatestCalibrationOutput
}

@input
structure GetLatestCalibrationInput {
    /// Calibrations directory (optional, uses default if not provided)
    calibrationsDirectory: FilePath
}

@output
structure GetLatestCalibrationOutput {
    /// Latest calibration (null if none exists)
    calibration: Calibration
}

/// List all calibrations
operation ListCalibrations {
    input: ListCalibrationsInput
    output: ListCalibrationsOutput
}

@input
structure ListCalibrationsInput {
    /// Calibrations directory (optional, uses default if not provided)
    calibrationsDirectory: FilePath
}

@output
structure ListCalibrationsOutput {
    /// List of calibration summaries
    @required
    calibrations: CalibrationSummaryList
}

/// Validate an existing calibration
operation ValidateCalibration {
    input: ValidateCalibrationInput
    output: ValidateCalibrationOutput
}

@input
structure ValidateCalibrationInput {
    /// Calibration ID
    @required
    calibrationId: CalibrationId

    /// Number of test points to use
    @required
    testPointCount: Integer
}

@output
structure ValidateCalibrationOutput {
    /// Validation results
    @required
    validation: CalibrationValidation
}

/// Get status of running calibration
operation GetCalibrationStatus {
    input: GetCalibrationStatusInput
    output: GetCalibrationStatusOutput
}

@input
structure GetCalibrationStatusInput {}

@output
structure GetCalibrationStatusOutput {
    /// Current phase
    @required
    phase: CalibrationPhase

    /// Progress within current phase (0-100)
    @required
    progressPercent: Float

    /// Status message
    @required
    message: String

    /// Error message if failed
    errorMessage: String
}

/// Cancel a running calibration
operation CancelCalibration {
    input: CancelCalibrationInput
    output: CancelCalibrationOutput
}

@input
structure CancelCalibrationInput {}

@output
structure CancelCalibrationOutput {
    /// Success
    @required
    success: Boolean
}

/// Delete a calibration file
operation DeleteCalibration {
    input: DeleteCalibrationInput
    output: DeleteCalibrationOutput
}

@input
structure DeleteCalibrationInput {
    /// Calibration ID
    @required
    calibrationId: CalibrationId
}

@output
structure DeleteCalibrationOutput {
    /// Success
    @required
    success: Boolean
}

// ============================================================================
// Coordinate Transformation Operations
// ============================================================================
/// Transform pixel coordinates to stage coordinates
operation TransformPixelToStage {
    input: TransformPixelToStageInput
    output: TransformPixelToStageOutput
}

@input
structure TransformPixelToStageInput {
    /// Calibration to use (uses current session calibration if not provided)
    calibrationId: CalibrationId

    /// Pixel coordinates
    @required
    pixelPosition: Position2D
}

@output
structure TransformPixelToStageOutput {
    /// Stage coordinates (X, Y in mm, Z is typically 0)
    @required
    stagePosition: Position3D

    /// Whether transform was successful
    @required
    success: Boolean

    /// Error message if transform failed
    errorMessage: String
}

/// Transform stage coordinates to pixel coordinates
operation TransformStageToPixel {
    input: TransformStageToPixelInput
    output: TransformStageToPixelOutput
}

@input
structure TransformStageToPixelInput {
    /// Calibration to use (uses current session calibration if not provided)
    calibrationId: CalibrationId

    /// Stage coordinates (X, Y in mm)
    @required
    stagePosition: Position3D
}

@output
structure TransformStageToPixelOutput {
    /// Pixel coordinates
    @required
    pixelPosition: Position2D

    /// Whether transform was successful
    @required
    success: Boolean

    /// Error message if transform failed
    errorMessage: String
}

/// Transform multiple pixel coordinates to stage coordinates (batch operation)
operation TransformBatchPixelsToStage {
    input: TransformBatchPixelsToStageInput
    output: TransformBatchPixelsToStageOutput
}

@input
structure TransformBatchPixelsToStageInput {
    /// Calibration to use (uses current session calibration if not provided)
    calibrationId: CalibrationId

    /// List of pixel coordinates
    @required
    pixelPositions: Position2DList
}

list Position2DList {
    member: Position2D
}

list Position3DList {
    member: Position3D
}

@output
structure TransformBatchPixelsToStageOutput {
    /// Stage coordinates
    @required
    stagePositions: Position3DList

    /// Whether all transforms were successful
    @required
    success: Boolean

    /// Number of successful transforms
    @required
    successCount: Integer

    /// Error message if any transforms failed
    errorMessage: String
}
