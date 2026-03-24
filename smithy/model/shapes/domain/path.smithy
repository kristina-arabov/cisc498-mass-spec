$version: "2.0"

namespace msrobot.domain.path

use msrobot.core.common#Duration
use msrobot.core.geometry#Resolution2D
use msrobot.domain.recording#SamplingMode
use msrobot.domain.roi#ROI

/// Path generation pattern
enum PathPattern {
    /// Zig-zag pattern (alternating direction rows)
    ZIGZAG

    /// Raster pattern (same direction rows)
    RASTER

    /// Spiral pattern (outward from center)
    SPIRAL
}

/// Single point in sampling path
structure PathPoint {
    /// Sequential index
    @required
    index: Integer

    /// X coordinate in mm
    @required
    x: Float

    /// Y coordinate in mm
    @required
    y: Float

    /// Z coordinate in mm (for CONSTANT_Z mode)
    z: Float
}

/// List of path points
list PathPointList {
    member: PathPoint
}

/// Path configuration
structure PathConfig {
    /// Spatial resolution
    @required
    resolution: Resolution2D

    /// Path pattern
    @required
    pattern: PathPattern

    /// Sampling mode
    @required
    mode: SamplingMode
}

/// Generated sampling path
structure SamplingPath {
    /// Ordered list of sampling points
    @required
    points: PathPointList

    /// Path configuration used
    @required
    config: PathConfig

    /// ROI used for generation
    @required
    roi: ROI

    /// Total number of points
    @required
    totalPoints: Integer

    /// Total path distance in mm
    @required
    totalDistanceMm: Float

    /// Estimated duration
    @required
    estimatedDuration: Duration
}

/// Path generation request
structure PathGenerationRequest {
    /// ROI to generate path within
    @required
    roi: ROI

    /// Path configuration
    @required
    config: PathConfig

    /// Dwell time for duration estimation
    @required
    dwellTime: Duration

    /// Pause time for duration estimation
    @required
    pauseTime: Duration
}

/// Path preview (lightweight version without full points)
structure PathPreview {
    /// Total number of points
    @required
    totalPoints: Integer

    /// Total path distance in mm
    @required
    totalDistanceMm: Float

    /// Estimated duration
    @required
    estimatedDuration: Duration

    /// First few points for preview
    @required
    previewPoints: PathPointList
}
