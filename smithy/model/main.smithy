$version: "2.0"

namespace msrobot.app

use msrobot.services.calibration#LoadCalibration
use msrobot.services.calibration#TransformPixelToStage

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
use msrobot.services.device#SetBrightness
use msrobot.services.device#SetConductanceThreshold
use msrobot.services.device#StartPreview
use msrobot.services.device#StopPreview

use msrobot.services.recording#AbortRecording
use msrobot.services.recording#ConfigureRecording
use msrobot.services.recording#ExportRecording
use msrobot.services.recording#GeneratePath
use msrobot.services.recording#PauseRecording
use msrobot.services.recording#ResumeRecording
use msrobot.services.recording#SetROI
use msrobot.services.recording#StartRecording

@title("MS-Robot API")
service AppService {
    version: "2.0.0"
    resources: [
        CalibrationResource
        RecordingResource
        DeviceResource
    ]
}

resource CalibrationResource {
    operations: [
        LoadCalibration
        TransformPixelToStage
    ]
}

resource RecordingResource {
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
        ReadConductance
        GetConductanceState
        SetConductanceThreshold
        SetBrightness
    ]
}
