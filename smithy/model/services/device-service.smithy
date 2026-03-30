$version: "2.0"

namespace msrobot.services.device

use msrobot.core.geometry#Position3D
use msrobot.domain.device#CameraDeviceInfo
use msrobot.domain.device#CameraState
use msrobot.domain.device#ConductanceMeterInfo
use msrobot.domain.device#ConductanceMeterState
use msrobot.domain.device#DeviceConnection
use msrobot.domain.device#DevicesStatus
use msrobot.domain.device#LightsState
use msrobot.domain.device#PrinterInfo
use msrobot.domain.device#PrinterState
use msrobot.domain.gcode#GCodeCommand
use msrobot.domain.gcode#GCodeResult
use msrobot.domain.sample#ConductanceReading

@title("Device Service")
service DeviceService {
    version: "2.0.0"
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

operation ListSerialPorts {
    input: ListSerialPortsInput
    output: ListSerialPortsOutput
}

@input
structure ListSerialPortsInput {}

@output
structure ListSerialPortsOutput {
    @required
    ports: SerialPortList
}

list SerialPortList {
    member: SerialPortInfo
}

structure SerialPortInfo {
    @required
    port: String

    description: String
    hardwareId: String

    @required
    inUse: Boolean
}

operation ListCameras {
    input: ListCamerasInput
    output: ListCamerasOutput
}

@input
structure ListCamerasInput {}

@output
structure ListCamerasOutput {
    @required
    cameras: CameraInfoList
}

list CameraInfoList {
    member: AvailableCameraInfo
}

structure AvailableCameraInfo {
    @required
    deviceIndex: Integer

    name: String

    @required
    inUse: Boolean
}

operation ConnectPrinter {
    input: ConnectPrinterInput
    output: ConnectPrinterOutput
}

@input
structure ConnectPrinterInput {
    @required
    printerInfo: PrinterInfo
}

@output
structure ConnectPrinterOutput {
    @required
    connection: DeviceConnection
}

operation DisconnectPrinter {
    input: DisconnectPrinterInput
    output: DisconnectPrinterOutput
}

@input
structure DisconnectPrinterInput {}

@output
structure DisconnectPrinterOutput {
    @required
    success: Boolean
}

/// Backends tried in order: CAP_DSHOW → CAP_MSMF → CAP_ANY. 5 warmup frames discarded.
operation ConnectCamera {
    input: ConnectCameraInput
    output: ConnectCameraOutput
}

@input
structure ConnectCameraInput {
    @required
    cameraInfo: CameraDeviceInfo
}

@output
structure ConnectCameraOutput {
    @required
    connection: DeviceConnection
}

operation DisconnectCamera {
    input: DisconnectCameraInput
    output: DisconnectCameraOutput
}

@input
structure DisconnectCameraInput {}

@output
structure DisconnectCameraOutput {
    @required
    success: Boolean
}

/// checktype() sends 't\r\n', expects 'c\r\n' before marking live.
operation ConnectConductanceMeter {
    input: ConnectConductanceMeterInput
    output: ConnectConductanceMeterOutput
}

@input
structure ConnectConductanceMeterInput {
    @required
    conductanceMeterInfo: ConductanceMeterInfo
}

@output
structure ConnectConductanceMeterOutput {
    @required
    connection: DeviceConnection
}

operation DisconnectConductanceMeter {
    input: DisconnectConductanceMeterInput
    output: DisconnectConductanceMeterOutput
}

@input
structure DisconnectConductanceMeterInput {}

@output
structure DisconnectConductanceMeterOutput {
    @required
    success: Boolean
}

/// baudRate must be 9600 (hardcoded in LightingThread).
operation ConnectLights {
    input: ConnectLightsInput
    output: ConnectLightsOutput
}

@input
structure ConnectLightsInput {
    @required
    port: String

    @required
    baudRate: Integer
}

@output
structure ConnectLightsOutput {
    @required
    connection: DeviceConnection
}

operation DisconnectLights {
    input: DisconnectLightsInput
    output: DisconnectLightsOutput
}

@input
structure DisconnectLightsInput {}

@output
structure DisconnectLightsOutput {
    @required
    success: Boolean
}

operation GetDevicesStatus {
    input: GetDevicesStatusInput
    output: GetDevicesStatusOutput
}

@input
structure GetDevicesStatusInput {}

@output
structure GetDevicesStatusOutput {
    @required
    status: DevicesStatus
}

/// Sends G28. Homes all three axes at session start.
operation HomePrinter {
    input: HomePrinterInput
    output: HomePrinterOutput
}

@input
structure HomePrinterInput {
    @required
    homeX: Boolean

    @required
    homeY: Boolean

    @required
    homeZ: Boolean
}

@output
structure HomePrinterOutput {
    @required
    success: Boolean

    @required
    state: PrinterState
}

/// Sends G90 then G0 X Y Z F<speed>. Position confirmed via M114.
operation MoveTo {
    input: MoveToInput
    output: MoveToOutput
}

@input
structure MoveToInput {
    @required
    position: Position3D

    /// mm/min
    @required
    speed: Float

    @required
    waitForCompletion: Boolean
}

@output
structure MoveToOutput {
    @required
    success: Boolean

    @required
    state: PrinterState
}

/// Sends G91 then G0 X Y Z F<speed>, restores G90.
operation MoveRelative {
    input: MoveRelativeInput
    output: MoveRelativeOutput
}

@input
structure MoveRelativeInput {
    @required
    offset: Position3D

    /// mm/min
    @required
    speed: Float

    @required
    waitForCompletion: Boolean
}

@output
structure MoveRelativeOutput {
    @required
    success: Boolean

    @required
    state: PrinterState
}

/// Issues M114 and parses the response.
operation GetPrinterState {
    input: GetPrinterStateInput
    output: GetPrinterStateOutput
}

@input
structure GetPrinterStateInput {}

@output
structure GetPrinterStateOutput {
    @required
    state: PrinterState
}

operation ExecuteGCode {
    input: ExecuteGCodeInput
    output: ExecuteGCodeOutput
}

@input
structure ExecuteGCodeInput {
    @required
    command: GCodeCommand
}

@output
structure ExecuteGCodeOutput {
    @required
    result: GCodeResult
}

operation EmergencyStop {
    input: EmergencyStopInput
    output: EmergencyStopOutput
}

@input
structure EmergencyStopInput {}

@output
structure EmergencyStopOutput {
    @required
    success: Boolean
}

operation StartPreview {
    input: StartPreviewInput
    output: StartPreviewOutput
}

@input
structure StartPreviewInput {}

@output
structure StartPreviewOutput {
    @required
    success: Boolean

    @required
    state: CameraState
}

operation StopPreview {
    input: StopPreviewInput
    output: StopPreviewOutput
}

@input
structure StopPreviewInput {}

@output
structure StopPreviewOutput {
    @required
    success: Boolean
}

/// applyCorrection=true undistorts via fisheyeUnwarp + secondUnwarp (calibration_service.py).
operation CaptureFrame {
    input: CaptureFrameInput
    output: CaptureFrameOutput
}

@input
structure CaptureFrameInput {
    @required
    applyCorrection: Boolean

    savePath: String
}

@output
structure CaptureFrameOutput {
    @required
    success: Boolean

    /// Base64-encoded JPEG if savePath was not provided.
    imageData: String

    savedPath: String

    @required
    width: Integer

    @required
    height: Integer
}

operation GetCameraState {
    input: GetCameraStateInput
    output: GetCameraStateOutput
}

@input
structure GetCameraStateInput {}

@output
structure GetCameraStateOutput {
    @required
    state: CameraState
}

/// Dequeues the most recent [timestamp_ms, value_uS] pair from ConThread. Returns 0 if empty.
operation ReadConductance {
    input: ReadConductanceInput
    output: ReadConductanceOutput
}

@input
structure ReadConductanceInput {}

@output
structure ReadConductanceOutput {
    @required
    reading: ConductanceReading
}

operation GetConductanceState {
    input: GetConductanceStateInput
    output: GetConductanceStateOutput
}

@input
structure GetConductanceStateInput {}

@output
structure GetConductanceStateOutput {
    @required
    state: ConductanceMeterState
}

/// Stored in printer.con_threshold.
operation SetConductanceThreshold {
    input: SetConductanceThresholdInput
    output: SetConductanceThresholdOutput
}

@input
structure SetConductanceThresholdInput {
    @required
    lowerThreshold: Integer

    @required
    upperThreshold: Integer
}

@output
structure SetConductanceThresholdOutput {
    @required
    success: Boolean
}

/// Maps 0–100% to 0–255 PWM via device_service.set_brightness().
operation SetBrightness {
    input: SetBrightnessInput
    output: SetBrightnessOutput
}

@input
structure SetBrightnessInput {
    /// 0 = off, 100 = maximum.
    @required
    brightnessPercent: Integer
}

@output
structure SetBrightnessOutput {
    @required
    success: Boolean

    @required
    lightsState: LightsState
}
