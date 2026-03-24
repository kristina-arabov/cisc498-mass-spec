$version: "2.0"

namespace msrobot.domain.session

use msrobot.core.common#FilePath
use msrobot.core.common#Timestamp

string SessionId

/// Status of a session
enum SessionStatus {
    /// Session created, awaiting calibration selection
    CREATED

    /// Calibration required before proceeding
    CALIBRATION_REQUIRED

    /// Session ready for recording
    READY

    /// Recording in progress
    RECORDING

    /// Session closed
    CLOSED
}

/// Session aggregate root
structure Session {
    /// Unique session identifier
    @required
    id: SessionId

    /// User-provided session name suffix
    @required
    name: String

    /// Full session name with timestamp prefix
    @required
    fullName: String

    /// Session creation timestamp
    @required
    createdAt: Timestamp

    /// Last modification timestamp
    @required
    modifiedAt: Timestamp

    /// Current session status
    @required
    status: SessionStatus

    /// Reference to calibration (optional until set)
    calibrationId: String

    /// Path to calibration file
    calibrationPath: FilePath

    /// List of recording IDs in this session
    @required
    recordings: RecordingIdList

    /// Output directory path
    @required
    outputDirectory: FilePath
}

/// List of recording IDs
list RecordingIdList {
    member: String
}

/// Summary of a session for listing
structure SessionSummary {
    /// Session ID
    @required
    id: SessionId

    /// Full session name
    @required
    fullName: String

    /// Creation timestamp
    @required
    createdAt: Timestamp

    /// Session status
    @required
    status: SessionStatus

    /// Number of recordings
    @required
    recordingCount: Integer

    /// Path to session directory
    @required
    path: FilePath
}

/// List of session summaries
list SessionSummaryList {
    member: SessionSummary
}
