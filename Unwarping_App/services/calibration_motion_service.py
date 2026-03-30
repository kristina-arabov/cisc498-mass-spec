"""
calibration_motion_service.py

Computes safe XYZ camera travel that keeps a detected chessboard in frame,
then plans an ordered list of printer positions for multi-image fisheye calibration.
Pure computation — no I/O, no Qt, no OpenCV.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


# ── Tunable constants ──────────────────────────────────────────────────────────

# Pixel buffer maintained between detected board corner extremes and image edges.
SAFETY_MARGIN_PX: int = 30

# Minimum board coverage fraction after a Z-up move — below this,
# corner detection becomes unreliable.
MIN_BOARD_COVERAGE_FRACTION: float = 0.35

# Moves smaller than this (mm) are skipped — not worth the settle time.
MIN_PLAY_MM: float = 5.0

# Fraction of available play actually commanded, to keep headroom from the limit.
Z_USE_FRACTION: float = 0.60
XY_USE_FRACTION: float = 0.50

# Absolute safety caps on any single commanded delta (mm).
MAX_Z_DELTA_MM: float = 20.0
MAX_XY_DELTA_MM: float = 15.0

# Printer feed rate used for calibration moves (mm/min).
CALIBRATION_FEED_RATE: int = 3000

# Time (ms) to wait after arriving at each position before capturing,
# allowing mechanical vibration to settle.
POST_MOVE_SETTLE_MS: int = 500

# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class BoardPlayAnalysis:
    """
    Describes the available camera movement range that keeps the chessboard
    fully within frame, given a gantry-mounted camera over a flat printer bed.

    Pixel margins are measured from the detected board edge to the image edge
    after subtracting SAFETY_MARGIN_PX.  Spatial values are in millimetres.
    """

    # Raw (safety-clipped) pixel margins from board extremes to image edges.
    margin_left_px:   float
    margin_right_px:  float
    margin_top_px:    float
    margin_bottom_px: float

    # Available Z travel (mm, positive magnitudes).
    z_can_move_up_mm:   float   # zoom-out headroom: board apparent size shrinks
    z_can_move_down_mm: float   # zoom-in  headroom: board apparent size grows

    # Available XY travel (mm, positive magnitudes).
    # "pos_x" means the camera can physically move in the +X direction.
    xy_can_move_pos_x_mm: float
    xy_can_move_neg_x_mm: float
    xy_can_move_pos_y_mm: float
    xy_can_move_neg_y_mm: float

    # Approximate spatial resolution at current Z height (mm per image pixel).
    mm_per_pixel: float


@dataclass
class CalibrationMove:
    """A single absolute printer position to occupy for one calibration capture."""

    abs_x: float
    abs_y: float
    abs_z: float
    label: str = ""   # human-readable description, e.g. "z_up", "home"


def analyze_board_play(
    corners: np.ndarray,
    img_shape: Tuple[int, int],
    K: np.ndarray,
    z_current: float,
) -> BoardPlayAnalysis:
    """
    Compute how far the gantry camera can safely travel in X, Y, and Z while
    keeping the detected chessboard fully visible with a safety margin.

    Parameters
    ----------
    corners     : Detected chessboard corners — any shape collapsible to (N, 2).
    img_shape   : Image dimensions as (width, height) in pixels.
    K           : 3×3 camera intrinsic matrix (rough single-image estimate is fine).
    z_current   : Current printer Z height in mm (distance from camera to board).

    Returns
    -------
    BoardPlayAnalysis
    """
    img_w, img_h = img_shape
    pts = corners.reshape(-1, 2).astype(float)

    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)

    board_w_px = x_max - x_min
    board_h_px = y_max - y_min

    # Pixel margins: distance from board extreme to image boundary, minus buffer.
    margin_left   = x_min          - SAFETY_MARGIN_PX
    margin_right  = img_w - x_max  - SAFETY_MARGIN_PX
    margin_top    = y_min          - SAFETY_MARGIN_PX
    margin_bottom = img_h - y_max  - SAFETY_MARGIN_PX

    # ── Z-up (zoom out) ───────────────────────────────────────────────────────
    # Apparent board width scales as board_w * z / (z + dz).
    # Stop when it shrinks to MIN_BOARD_COVERAGE_FRACTION * img_w.
    min_board_w_px = MIN_BOARD_COVERAGE_FRACTION * img_w
    if board_w_px > min_board_w_px and z_current > 0:
        dz_up = z_current * (board_w_px / min_board_w_px - 1.0)
    else:
        dz_up = 0.0

    # ── Z-down (zoom in) ──────────────────────────────────────────────────────
    # Board grows; stop when the tighter dimension would hit the safety boundary.
    safe_w = img_w - 2 * SAFETY_MARGIN_PX
    safe_h = img_h - 2 * SAFETY_MARGIN_PX
    scale_lim_w = safe_w / board_w_px if board_w_px > 0 else 1.0
    scale_lim_h = safe_h / board_h_px if board_h_px > 0 else 1.0
    scale_lim   = min(scale_lim_w, scale_lim_h)
    dz_down = z_current * (1.0 - 1.0 / scale_lim) if scale_lim > 1.0 else 0.0

    # ── XY play ───────────────────────────────────────────────────────────────
    # Paraxial approximation: pixels_per_mm ≈ fx / z
    # Moving the camera +X shifts the board -X in the image → uses left margin.
    fx            = float(K[0, 0])
    pixels_per_mm = fx / z_current if (z_current > 0 and fx > 0) else 1.0
    mm_per_pixel  = 1.0 / pixels_per_mm

    xy_pos_x = max(margin_left,   0.0) * mm_per_pixel
    xy_neg_x = max(margin_right,  0.0) * mm_per_pixel
    xy_pos_y = max(margin_top,    0.0) * mm_per_pixel
    xy_neg_y = max(margin_bottom, 0.0) * mm_per_pixel

    return BoardPlayAnalysis(
        margin_left_px=max(margin_left,     0.0),
        margin_right_px=max(margin_right,   0.0),
        margin_top_px=max(margin_top,       0.0),
        margin_bottom_px=max(margin_bottom, 0.0),
        z_can_move_up_mm=min(max(dz_up,    0.0), MAX_Z_DELTA_MM),
        z_can_move_down_mm=min(max(dz_down, 0.0), MAX_Z_DELTA_MM),
        xy_can_move_pos_x_mm=min(xy_pos_x,  MAX_XY_DELTA_MM),
        xy_can_move_neg_x_mm=min(xy_neg_x,  MAX_XY_DELTA_MM),
        xy_can_move_pos_y_mm=min(xy_pos_y,  MAX_XY_DELTA_MM),
        xy_can_move_neg_y_mm=min(xy_neg_y,  MAX_XY_DELTA_MM),
        mm_per_pixel=mm_per_pixel,
    )


def plan_calibration_moves(
    play: BoardPlayAnalysis,
    start_x: float,
    start_y: float,
    start_z: float,
) -> List[CalibrationMove]:
    """
    Build an ordered list of absolute printer positions for multi-image
    fisheye calibration.

    Priority order
    --------------
    1. Home position — always included, captured first (no movement required).
    2. Z-up          — changes apparent board scale; most effective at separating
                       distortion coefficients from focal length.
    3. Z-down        — pushes board corners further into the distorted region.
    4. XY shifts     — fallback when Z travel alone is insufficient (< MIN_PLAY_MM).
                       Applied in +X, -X, +Y, -Y order until 3 positions exist.

    Parameters
    ----------
    play            : BoardPlayAnalysis from analyze_board_play().
    start_x/y/z     : Current absolute printer position in mm.

    Returns
    -------
    Ordered List[CalibrationMove].
    """
    moves: List[CalibrationMove] = []

    # ── 1. Home: always capture here first ────────────────────────────────────
    moves.append(CalibrationMove(
        abs_x=start_x, abs_y=start_y, abs_z=start_z, label="home"
    ))

    # ── 2. Z-up (zoom out) ────────────────────────────────────────────────────
    if play.z_can_move_up_mm >= MIN_PLAY_MM:
        dz = min(play.z_can_move_up_mm * Z_USE_FRACTION, MAX_Z_DELTA_MM)
        moves.append(CalibrationMove(
            abs_x=start_x, abs_y=start_y, abs_z=start_z + dz, label="z_up"
        ))

    # ── 3. Z-down (zoom in) ───────────────────────────────────────────────────
    if play.z_can_move_down_mm >= MIN_PLAY_MM:
        dz = min(play.z_can_move_down_mm * Z_USE_FRACTION, MAX_Z_DELTA_MM)
        moves.append(CalibrationMove(
            abs_x=start_x, abs_y=start_y, abs_z=start_z - dz, label="z_down"
        ))

    # ── 4. XY fallback ────────────────────────────────────────────────────────
    if len(moves) < 3:
        xy_candidates = [
            (play.xy_can_move_pos_x_mm, "xy_pos_x",  1,  0),
            (play.xy_can_move_neg_x_mm, "xy_neg_x", -1,  0),
            (play.xy_can_move_pos_y_mm, "xy_pos_y",  0,  1),
            (play.xy_can_move_neg_y_mm, "xy_neg_y",  0, -1),
        ]
        for available, label, sx, sy in xy_candidates:
            if available >= MIN_PLAY_MM:
                delta = min(available * XY_USE_FRACTION, MAX_XY_DELTA_MM)
                moves.append(CalibrationMove(
                    abs_x=start_x + sx * delta,
                    abs_y=start_y + sy * delta,
                    abs_z=start_z,
                    label=label,
                ))

    return moves
