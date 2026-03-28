$version: "2.0"

namespace msrobot.domain.recording

use msrobot.core.common#Duration
use msrobot.core.geometry#Position2D
use msrobot.core.geometry#Range
use msrobot.core.geometry#Resolution2D

/// Sampling mode. Stored in SamplingItem.mode as the lowercase string shown below.
enum SamplingMode {
    /// "constant" — probe descends to a fixed sampleHeight and dwells.
    CONSTANT_Z

    /// "conductive" — probe steps down by stepSize until conductance threshold is crossed.
    CONDUCTANCE

    /// "drag" — probe moves at fixed sampleHeight across the surface continuously.
    DRAG
}

/// XY and Z travel speeds. Accelerations are hardcoded in gcodegen.py (XY 1250, Z 400 mm/s²).
structure MotionConfig {
    /// SamplingItem.xy_speed (mm/min)
    @required
    xySpeed: Float

    /// SamplingItem.z_down_speed (mm/min)
    @required
    zDownSpeed: Float

    /// SamplingItem.z_up_speed (mm/min)
    @required
    zUpSpeed: Float
}

/// Reference point sampled at the start of every run before the main scan.
structure ReferenceConfig {
    /// XY stage position (sampling.dot = [x, y]).
    @required
    position: Position2D

    /// "constant" or "conductive" only (DRAG not supported for reference).
    /// SamplingItem.ref_mode
    @required
    refMode: SamplingMode

    /// G4 dwell at transit height after the reference measurement (seconds). SamplingItem.ref_dwellTime
    @required
    dwellTime: Duration

    /// Recording window at reference sample height (seconds). SamplingItem.ref_sampleTime
    @required
    sampleTime: Duration

    /// Z height to probe at the reference point (mm). SamplingItem.ref_sampleHeight
    @required
    sampleHeight: Float

    /// Z step size for CONDUCTANCE mode (mm). SamplingItem.ref_stepSize
    stepSize: Float
}

/// Full sampling run configuration. Fields map directly to SamplingItem attributes.
structure RecordingConfig {
    /// Point spacing in X and Y (mm). SamplingItem.spatialRes_X / spatialRes_Y
    @required
    resolution: Resolution2D

    /// Recording window at each sample point while at sampleHeight (seconds). SamplingItem.sampleTime
    @required
    sampleTime: Duration

    /// G4 dwell at transitHeight after each sample, before moving to the next point (seconds). SamplingItem.dwellTime
    @required
    dwellTime: Duration

    /// SamplingItem.mode
    @required
    samplingMode: SamplingMode

    /// Z height the probe retracts to between sample points (mm). SamplingItem.transitHeight
    @required
    transitHeight: Float

    /// Fixed Z sample height for CONSTANT_Z mode (mm). SamplingItem.sampleHeight
    sampleHeight: Float

    /// Contact detection range in μS for CONDUCTANCE mode. SamplingItem.con_threshold
    conductanceThreshold: Range

    /// Z step size per increment in CONDUCTANCE mode (mm). SamplingItem.stepSize
    stepSize: Float

    @required
    motion: MotionConfig

    reference: ReferenceConfig
}
