$version: "2.0"

namespace msrobot.core.common

/// Duration in milliseconds.
structure Duration {
    @required
    milliseconds: Long
}

/// ISO 8601 timestamp string.
string Timestamp

/// File path string.
string FilePath
