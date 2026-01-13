$version: "2.0"

namespace msrobot.domain.roi

use msrobot.core.geometry#BoundingBox
use msrobot.core.geometry#Position2D

/// Coordinate system for ROI
enum CoordinateSystem {
    /// Pixel coordinates
    PIXEL

    /// Stage coordinates in mm
    STAGE_MM
}

/// List of 2D positions (vertices)
list VertexList {
    member: Position2D
}

/// Region of Interest polygon
structure ROI {
    /// Polygon vertices (ordered)
    @required
    vertices: VertexList

    /// Coordinate system
    @required
    coordinateSystem: CoordinateSystem

    /// Computed bounding box
    @required
    boundingBox: BoundingBox

    /// Computed area in mm² (if STAGE_MM)
    area: Float
}

/// ROI with source tracking
structure ROIWithSource {
    /// The ROI polygon
    @required
    roi: ROI

    /// Method used to create ROI
    @required
    sourceMethod: ROISourceMethod

    /// Transform session ID used for pixel-to-stage conversion
    transformSessionId: String

    /// Original pixel vertices if converted from pixels
    originalPixelVertices: VertexList
}

/// How the ROI was created
enum ROISourceMethod {
    /// Manually drawn by user
    USER_DRAWN

    /// Auto-detected from image
    AUTO_DETECTED

    /// Loaded from file
    LOADED

    /// Programmatically defined
    PROGRAMMATIC
}
