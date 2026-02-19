$version: "2.0"

namespace msrobot.domain.device

use msrobot.core.common#Timestamp
use msrobot.core.geometry#Pose
use msrobot.core.geometry#Resolution

/// Device type enumeration
enum DeviceType {
    /// 3D printer / robotic arm
    PRINTER

    /// Camera
    CAMERA

    /// Conductance meter
    CONDUCTANCE

    /// Lights
    LIGHTS
}

/// Device connection status
enum ConnectionStatus {
    /// Not connected
    DISCONNECTED

    /// Connection in progress
    CONNECTING

    /// Successfully connected
    CONNECTED

    /// Connection error
    ERROR
}

/// Generic device connection info
structure DeviceConnection {
    /// Type of device
    @required
    deviceType: DeviceType

    /// Connection identifier (port, index, etc.)
    @required
    connectionId: String

    /// Current status
    @required
    status: ConnectionStatus

    /// Last error message if status is ERROR
    lastError: String

    /// Connection timestamp
    connectedAt: Timestamp
}

/// List of device connections
list DeviceConnectionList {
    member: DeviceConnection
}

/// Printer/Arm device information
structure PrinterInfo {
    /// COM port
    @required
    port: String

    /// Baud rate
    @required
    baudRate: Integer

    /// Connection timeout in ms
    @required
    timeoutMs: Integer

    /// Printer model if known
    model: String

    /// Firmware version if known
    firmwareVersion: String
}

/// Printer state
structure PrinterState {
    /// Current pose
    @required
    pose: Pose

    /// Is printer homed
    @required
    isHomed: Boolean

    /// Is printer currently moving
    @required
    isMoving: Boolean

    /// Nozzle temperature
    temperatureNozzle: Float

    /// Bed temperature
    temperatureBed: Float

    /// Last state update
    @required
    lastUpdate: Timestamp
}

/// Camera device information
structure CameraDeviceInfo {
    /// Device index
    @required
    deviceIndex: Integer

    /// Camera resolution
    @required
    resolution: Resolution

    /// Frames per second
    @required
    fps: Integer

    /// Camera name/description
    name: String
}

/// Camera state
structure CameraState {
    /// Is camera streaming
    @required
    isStreaming: Boolean

    /// Is recording video
    @required
    isRecording: Boolean

    /// Current FPS (actual)
    currentFps: Float

    /// Last frame timestamp
    lastFrameAt: Timestamp
}

/// Conductance meter device information
structure ConductanceMeterInfo {
    /// COM port
    @required
    port: String

    /// Baud rate
    @required
    baudRate: Integer

    /// Connection timeout in ms
    @required
    timeoutMs: Integer
}

/// Conductance meter state
structure ConductanceMeterState {
    /// Current conductance reading in μS
    @required
    currentValue: Integer

    /// Last reading timestamp
    @required
    lastReadingAt: Timestamp

    /// Readings per second
    readingsPerSecond: Float
}


/// Light controller state
structure LightState { }


/// All devices status
structure DevicesStatus {
    /// Printer connection
    @required
    printer: DeviceConnection

    /// Camera connection
    @required
    camera: DeviceConnection

    /// Conductance meter connection
    @required
    conductance: DeviceConnection

    /// Printer state (if connected)
    printerState: PrinterState

    /// Camera state (if connected)
    cameraState: CameraState

    /// Conductance state (if connected)
    conductanceState: ConductanceMeterState

    /// Lights state (if connected)
    lightsState: LightsState
}
