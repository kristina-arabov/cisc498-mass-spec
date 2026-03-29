$version: "2.0"

namespace msrobot.core.geometry

structure Position2D {
    @required
    x: Float

    @required
    y: Float
}

structure Position3D {
    @required
    x: Float

    @required
    y: Float

    @required
    z: Float
}

/// Image resolution in pixels.
structure Resolution {
    @required
    width: Integer

    @required
    height: Integer
}

/// Sampling point spacing in mm.
structure Resolution2D {
    @required
    x: Float

    @required
    y: Float
}

structure Range {
    @required
    lower: Float

    @required
    upper: Float
}

list FloatList {
    member: Float
}

/// 3×3 matrix as a list of rows.
list Matrix3x3 {
    member: FloatList
}
