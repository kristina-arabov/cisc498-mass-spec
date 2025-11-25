$version: "2.0"

namespace msrobot.services.recording

use msrobot.domain.export#ExportConfig
use msrobot.domain.export#ExportProgress
use msrobot.domain.export#ExportResult
use msrobot.domain.path#PathPreview
use msrobot.domain.path#SamplingPath
use msrobot.domain.recording#Recording
use msrobot.domain.recording#RecordingConfig
use msrobot.domain.recording#RecordingId
use msrobot.domain.recording#RecordingStatistics
use msrobot.domain.recording#RecordingSummaryList
use msrobot.domain.roi#ROI
use msrobot.domain.sample#SampleList
use msrobot.domain.session#SessionId

/// Service for managing recordings (singleton repository)
@title("Recording Service")
service RecordingService {
    version: "2.0.0"
    operations: [
        // Lifecycle
        CreateRecording
        LoadRecording
        DeleteRecording
        ConfigureRecording
        // ROI and Path
        SetROI
        GeneratePath
        PreviewPath
        // Execution
        StartRecording
        PauseRecording
        ResumeRecording
        AbortRecording
        // Status and Data
        GetRecordingState
        GetRecordingStatistics
        ListRecordings
        ReadSamples
        // Export
        ExportRecording
        GetExportProgress
        CancelExport
    ]
}

/// Create a new recording in a session
operation CreateRecording {
    input: CreateRecordingInput
    output: CreateRecordingOutput
}

@input
structure CreateRecordingInput {
    /// Session ID
    @required
    sessionId: SessionId

    /// Recording name (optional, auto-generated if not provided)
    name: String
}

@output
structure CreateRecordingOutput {
    /// Created recording
    @required
    recording: Recording
}

/// Configure recording parameters
operation ConfigureRecording {
    input: ConfigureRecordingInput
    output: ConfigureRecordingOutput
}

@input
structure ConfigureRecordingInput {
    /// Recording ID
    @required
    recordingId: RecordingId

    /// Recording configuration
    @required
    config: RecordingConfig
}

@output
structure ConfigureRecordingOutput {
    /// Updated recording
    @required
    recording: Recording
}

/// Set ROI for recording
operation SetROI {
    input: SetROIInput
    output: SetROIOutput
}

@input
structure SetROIInput {
    /// Recording ID
    @required
    recordingId: RecordingId

    /// Region of interest
    @required
    roi: ROI
}

@output
structure SetROIOutput {
    /// Updated recording
    @required
    recording: Recording
}

/// Generate sampling path from ROI and config
operation GeneratePath {
    input: GeneratePathInput
    output: GeneratePathOutput
}

@input
structure GeneratePathInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure GeneratePathOutput {
    /// Generated path
    @required
    path: SamplingPath

    /// Updated recording
    @required
    recording: Recording
}

/// Preview path without generating full path
operation PreviewPath {
    input: PreviewPathInput
    output: PreviewPathOutput
}

@input
structure PreviewPathInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure PreviewPathOutput {
    /// Path preview
    @required
    preview: PathPreview
}

/// Start recording execution
operation StartRecording {
    input: StartRecordingInput
    output: StartRecordingOutput
}

@input
structure StartRecordingInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure StartRecordingOutput {
    /// Updated recording
    @required
    recording: Recording
}

/// Pause recording
operation PauseRecording {
    input: PauseRecordingInput
    output: PauseRecordingOutput
}

@input
structure PauseRecordingInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure PauseRecordingOutput {
    /// Updated recording
    @required
    recording: Recording
}

/// Resume paused recording
operation ResumeRecording {
    input: ResumeRecordingInput
    output: ResumeRecordingOutput
}

@input
structure ResumeRecordingInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure ResumeRecordingOutput {
    /// Updated recording
    @required
    recording: Recording
}

/// Abort recording
operation AbortRecording {
    input: AbortRecordingInput
    output: AbortRecordingOutput
}

@input
structure AbortRecordingInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure AbortRecordingOutput {
    /// Updated recording
    @required
    recording: Recording
}

/// Get current recording state
operation GetRecordingState {
    input: GetRecordingStateInput
    output: GetRecordingStateOutput
}

@input
structure GetRecordingStateInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure GetRecordingStateOutput {
    /// Recording state
    @required
    recording: Recording
}

/// Get recording statistics
operation GetRecordingStatistics {
    input: GetRecordingStatisticsInput
    output: GetRecordingStatisticsOutput
}

@input
structure GetRecordingStatisticsInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure GetRecordingStatisticsOutput {
    /// Recording statistics
    @required
    statistics: RecordingStatistics
}

/// List recordings in a session
operation ListRecordings {
    input: ListRecordingsInput
    output: ListRecordingsOutput
}

@input
structure ListRecordingsInput {
    /// Session ID
    @required
    sessionId: SessionId
}

@output
structure ListRecordingsOutput {
    /// Recording summaries
    @required
    recordings: RecordingSummaryList
}

/// Export recording to file
operation ExportRecording {
    input: ExportRecordingInput
    output: ExportRecordingOutput
}

@input
structure ExportRecordingInput {
    /// Recording ID
    @required
    recordingId: RecordingId

    /// Export configuration
    @required
    config: ExportConfig
}

@output
structure ExportRecordingOutput {
    /// Export result
    @required
    result: ExportResult
}

/// Get export progress
operation GetExportProgress {
    input: GetExportProgressInput
    output: GetExportProgressOutput
}

@input
structure GetExportProgressInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure GetExportProgressOutput {
    /// Export progress
    @required
    progress: ExportProgress
}

/// Read samples from recording (paginated)
operation ReadSamples {
    input: ReadSamplesInput
    output: ReadSamplesOutput
}

@input
structure ReadSamplesInput {
    /// Recording ID
    @required
    recordingId: RecordingId

    /// Start index
    @required
    startIndex: Integer

    /// Number of samples to read
    @required
    count: Integer
}

@output
structure ReadSamplesOutput {
    /// Samples
    @required
    samples: SampleList

    /// Total sample count in recording
    @required
    totalCount: Integer

    /// Whether there are more samples
    @required
    hasMore: Boolean
}

/// Load an existing recording from file
operation LoadRecording {
    input: LoadRecordingInput
    output: LoadRecordingOutput
}

@input
structure LoadRecordingInput {
    /// Recording ID or path to .msrbt file
    @required
    recordingId: String
}

@output
structure LoadRecordingOutput {
    /// Loaded recording
    @required
    recording: Recording
}

/// Delete a recording and its data file
operation DeleteRecording {
    input: DeleteRecordingInput
    output: DeleteRecordingOutput
}

@input
structure DeleteRecordingInput {
    /// Recording ID
    @required
    recordingId: RecordingId

    /// Also delete the .msrbt data file
    @required
    deleteDataFile: Boolean
}

@output
structure DeleteRecordingOutput {
    /// Success
    @required
    success: Boolean
}

/// Cancel an in-progress export
operation CancelExport {
    input: CancelExportInput
    output: CancelExportOutput
}

@input
structure CancelExportInput {
    /// Recording ID
    @required
    recordingId: RecordingId
}

@output
structure CancelExportOutput {
    /// Success
    @required
    success: Boolean
}
