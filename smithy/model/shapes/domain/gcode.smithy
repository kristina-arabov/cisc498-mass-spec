$version: "2.0"

namespace msrobot.domain.gcode

/// G-code command type
enum GCodeType {
    /// G0 - Rapid move
    RAPID_MOVE

    /// G1 - Linear move
    LINEAR_MOVE

    /// G4 - Dwell
    DWELL

    /// G28 - Home
    HOME

    /// G90 - Absolute positioning
    SET_ABSOLUTE

    /// G91 - Relative positioning
    SET_RELATIVE

    /// G92 - Set position
    SET_POSITION

    /// M114 - Report position
    REPORT_POSITION

    /// M105 - Report temperature
    REPORT_TEMPERATURE

    /// M400 - Wait for moves
    WAIT_FOR_MOVES

    /// M203 - Set max feedrate
    SET_MAX_FEEDRATE

    /// Unknown command
    UNKNOWN
}

/// G-code command with parameters
structure GCodeCommand {
    /// Command type
    @required
    type: GCodeType

    /// Raw command string
    @required
    rawCommand: String

    /// X parameter (if applicable)
    x: Float

    /// Y parameter (if applicable)
    y: Float

    /// Z parameter (if applicable)
    z: Float

    /// Feed rate (if applicable)
    feedRate: Float

    /// Dwell time in ms (if applicable)
    dwellMs: Integer

    /// Command timestamp
    timestamp: String
}

/// List of G-code commands
list GCodeCommandList {
    member: GCodeCommand
}

/// G-code execution result
structure GCodeResult {
    /// Original command
    @required
    command: GCodeCommand

    /// Whether command succeeded
    @required
    success: Boolean

    /// Response from printer
    response: String

    /// Error message if failed
    errorMessage: String

    /// Execution duration in ms
    executionMs: Integer
}

/// Position response from M114
structure PositionResponse {
    /// X position
    @required
    x: Float

    /// Y position
    @required
    y: Float

    /// Z position
    @required
    z: Float

    /// E position (extruder, usually unused)
    e: Float

    /// Step count X
    countX: Integer

    /// Step count Y
    countY: Integer

    /// Step count Z
    countZ: Integer
}

/// Temperature response from M105
structure TemperatureResponse {
    /// Nozzle temperature
    @required
    nozzle: Float

    /// Nozzle target temperature
    @required
    nozzleTarget: Float

    /// Bed temperature
    @required
    bed: Float

    /// Bed target temperature
    @required
    bedTarget: Float
}
