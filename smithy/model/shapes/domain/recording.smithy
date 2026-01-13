$version: "2.0"

namespace msrobot.domain.recording

use msrobot.core.common#Duration
use msrobot.core.common#FilePath
use msrobot.core.common#Timestamp
use msrobot.core.geometry#Position3D
use msrobot.core.geometry#Range
use msrobot.core.geometry#Resolution2D
use msrobot.domain.path#SamplingPath
use msrobot.domain.roi#ROI
use msrobot.domain.session#SessionId

/// Unique identifier for a recording
string RecordingId

/// Recording status
enum RecordingStatus {
    /// Recording created
    CREATED

    /// Configuring recording parameters
    CONFIGURING

    /// Path has been generated
    PATH_GENERATED

    /// Ready to start
    READY

    /// Recording in progress
    RUNNING

    /// Recording paused
    PAUSED

    /// Completing (finalizing)
    COMPLETING

    /// Recording completed successfully
    COMPLETED

    /// Recording aborted by user
    ABORTED

    /// Recording ended with error
    ERROR
}

/// Sampling mode
enum SamplingMode {
    /// Fixed Z height for flat samples
    CONSTANT_Z

    /// Probe until conductance detected
    CONDUCTANCE
}

/// When to sample reference point
enum ReferenceWhen {
    /// Sample at start only
    START

    /// Sample at end only
    END

    /// Sample at both start and end
    START_AND_END
}

/// Motion configuration
structure MotionConfig {
    /// XY travel speed in mm/min
    @required
    xySpeed: Float

    /// Z probe (descent) speed in mm/min
    @required
    zProbeSpeed: Float

    /// Z retract speed in mm/min
    @required
    zRetractSpeed: Float

    /// XY acceleration in mm/s²
    @required
    xyAcceleration: Float

    /// Z acceleration in mm/s²
    @required
    zAcceleration: Float
}

/// Reference point configuration
structure ReferenceConfig {
    /// Reference position
    @required
    position: Position3D

    /// When to sample reference
    @required
    when: ReferenceWhen

    /// Dwell time at reference
    @required
    dwellTime: Duration

    /// Sample time at reference
    @required
    sampleTime: Duration
}

/// Recording configuration (immutable snapshot)
structure RecordingConfig {
    /// Spatial resolution
    @required
    resolution: Resolution2D

    /// Dwell time at each sample point
    @required
    dwellTime: Duration

    /// Pause time between samples
    @required
    pauseTime: Duration

    /// Sampling mode
    @required
    mode: SamplingMode

    /// Z height for CONSTANT_Z mode
    constantZ: Float

    /// Conductance threshold range
    conductanceThreshold: Range

    /// Probe step size in mm for CONDUCTANCE mode
    probeStep: Float

    /// Motion configuration
    @required
    motion: MotionConfig

    /// Reference point configuration
    reference: ReferenceConfig
}

/// Recording statistics (updated in real-time)
structure RecordingStatistics {
    /// Number of samples completed
    @required
    samplesCompleted: Integer

    /// Number of samples skipped
    @required
    samplesSkipped: Integer

    /// Number of samples with errors
    @required
    samplesError: Integer

    /// Elapsed time
    @required
    elapsedTime: Duration

    /// Estimated remaining time
    @required
    estimatedRemaining: Duration

    /// Average time per sample
    @required
    averageSampleTime: Duration

    /// Average conductance reading
    averageConductance: Float

    /// Minimum Z contact height
    minZ: Float

    /// Maximum Z contact height
    maxZ: Float
}

/// Recording aggregate root
structure Recording {
    /// Unique recording identifier
    @required
    id: RecordingId

    /// Parent session ID
    @required
    sessionId: SessionId

    /// Recording name
    @required
    name: String

    /// Creation timestamp
    @required
    createdAt: Timestamp

    /// Start timestamp
    startedAt: Timestamp

    /// Pause timestamp
    pausedAt: Timestamp

    /// Completion timestamp
    completedAt: Timestamp

    /// Recording configuration
    @required
    config: RecordingConfig

    /// Region of interest
    roi: ROI

    /// Generated sampling path
    path: SamplingPath

    /// Current status
    @required
    status: RecordingStatus

    /// Current sample index
    @required
    currentSampleIndex: Integer

    /// Total expected samples
    @required
    totalSamples: Integer

    /// Path to .msrbt file
    @required
    msrbtFile: FilePath

    /// Path to temporary G-code buffer
    tempGcodeFile: FilePath

    /// Recording statistics
    @required
    statistics: RecordingStatistics
}

/// Summary of a recording for listing
structure RecordingSummary {
    /// Recording ID
    @required
    id: RecordingId

    /// Recording name
    @required
    name: String

    /// Status
    @required
    status: RecordingStatus

    /// Samples completed
    @required
    samplesCompleted: Integer

    /// Total samples
    @required
    totalSamples: Integer

    /// Path to .msrbt file
    @required
    msrbtFile: FilePath
}

/// List of recording summaries
list RecordingSummaryList {
    member: RecordingSummary
}
