$version: "2.0"

namespace msrobot.domain.export

use msrobot.core.common#FilePath

enum ExportFormat {
    CSV
}

/// CSV columns as written by sampling_service.createCSV() / addData().
/// Header: "Time (ms),Conductance,X,Y,Z"
enum CsvColumn {
    /// Milliseconds since recording start: int(round(time.time()*1000)) - startThr
    TIME_MS

    /// Conductance in μS; 0 if meter disconnected.
    CONDUCTANCE

    X
    Y
    Z
}

structure ExportConfig {
    @required
    format: ExportFormat

    /// Chosen via QFileDialog in p5_sampling_complete.py.
    @required
    outputPath: FilePath

    @required
    includeHeader: Boolean

    /// Decimal places for X, Y, Z columns.
    @required
    decimalPrecision: Integer
}

structure ExportResult {
    @required
    success: Boolean

    @required
    outputPath: FilePath

    /// Rows written, excluding the header. Equals len(SamplingItem.csv_rows).
    @required
    samplesExported: Integer

    errorMessage: String
}
