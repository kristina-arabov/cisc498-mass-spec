$version: "2.0"

namespace msrobot.domain.sample

use msrobot.core.common#Timestamp

/// One row written by sampling_service.addData(). CSV header: "Time (ms),Conductance,X,Y,Z"
structure ActualSampleRow {
    /// ms since recording start: int(round(time.time()*1000)) - startThr
    @required
    timeMs: Long

    /// Conductance in μS; 0 if meter disconnected.
    @required
    conductance: Integer

    @required
    x: Float

    @required
    y: Float

    @required
    z: Float
}

list ActualSampleRowList {
    member: ActualSampleRow
}

/// Timestamped conductance reading from ConThread's queue.
structure ConductanceReading {
    /// Value in μS.
    @required
    value: Integer

    @required
    timestamp: Timestamp
}
