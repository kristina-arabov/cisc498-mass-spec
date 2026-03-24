$version: "2.0"

namespace msrobot.services.device

use msrobot.core.geometry#Position3D
use msrobot.domain.device#CameraDeviceInfo
use msrobot.domain.device#CameraState
use msrobot.domain.device#ConductanceMeterInfo
use msrobot.domain.device#ConductanceMeterState
use msrobot.domain.device#DeviceConnection
use msrobot.domain.device#DevicesStatus
use msrobot.domain.device#PrinterInfo
use msrobot.domain.device#PrinterState
use msrobot.domain.gcode#GCodeCommand
use msrobot.domain.gcode#GCodeResult
use msrobot.domain.sample#ConductanceReading

/// Service for managing hardware devices (singleton)
@title("Device Service")
service DeviceService {
    version: "2.0.0"
    operations: [
        // Discovery
        ListSerialPorts
        ListCameras
        // Connection management
        ConnectPrinter
        DisconnectPrinter

        ConnectCamera
        DisconnectCamera

        ConnectConductanceMeter
        DisconnectConductanceMeter

        ConnectLights
        DisconnectLights

        GetDevicesStatus
        // Printer operations
        HomePrinter
        MoveTo
        MoveRelative
        GetPrinterState
        ExecuteGCode
        EmergencyStop
        // Camera operations
        StartPreview
        StopPreview
        CaptureFrame
        GetCameraState
        SetCameraExposure
        // Conductance operations
        ReadConductance
        GetConductanceState
        SetConductanceThreshold
    ]
}

// ============================================================================
// Discovery Operations
// ============================================================================
/// List available serial ports
operation ListSerialPorts {
    input: ListSerialPortsInput
    output: ListSerialPortsOutput
}

@input
structure ListSerialPortsInput {}

@output
structure ListSerialPortsOutput {
    /// Available serial ports
    @required
    ports: SerialPortList
}

list SerialPortList {
    member: SerialPortInfo
}

structure SerialPortInfo {
    /// Port name (e.g., COM3, /dev/ttyUSB0)
    @required
    port: String

    /// Device description
    description: String

    /// Hardware ID
    hardwareId: String

    /// Whether port is currently in use
    @required
    inUse: Boolean
}

/// List available cameras
operation ListCameras {
    input: ListCamerasInput
    output: ListCamerasOutput
}

@input
structure ListCamerasInput {}

@output
structure ListCamerasOutput {
    /// Available cameras
    @required
    cameras: CameraInfoList
}

list CameraInfoList {
    member: AvailableCameraInfo
}

structure AvailableCameraInfo {
    /// Device index
    @required
    deviceIndex: Integer

    /// Camera name
    name: String

    /// Whether camera is currently in use
    @required
    inUse: Boolean
}

// ============================================================================
// Connection Operations
// ============================================================================
/// Connect to printer
operation ConnectPrinter {
    input: ConnectPrinterInput
    output: ConnectPrinterOutput
}

@input
structure ConnectPrinterInput {
    /// Printer info
    @required
    printerInfo: PrinterInfo
}

@output
structure ConnectPrinterOutput {
    /// Connection result
    @required
    connection: DeviceConnection
}

/// Disconnect printer
operation DisconnectPrinter {
    input: DisconnectPrinterInput
    output: DisconnectPrinterOutput
}

@input
structure DisconnectPrinterInput {}

@output
structure DisconnectPrinterOutput {
    /// Success
    @required
    success: Boolean
}

/// Connect to camera
operation ConnectCamera {
    input: ConnectCameraInput
    output: ConnectCameraOutput
}

@input
structure ConnectCameraInput {
    /// Camera info
    @required
    cameraInfo: CameraDeviceInfo
}

@output
structure ConnectCameraOutput {
    /// Connection result
    @required
    connection: DeviceConnection
}

/// Disconnect camera
operation DisconnectCamera {
    input: DisconnectCameraInput
    output: DisconnectCameraOutput
}

@input
structure DisconnectCameraInput {}

@output
structure DisconnectCameraOutput {
    /// Success
    @required
    success: Boolean
}

/// Connect to conductance meter
operation ConnectConductanceMeter {
    input: ConnectConductanceMeterInput
    output: ConnectConductanceMeterOutput
}

@input
structure ConnectConductanceMeterInput {
    /// Conductance meter info
    @required
    conductanceMeterInfo: ConductanceMeterInfo
}

@output
structure ConnectConductanceMeterOutput {
    /// Connection result
    @required
    connection: DeviceConnection
}

/// Disconnect conductance meter
operation DisconnectConductanceMeter {
    input: DisconnectConductanceMeterInput
    output: DisconnectConductanceMeterOutput
}

@input
structure DisconnectConductanceMeterInput {}

@output
structure DisconnectConductanceMeterOutput {
    /// Success
    @required
    success: Boolean
}

/// Connect to light controller
operation ConnectLights {
    input: ConnectLightsInput
    output: ConnectLightsOutput
}

@input
structure ConnectLightsInput {}

@output
structure ConnectLightsOutput {
    /// Connection result
    @required
    connection: DeviceConnection
}

/// Disconnect light controller
operation DisconnectLights {
    input: DisconnectLightsInput
    output: DisconnectLightsOutput
}

@input
structure DisconnectLightsInput {}

@output
structure DisconnectLightsOutput {
    /// Success
    @required
    success: Boolean
}



/// Get status of all devices
operation GetDevicesStatus {
    input: GetDevicesStatusInput
    output: GetDevicesStatusOutput
}

@input
structure GetDevicesStatusInput {}

