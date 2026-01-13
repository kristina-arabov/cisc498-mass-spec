$version: "2.0"

namespace msrobot.core.common

/// Duration in milliseconds
structure Duration {
    /// Milliseconds
    @required
    milliseconds: Long
}

/// Timestamp as ISO 8601 string
string Timestamp

/// UUID string identifier
string UUID

/// File path string
string FilePath

/// Empty unit structure for void returns
structure Unit {}

/// Generic success response
structure SuccessResponse {
    /// Whether the operation succeeded
    @required
    success: Boolean

    /// Optional message
    message: String
}

/// Error information
structure ErrorInfo {
    /// Error code
    @required
    code: String

    /// Human-readable error message
    @required
    message: String

    /// Whether the error is recoverable
    @required
    recoverable: Boolean

    /// Additional details
    details: String
}
