$version: "2.0"

namespace msrobot.services.calibration

use msrobot.core.geometry#Position2D
use msrobot.core.geometry#Position3D
use msrobot.domain.calibration#Calibration
use msrobot.domain.calibration#CalibrationId

@title("Calibration Service")
service CalibrationService {
    version: "2.0.0"
    operations: [
        LoadCalibration
        TransformPixelToStage
    ]
}

/// Load a calibration JSON file. Implemented by p1_provide_transformation.py + sampling_service.setTransformation().
operation LoadCalibration {
    input: LoadCalibrationInput
    output: LoadCalibrationOutput
}

@input
structure LoadCalibrationInput {
    /// Full path to the calibration JSON (e.g. transformations/data_03-27-2026_14-35-22.json).
    @required
    calibrationId: String
}

@output
structure LoadCalibrationOutput {
    @required
    calibration: Calibration
}

/// Transform a pixel coordinate to stage mm. Implemented by sampling_service.findLocations().
operation TransformPixelToStage {
    input: TransformPixelToStageInput
    output: TransformPixelToStageOutput
}

@input
structure TransformPixelToStageInput {
    /// Uses the currently loaded calibration if omitted.
    calibrationId: CalibrationId

    @required
    pixelPosition: Position2D
}

@output
structure TransformPixelToStageOutput {
    @required
    stagePosition: Position3D

    @required
    success: Boolean

    errorMessage: String
}
