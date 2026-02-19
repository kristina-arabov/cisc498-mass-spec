$version: "2.0"

namespace msrobot.app

use msrobot.services.calibration#CancelCalibration
use msrobot.services.calibration#DeleteCalibration
use msrobot.services.calibration#GetCalibrationStatus
use msrobot.services.calibration#GetLatestCalibration
use msrobot.services.calibration#ListCalibrations
use msrobot.services.calibration#LoadCalibration
use msrobot.services.calibration#RunCalibration
use msrobot.services.calibration#SaveCalibration
use msrobot.services.calibration#TransformBatchPixelsToStage
use msrobot.services.calibration#TransformPixelToStage
use msrobot.services.calibration#TransformStageToPixel
use msrobot.services.calibration#ValidateCalibration
use msrobot.services.device#CaptureFrame
use msrobot.services.device#ConnectCamera
use msrobot.services.device#ConnectConductanceMeter
use msrobot.services.device#ConnectLights
use msrobot.services.device#ConnectPrinter
use msrobot.services.device#DisconnectCamera
use msrobot.services.device#DisconnectConductanceMeter
use msrobot.services.device#DisconnectLights
use msrobot.services.device#DisconnectPrinter
use msrobot.services.device#EmergencyStop
use msrobot.services.device#ExecuteGCode
use msrobot.services.device#GetCameraState
use msrobot.services.device#GetConductanceState
use msrobot.services.device#GetDevicesStatus
use msrobot.services.device#GetPrinterState
use msrobot.services.device#HomePrinter
use msrobot.services.device#ListCameras
use msrobot.services.device#ListSerialPorts
use msrobot.services.device#MoveRelative
use msrobot.services.device#MoveTo
use msrobot.services.device#ReadConductance
use msrobot.services.device#SetCameraExposure
use msrobot.services.device#SetConductanceThreshold
use msrobot.services.device#StartPreview
use msrobot.services.device#StopPreview
use msrobot.services.recording#AbortRecording
use msrobot.services.recording#CancelExport
use msrobot.services.recording#ConfigureRecording
use msrobot.services.recording#CreateRecording
use msrobot.services.recording#DeleteRecording
use msrobot.services.recording#ExportRecording
use msrobot.services.recording#GeneratePath
use msrobot.services.recording#GetExportProgress
use msrobot.services.recording#GetRecordingState
use msrobot.services.recording#GetRecordingStatistics
use msrobot.services.recording#ListRecordings
use msrobot.services.recording#LoadRecording
use msrobot.services.recording#PauseRecording
use msrobot.services.recording#PreviewPath
use msrobot.services.recording#ReadSamples
use msrobot.services.recording#ResumeRecording
use msrobot.services.recording#SetROI
use msrobot.services.recording#StartRecording
use msrobot.services.session#CloseSession
use msrobot.services.session#CreateSession
use msrobot.services.session#DeleteSession
use msrobot.services.session#GetCurrentSession
use msrobot.services.session#GetSessionDirectory
use msrobot.services.session#ListSessions
use msrobot.services.session#LoadSession
use msrobot.services.session#SaveSession
use msrobot.services.session#SetSessionCalibration

/// MS-Robot Application API
///
/// This is the unified API for the MS-Robot mass spectrometry desktop application.
/// The API provides functionality for:
///
/// **Session Management**
/// - Create, load, save, and close work sessions
/// - Associate calibrations with sessions
///
/// **Calibration**
/// - Run automated camera and hand-eye calibration
/// - Transform coordinates between pixel and stage space
/// - Validate calibration accuracy
///
/// **Recording**
/// - Configure and execute sample recordings
/// - Define regions of interest (ROI) and generate sampling paths
/// - Export recorded data to various formats
///
/// **Device Control**
/// - Connect and manage hardware devices (printer, camera, conductance meter)
/// - Control printer movement and execute G-code
/// - Capture camera frames and read conductance values
@title("MS-Robot API")
service AppService {
    version: "2.0.0"
    resources: [
        SessionResource
        CalibrationResource
        RecordingResource
        DeviceResource
    ]
}

/// Session Management
///
/// Sessions are the top-level workspace concept in MS-Robot. A session represents
/// a single work session that contains recordings, calibration references, and
/// all associated metadata.
///
/// **Key Operations:**
/// - Create new sessions with automatic timestamped naming
/// - Load existing sessions from disk
/// - Save session state to persist changes
/// - Associate calibrations with sessions
resource SessionResource {
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

/// Calibration Management
///
/// The calibration system handles camera intrinsic calibration and hand-eye
/// (camera-to-stage) calibration. Calibrations enable accurate transformation
/// between pixel coordinates (camera space) and stage coordinates (physical space).
///
/// **Key Operations:**
/// - Run automated calibration using checkerboard patterns
/// - Transform coordinates between pixel and stage space
/// - Validate calibration accuracy
/// - Manage calibration files
resource CalibrationResource {
    operations: [
        RunCalibration
        CancelCalibration
        LoadCalibration
        SaveCalibration
        DeleteCalibration
        GetLatestCalibration
        ListCalibrations
        ValidateCalibration
        GetCalibrationStatus
        TransformPixelToStage
        TransformStageToPixel
        TransformBatchPixelsToStage
    ]
}

/// Recording Management
///
/// Recordings capture mass spectrometry data by sampling conductance values
/// along defined paths within regions of interest (ROI). The recording system
/// handles path generation, sample collection, and data export.
///
/// **Key Operations:**
/// - Create and configure recordings with ROI and sampling parameters
/// - Generate sampling paths from ROI definitions
/// - Execute recordings with real-time progress tracking
/// - Export data to various formats (CSV, TXT, imzML)
resource RecordingResource {
    operations: [
        CreateRecording
        LoadRecording
        DeleteRecording
        ConfigureRecording
        SetROI
        GeneratePath
        PreviewPath
        StartRecording
        PauseRecording
        ResumeRecording
        AbortRecording
        GetRecordingState
        GetRecordingStatistics
        ListRecordings
        ReadSamples
        ExportRecording
        GetExportProgress
        CancelExport
    ]
}

/// Device Control
///
/// The device system manages all hardware connections and operations including
/// the 3D printer (motion stage), camera, and conductance meter.
///
/// **Printer Operations:**
/// - Connect/disconnect, home axes, absolute/relative movement
/// - Execute raw G-code commands, emergency stop
///
/// **Camera Operations:**
/// - Connect/disconnect, start/stop preview, capture frames
/// - Configure exposure settings
///
/// **Conductance Meter Operations:**
/// - Connect/disconnect, read values, set thresholds
resource DeviceResource {
    operations: [
        ListSerialPorts
        ListCameras
        ConnectPrinter
        DisconnectPrinter
        ConnectCamera
        DisconnectCamera
        ConnectConductanceMeter
        DisconnectConductanceMeter
        ConnectLights
        DisconnectLights
        GetDevicesStatus
        HomePrinter
        MoveTo
        MoveRelative
        GetPrinterState
        ExecuteGCode
        EmergencyStop
        StartPreview
        StopPreview
        CaptureFrame
        GetCameraState
        SetCameraExposure
        ReadConductance
        GetConductanceState
        SetConductanceThreshold
    ]
}
