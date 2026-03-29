$version: "2.0"

namespace msrobot.services.recording

use msrobot.domain.export#ExportConfig
use msrobot.domain.export#ExportResult
use msrobot.domain.path#SamplingPath
use msrobot.domain.recording#RecordingConfig
use msrobot.domain.roi#ROI

/// Sampling workflow. Backed by SamplingItem singleton + Application.py global_poll().
@title("Recording Service")
service RecordingService {
    version: "2.0.0"
    operations: [
        ConfigureRecording
        SetROI
        GeneratePath
        StartRecording
        PauseRecording
        ResumeRecording
        AbortRecording
        ExportRecording
    ]
}

/// Set sampling parameters into SamplingItem (via p3_prerun_config.py).
operation ConfigureRecording {
    input: ConfigureRecordingInput
    output: ConfigureRecordingOutput
}

@input
structure ConfigureRecordingInput {
    @required
    config: RecordingConfig
}

@output
structure ConfigureRecordingOutput {
    @required
    success: Boolean
}

/// Set the ROI polygon (drawn in p2_roi_selection.py, stored in SamplingItem).
operation SetROI {
    input: SetROIInput
    output: SetROIOutput
}

@input
structure SetROIInput {
    @required
    roi: ROI
}

@output
structure SetROIOutput {
    @required
    success: Boolean
}

/// Generate the G-code path via sampling_service.getSampling().
operation GeneratePath {
    input: GeneratePathInput
    output: GeneratePathOutput
}

@input
structure GeneratePathInput {}

@output
structure GeneratePathOutput {
    @required
    path: SamplingPath
}

/// Begin sampling: global_poll() starts consuming SamplingItem.gcodes.
operation StartRecording {
    input: StartRecordingInput
    output: StartRecordingOutput
}

@input
structure StartRecordingInput {}

@output
structure StartRecordingOutput {
    @required
    success: Boolean
}

/// Sets SamplingItem.paused = True.
operation PauseRecording {
    input: PauseRecordingInput
    output: PauseRecordingOutput
}

@input
structure PauseRecordingInput {}

@output
structure PauseRecordingOutput {
    @required
    success: Boolean
}

/// Sets SamplingItem.paused = False.
operation ResumeRecording {
    input: ResumeRecordingInput
    output: ResumeRecordingOutput
}

@input
structure ResumeRecordingInput {}

@output
structure ResumeRecordingOutput {
    @required
    success: Boolean
}

/// Sets SamplingItem.moving = False; exits the sampling loop.
operation AbortRecording {
    input: AbortRecordingInput
    output: AbortRecordingOutput
}

@input
structure AbortRecordingInput {}

@output
structure AbortRecordingOutput {
    @required
    success: Boolean
}

/// Write SamplingItem.csv_rows to disk (QFileDialog in p5_sampling_complete.py).
operation ExportRecording {
    input: ExportRecordingInput
    output: ExportRecordingOutput
}

@input
structure ExportRecordingInput {
    @required
    config: ExportConfig
}

@output
structure ExportRecordingOutput {
    @required
    result: ExportResult
}
