$version: "2.0"

namespace msrobot.services.session

use msrobot.core.common#FilePath
use msrobot.domain.session#Session
use msrobot.domain.session#SessionId
use msrobot.domain.session#SessionSummaryList

/// Service for managing sessions (singleton repository)
@title("Session Service")
service SessionService {
    version: "2.0.0"
    operations: [
        CreateSession
        LoadSession
        SaveSession
        CloseSession
        DeleteSession
        ListSessions
        GetCurrentSession
        SetSessionCalibration
        GetSessionDirectory
    ]
}

/// Create a new session
operation CreateSession {
    input: CreateSessionInput
    output: CreateSessionOutput
}

@input
structure CreateSessionInput {
    /// User-provided session name (will be prefixed with timestamp)
    @required
    name: String

    /// Output directory (optional, uses default if not provided)
    outputDirectory: FilePath
}

@output
structure CreateSessionOutput {
    /// Created session
    @required
    session: Session
}

/// Load an existing session
operation LoadSession {
    input: LoadSessionInput
    output: LoadSessionOutput
}

@input
structure LoadSessionInput {
    /// Session ID or path to session.json
    @required
    sessionId: String
}

@output
structure LoadSessionOutput {
    /// Loaded session
    @required
    session: Session
}

/// Save current session state
operation SaveSession {
    input: SaveSessionInput
    output: SaveSessionOutput
}

@input
structure SaveSessionInput {
    /// Session ID
    @required
    sessionId: SessionId
}

@output
structure SaveSessionOutput {
    /// Success response
    @required
    success: Boolean
}

/// Close a session
operation CloseSession {
    input: CloseSessionInput
    output: CloseSessionOutput
}

@input
structure CloseSessionInput {
    /// Session ID
    @required
    sessionId: SessionId
}

@output
structure CloseSessionOutput {
    /// Success response
    @required
    success: Boolean
}

/// List all sessions in output directory
operation ListSessions {
    input: ListSessionsInput
    output: ListSessionsOutput
}

@input
structure ListSessionsInput {
    /// Output directory to search (optional, uses default if not provided)
    outputDirectory: FilePath
}

@output
structure ListSessionsOutput {
    /// List of session summaries
    @required
    sessions: SessionSummaryList
}

/// Get the current active session
operation GetCurrentSession {
    input: GetCurrentSessionInput
    output: GetCurrentSessionOutput
}

@input
structure GetCurrentSessionInput {}

@output
structure GetCurrentSessionOutput {
    /// Current session (null if none active)
    session: Session
}

/// Set calibration for a session
operation SetSessionCalibration {
    input: SetSessionCalibrationInput
    output: SetSessionCalibrationOutput
}

@input
structure SetSessionCalibrationInput {
    /// Session ID
    @required
    sessionId: SessionId

    /// Path to calibration file
    @required
    calibrationPath: FilePath
}

@output
structure SetSessionCalibrationOutput {
    /// Success response
    @required
    success: Boolean

    /// Updated session
    @required
    session: Session
}

/// Delete a session and optionally its data
operation DeleteSession {
    input: DeleteSessionInput
    output: DeleteSessionOutput
}

@input
structure DeleteSessionInput {
    /// Session ID
    @required
    sessionId: SessionId

    /// Also delete all recording data files
    @required
    deleteRecordings: Boolean
}

@output
structure DeleteSessionOutput {
    /// Success
    @required
    success: Boolean
}

/// Get session output directory path
operation GetSessionDirectory {
    input: GetSessionDirectoryInput
    output: GetSessionDirectoryOutput
}

@input
structure GetSessionDirectoryInput {
    /// Session ID (uses current session if not provided)
    sessionId: SessionId
}

@output
structure GetSessionDirectoryOutput {
    /// Directory path
    @required
    directory: FilePath

    /// Whether directory exists
    @required
    exists: Boolean
}
