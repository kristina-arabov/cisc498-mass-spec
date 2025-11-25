$version: "2.0"

namespace msrobot.core.geometry

/// 2D position in millimeters
structure Position2D {
    /// X coordinate in mm
    @required
    x: Float

    /// Y coordinate in mm
    @required
    y: Float
}

/// 3D position in millimeters
structure Position3D {
    /// X coordinate in mm
    @required
    x: Float

    /// Y coordinate in mm
    @required
    y: Float

    /// Z coordinate in mm
    @required
    z: Float
}

/// 3D vector
structure Vector3D {
    /// X component
    @required
    x: Float

    /// Y component
    @required
    y: Float

    /// Z component
    @required
    z: Float
}

/// Quaternion for rotation representation (w, x, y, z)
structure Quaternion {
    /// Scalar component
    @required
    w: Float

    /// X component
    @required
    x: Float

    /// Y component
    @required
    y: Float

    /// Z component
    @required
    z: Float
}

/// Complete 6DOF pose (position + orientation)
structure Pose {
    /// 3D position
    @required
    position: Position3D

    /// Orientation as quaternion
    @required
    orientation: Quaternion
}

/// Image resolution in pixels
structure Resolution {
    /// Width in pixels
    @required
    width: Integer

    /// Height in pixels
    @required
    height: Integer
}

/// Spatial resolution for sampling
structure Resolution2D {
    /// X resolution in mm
    @required
    x: Float

    /// Y resolution in mm
    @required
    y: Float
}

/// Numeric range with bounds
structure Range {
    /// Lower bound
    @required
    lower: Float

    /// Upper bound
    @required
    upper: Float
}

/// Axis-aligned bounding box
structure BoundingBox {
    /// Minimum X coordinate
    @required
    minX: Float

    /// Maximum X coordinate
    @required
    maxX: Float

    /// Minimum Y coordinate
    @required
    minY: Float

    /// Maximum Y coordinate
    @required
    maxY: Float
}

/// List of floats
list FloatList {
    member: Float
}

/// 3x3 matrix as list of rows
list Matrix3x3 {
    member: FloatList
}

/// 4x4 matrix as list of rows
list Matrix4x4 {
    member: FloatList
}