@output
structure GetDevicesStatusOutput {
    /// Devices status
    @required
    status: DevicesStatus
}

// ============================================================================
// Printer Operations
// ============================================================================
/// Home printer axes
operation HomePrinter {
    input: HomePrinterInput
    output: HomePrinterOutput
}

@input
structure HomePrinterInput {
    /// Home X axis
    @required
    homeX: Boolean

    /// Home Y axis
    @required
    homeY: Boolean

    /// Home Z axis
    @required
    homeZ: Boolean
}

@output
structure HomePrinterOutput {
    /// Success
    @required
    success: Boolean

    /// Printer state after homing
    @required
    state: PrinterState
}

/// Move to absolute position
operation MoveTo {
    input: MoveToInput
    output: MoveToOutput
}

@input
structure MoveToInput {
    /// Target position
    @required
    position: Position3D

    /// Speed in mm/min
    @required
    speed: Float

    /// Wait for move to complete
    @required
    waitForCompletion: Boolean
}

@output
structure MoveToOutput {
    /// Success
    @required
    success: Boolean

    /// Printer state after move
    @required
    state: PrinterState
}

/// Move relative to current position
operation MoveRelative {
    input: MoveRelativeInput
    output: MoveRelativeOutput
}

@input
structure MoveRelativeInput {
    /// Relative offset
    @required
    offset: Position3D

    /// Speed in mm/min
    @required
    speed: Float

    /// Wait for move to complete
    @required
    waitForCompletion: Boolean
}

@output
structure MoveRelativeOutput {
    /// Success
    @required
    success: Boolean

    /// Printer state after move
    @required
    state: PrinterState
}

/// Get current printer state
operation GetPrinterState {
    input: GetPrinterStateInput
    output: GetPrinterStateOutput
}

@input
structure GetPrinterStateInput {}

@output
structure GetPrinterStateOutput {
    /// Printer state
    @required
    state: PrinterState
}

/// Execute raw G-code command
operation ExecuteGCode {
    input: ExecuteGCodeInput
    output: ExecuteGCodeOutput
}

@input
structure ExecuteGCodeInput {
    /// G-code command
    @required
    command: GCodeCommand
}

@output
structure ExecuteGCodeOutput {
    /// Execution result
    @required
    result: GCodeResult
}

/// Emergency stop
operation EmergencyStop {
    input: EmergencyStopInput
    output: EmergencyStopOutput
}

@input
structure EmergencyStopInput {}

@output
structure EmergencyStopOutput {
    /// Success
    @required
    success: Boolean
}

// ============================================================================
// Camera Operations
// ============================================================================
/// Start camera preview
operation StartPreview {
    input: StartPreviewInput
    output: StartPreviewOutput
}

@input
structure StartPreviewInput {}

@output
structure StartPreviewOutput {
    /// Success
    @required
    success: Boolean

    /// Camera state
    @required
    state: CameraState
}

/// Stop camera preview
operation StopPreview {
    input: StopPreviewInput
    output: StopPreviewOutput
}

@input
structure StopPreviewInput {}

@output
structure StopPreviewOutput {
    /// Success
    @required
    success: Boolean
}

/// Capture single frame
operation CaptureFrame {
    input: CaptureFrameInput
    output: CaptureFrameOutput
}

@input
structure CaptureFrameInput {
    /// Apply distortion correction
    @required
    applyCorrection: Boolean

    /// Optional path to save image
    savePath: String
}

@output
structure CaptureFrameOutput {
    /// Success
    @required
    success: Boolean

    /// Base64 encoded image data (if not saved to file)
    imageData: String

    /// Saved file path (if saved to file)
    savedPath: String

    /// Image width
    @required
    width: Integer

    /// Image height
    @required
    height: Integer
}

/// Get camera state
operation GetCameraState {
    input: GetCameraStateInput
    output: GetCameraStateOutput
}

@input
structure GetCameraStateInput {}

@output
structure GetCameraStateOutput {
    /// Camera state
    @required
    state: CameraState
}

// ============================================================================
// Conductance Operations
// ============================================================================
/// Read current conductance value
operation ReadConductance {
    input: ReadConductanceInput
    output: ReadConductanceOutput
}

@input
structure ReadConductanceInput {}

@output
structure ReadConductanceOutput {
    /// Conductance reading
    @required
    reading: ConductanceReading
}

/// Get conductance meter state
operation GetConductanceState {
    input: GetConductanceStateInput
    output: GetConductanceStateOutput
}

@input
structure GetConductanceStateInput {}

@output
structure GetConductanceStateOutput {
    /// Conductance state
    @required
    state: ConductanceMeterState
}

/// Set conductance threshold for contact detection
operation SetConductanceThreshold {
    input: SetConductanceThresholdInput
    output: SetConductanceThresholdOutput
}

@input
structure SetConductanceThresholdInput {
    /// Lower threshold value
    @required
    lowerThreshold: Integer

    /// Upper threshold value
    @required
    upperThreshold: Integer
}

@output
structure SetConductanceThresholdOutput {
    /// Success
    @required
    success: Boolean
}

/// Set camera exposure settings
operation SetCameraExposure {
    input: SetCameraExposureInput
    output: SetCameraExposureOutput
}

@input
structure SetCameraExposureInput {
    /// Auto exposure enabled
    @required
    autoExposure: Boolean

    /// Manual exposure value (if autoExposure is false)
    exposureValue: Integer

    /// Brightness adjustment
    brightness: Integer

    /// Contrast adjustment
    contrast: Integer
}

@output
structure SetCameraExposureOutput {
    /// Success
    @required
    success: Boolean

    /// Updated camera state
    @required
    state: CameraState
}
