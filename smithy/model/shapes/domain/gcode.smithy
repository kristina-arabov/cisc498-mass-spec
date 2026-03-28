$version: "2.0"

namespace msrobot.domain.gcode

/// G-code command types used by the application.
enum GCodeType {
    /// G0 — rapid move (XY transit and Z retract)
    RAPID_MOVE

    /// G1 — linear move with feedrate (Z descent)
    LINEAR_MOVE

    /// G4 P<ms> — dwell; used for sampleTime at sample height and dwellTime at transit height
    DWELL

    /// G28 — home axes
    HOME

    /// G90 — absolute positioning mode
    SET_ABSOLUTE

    /// G91 — relative positioning mode (CONDUCTANCE step-down moves)
    SET_RELATIVE

    /// G92 — set current position (e.g. G92 Z0 after contact in CONDUCTANCE mode)
    SET_POSITION

    /// M114 — report position; parsed as "X<v> Y<v> Z<v>" from the Count line
    REPORT_POSITION

    /// M105 — report temperatures; pattern r"T:(\d*\.?\d*) B:(\d*\.?\d*)"
    REPORT_TEMPERATURE

    /// M104 S<temp> — set nozzle temperature
    SET_NOZZLE_TEMP

    /// M140 S<temp> — set bed temperature
    SET_BED_TEMP

    /// M400 — wait for buffered moves to complete
    WAIT_FOR_MOVES

    /// M203 X5000 Y5000 Z5000 — set maximum feedrate limits
    SET_MAX_FEEDRATE

    UNKNOWN
}

structure GCodeCommand {
    @required
    type: GCodeType

    @required
    rawCommand: String

    x: Float
    y: Float
    z: Float
    feedRate: Float

    /// P parameter (ms) for G4 dwell.
    dwellMs: Integer

    timestamp: String
}

list GCodeCommandList {
    member: GCodeCommand
}

structure GCodeResult {
    @required
    command: GCodeCommand

    /// True when firmware responds with "ok".
    @required
    success: Boolean

    response: String
    errorMessage: String

    /// Dispatch-to-acknowledgement time in ms.
    executionMs: Integer
}

/// Parsed M114 response. printer.py extracts X/Y/Z from the "Count" line.
structure PositionResponse {
    @required
    x: Float

    @required
    y: Float

    @required
    z: Float

    /// E axis — always 0, extruder not used.
    e: Float

    countX: Integer
    countY: Integer
    countZ: Integer
}

/// Parsed M105 response. Pattern: r"T:(\d*\.?\d*) B:(\d*\.?\d*)"
structure TemperatureResponse {
    @required
    nozzle: Float

    @required
    nozzleTarget: Float

    @required
    bed: Float

    @required
    bedTarget: Float
}
