$version: "2.0"

namespace msrobot.domain.device

use msrobot.core.common#Timestamp
use msrobot.core.geometry#Position3D
use msrobot.core.geometry#Resolution

enum DeviceType {
    PRINTER
    CAMERA
    CONDUCTANCE
    LIGHTS
}

enum ConnectionStatus {
    DISCONNECTED
    CONNECTING
    CONNECTED
    ERROR
}

structure DeviceConnection {
    @required
    deviceType: DeviceType

    /// COM port name, camera index, etc.
    @required
    connectionId: String

    @required
    status: ConnectionStatus

    lastError: String
    connectedAt: Timestamp
}

/// Marlin firmware over virtual COM port via pronsole_pipe.py.
structure PrinterInfo {
    /// e.g. COM3 on Windows, /dev/ttyUSB0 on Linux
    @required
    port: String

    /// Marlin default: 115200
    @required
    baudRate: Integer

    /// Default: 2000 ms
    @required
    timeoutMs: Integer

    model: String
    firmwareVersion: String
}

/// 3-axis Cartesian gantry — position only, no orientation.
/// Position tracked by parsing M114 "X<v> Y<v> Z<v>" from the Count line.
structure PrinterState {
    @required
    position: Position3D

    @required
    isHomed: Boolean

    @required
    isMoving: Boolean

    /// From M105; null if not available.
    temperatureNozzle: Float

    /// From M105; null if not available.
    temperatureBed: Float

    @required
    lastUpdate: Timestamp
}

/// Two resolution contexts: Unwarping App 1280×720, Printer Control App 500×219.
/// Backend order: CAP_DSHOW → CAP_MSMF → CAP_ANY. 5 warmup frames discarded on connect.
structure CameraDeviceInfo {
    @required
    deviceIndex: Integer

    @required
    resolution: Resolution

    /// 30 FPS in both contexts.
    @required
    fps: Integer

    name: String
}

structure CameraState {
    @required
    isStreaming: Boolean

    /// Video recording (camera.py context only).
    @required
    isRecording: Boolean

    currentFps: Float
    lastFrameAt: Timestamp
}

/// checktype() sends 't\r\n' and expects 'c\r\n' to confirm the meter.
structure ConductanceMeterInfo {
    @required
    port: String

    @required
    baudRate: Integer

    /// Default: 2000 ms
    @required
    timeoutMs: Integer
}

/// Readings queued as [timestamp_ms, value_uS] by ConThread, consumed by getConductance().
structure ConductanceMeterState {
    /// Most recent reading in μS.
    @required
    currentValue: Integer

    @required
    lastReadingAt: Timestamp

    readingsPerSecond: Float
}

/// Baud rate hardcoded to 9600 in LightingThread. Brightness mapped 0–100% → 0–255 PWM.
structure LightsState {
    /// PWM duty cycle: 0 = off, 255 = maximum.
    @required
    brightness: Integer

    @required
    isConnected: Boolean
}

/// Snapshot of all connected device states.
structure DevicesStatus {
    @required
    printer: DeviceConnection

    @required
    camera: DeviceConnection

    @required
    conductance: DeviceConnection

    @required
    lights: DeviceConnection

    printerState: PrinterState
    cameraState: CameraState
    conductanceState: ConductanceMeterState
    lightsState: LightsState
}
