$version: "2.0"

namespace msrobot.domain.sample

use msrobot.core.common#Duration
use msrobot.core.common#Timestamp
use msrobot.core.geometry#Pose
use msrobot.core.geometry#Position3D
use msrobot.domain.gcode#GCodeCommand

/// Sample status
enum SampleStatus {
    /// Sample pending execution
    PENDING

    /// Sample in progress
    IN_PROGRESS

    /// Sample completed successfully
    SAMPLED

    /// Sample skipped
    SKIPPED

    /// Sample ended with error
    ERROR
}

/// Contact detection method
enum ContactMethod {
    /// Fixed Z height contact
    CONSTANT_Z

    /// Conductance-based contact detection
    CONDUCTANCE

    /// Force sensing contact (future)
    FORCE_SENSING
}

/// Conductance reading
structure ConductanceReading {
    /// Conductance value in μS
    @required
    value: Integer

    /// Reading timestamp
    @required
    timestamp: Timestamp
}

/// Contact information
structure ContactInfo {
    /// Whether contact was detected
    @required
    contactDetected: Boolean

    /// Contact timestamp
    @required
    contactTimestamp: Timestamp

    /// Z height at start of approach
    @required
    approachStartZ: Float

    /// Z height at contact
    @required
    contactZ: Float

    /// Number of probe steps to contact
    @required
    probeSteps: Integer

    /// Contact detection method
    @required
    contactMethod: ContactMethod
}

/// List of G-code commands
list GCodeCommandList {
    member: GCodeCommand
}

/// Sample entity
structure Sample {
    /// Sequential index in recording
    @required
    index: Integer

    /// Absolute timestamp of contact
    @required
    timestamp: Timestamp

    /// Elapsed time since recording start
    @required
    elapsed: Duration

    /// Full 6DOF pose at contact
    @required
    pose: Pose

    /// Planned target position
    @required
    targetPosition: Position3D

    /// Contact information
    @required
    contact: ContactInfo

    /// Conductance reading if applicable
    conductance: ConductanceReading

    /// G-code commands executed for this sample
    @required
    gcodeCommands: GCodeCommandList

    /// Sample status
    @required
    status: SampleStatus

    /// Error message if status is ERROR
    errorMessage: String
}

/// List of samples
list SampleList {
    member: Sample
}

/// Sample data for export
structure SampleExport {
    /// Sample index
    @required
    index: Integer

    /// Timestamp ISO string
    @required
    timestamp: String

    /// Elapsed milliseconds
    @required
    elapsedMs: Long

    /// Position X
    @required
    posX: Float

    /// Position Y
    @required
    posY: Float

    /// Position Z (contact height)
    @required
    posZ: Float

    /// Quaternion W
    @required
    quatW: Float

    /// Quaternion X
    @required
    quatX: Float

    /// Quaternion Y
    @required
    quatY: Float

    /// Quaternion Z
    @required
    quatZ: Float

    /// Conductance value (-1 if N/A)
    @required
    conductance: Integer

    /// Status string
    @required
    status: String
}

/// List of sample exports
list SampleExportList {
    member: SampleExport
}
