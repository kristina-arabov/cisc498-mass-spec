$version: "2.0"

namespace msrobot.domain.export

use msrobot.core.common#FilePath

/// Export format type
enum ExportFormat {
    /// Comma-separated values
    CSV

    /// Human-readable text
    TXT

    /// Excel workbook
    XLSX
}

/// Export configuration
structure ExportConfig {
    /// Export format
    @required
    format: ExportFormat

    /// Output file path
    @required
    outputPath: FilePath

    /// Include header row (for CSV)
    @required
    includeHeader: Boolean

    /// Include metadata sheet (for XLSX)
    @required
    includeMetadata: Boolean

    /// Include Z-heights grid sheet (for XLSX)
    @required
    includeZHeightsGrid: Boolean

    /// Decimal precision for float values
    @required
    decimalPrecision: Integer
}

/// Export result
structure ExportResult {
    /// Whether export succeeded
    @required
    success: Boolean

    /// Output file path
    @required
    outputPath: FilePath

    /// Number of samples exported
    @required
    samplesExported: Integer

    /// File size in bytes
    @required
    fileSizeBytes: Long

    /// Export duration in ms
    @required
    exportDurationMs: Integer

    /// Error message if failed
    errorMessage: String
}

/// Export progress
structure ExportProgress {
    /// Samples processed
    @required
    samplesProcessed: Integer

    /// Total samples
    @required
    totalSamples: Integer

    /// Progress percentage
    @required
    progressPercent: Float

    /// Current phase description
    @required
    currentPhase: String
}
