$version: "2.0"

namespace msrobot.domain.roi

use msrobot.core.geometry#Position2D

list VertexList {
    member: Position2D
}

/// ROI polygon drawn in p2_roi_selection.py (Rectangle or freehand Draw mode).
/// Vertices are stored in stage mm coordinates after sampling_service.findLocations() transforms them.
structure ROI {
    @required
    vertices: VertexList

    /// Area in mm² (only valid after coordinate transformation).
    area: Float
}
