import os
import cv2
import numpy as np
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QMovie

from Unwarping_App.components.utils import updateFrame
from Unwarping_App.components.common import LightingDropdown, UnwarpComparison

from Unwarping_App.services import calibration_service, calibration_motion_service, device_service


# How often corner detection is re-run against the latest camera frame (ms).
# findChessboardCorners is expensive, so keep this well above ~200ms.
CORNER_PREVIEW_INTERVAL_MS: int = 500

# If True, moves the printer to several viewpoints before calibrating.
# Set False to use a single image — handy when the printer is unavailable.
MULTI_IMAGE_CALIBRATION: bool = True

# If True, saves every captured calibration frame to DEBUG_OUTPUT_DIR/<timestamp>/.
DEBUG_SAVE_IMAGES: bool = True

# Folder (relative to project root) where debug images are written.
DEBUG_OUTPUT_DIR: str = "debugging"

# Timeout (ms) waiting for a post-movement camera frame in _wait_for_fresh_frame.
FRESH_FRAME_TIMEOUT_MS: int = 2000

# Sanity bounds for the rough focal length (px) used in board-play analysis.
# Single-image fisheye calibration diverges often; values outside this range
# are replaced with fx = image_width as a heuristic fallback (~60° FoV webcam).
FOCAL_LENGTH_MIN_PX: float = 100.0
FOCAL_LENGTH_MAX_PX: float = 5000.0


# ── Corner preview worker ──────────────────────────────────────────────────────

class CornerPreviewWorker(QThread):
    """
    Runs corner detection every CORNER_PREVIEW_INTERVAL_MS and emits the result.
    The page blends the latest corners onto every camera frame so the overlay
    stays smooth without running findChessboardCorners at 30 fps.
    """

    # (found: bool, corners: np.ndarray | None)
    corners_updated = pyqtSignal(bool, object)

    def __init__(self, camera, checkerboard, parent=None):
        super().__init__(parent)
        self.camera       = camera
        self.checkerboard = checkerboard
        self._stop        = False

    def stop(self):
        self._stop = True

    def run(self):
        while not self._stop:
            frame = self.camera.frame
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ret, corners = cv2.findChessboardCorners(
                    gray, self.checkerboard,
                    cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
                )
                self.corners_updated.emit(ret, corners if ret else None)
            self.msleep(CORNER_PREVIEW_INTERVAL_MS)


# ── Calibration worker ─────────────────────────────────────────────────────────

class CalibrationWorker(QThread):
    """
    Background thread for the full multi-image fisheye calibration sequence:
    capture home frame → rough K → board-play analysis → multi-position capture
    (if printer connected) → return home → run calibration → emit result.
    """

    status_update = pyqtSignal(str)
    result_ready  = pyqtSignal(object)   # np.ndarray (BGR) — final undistorted image
    finished      = pyqtSignal(bool, str)

    def __init__(self, camera, printer, checkerboard, transformation, parent=None):
        super().__init__(parent)
        self.camera         = camera
        self.printer        = printer
        self.checkerboard   = checkerboard
        self.transformation = transformation
        self._abort         = False

    def abort(self):
        self._abort = True

    def run(self):
        try:
            self._execute()
        except Exception as e:
            self.finished.emit(False, f"Unexpected calibration error: {e}")

    def _execute(self):
        self.status_update.emit("Capturing initial frame…")
        raw = self.camera.frame
        if raw is None:
            self.finished.emit(False, "No camera frame available. Check camera connection.")
            return
        home_frame = raw.copy()

        objp = np.zeros(
            (1, self.checkerboard[0] * self.checkerboard[1], 3), np.float32
        )
        objp[0, :, :2] = np.mgrid[
            0:self.checkerboard[0], 0:self.checkerboard[1]
        ].T.reshape(-1, 2)

        # Rough single-image K — only used for board-play analysis, not quality-gated.
        _, K_rough, _, _ = calibration_service.checkFishReadability(
            home_frame, self.checkerboard, objp,
            calibration_service.FISHEYE_CALIBRATION_FLAGS,
        )

        gray = cv2.cvtColor(home_frame, cv2.COLOR_BGR2GRAY)
        corners_ret, corners = cv2.findChessboardCorners(
            gray, self.checkerboard,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
        )

        prt_connected = getattr(self.printer, "prtconnect", False)

        # K validity is NOT required for printer_ready — single-image fisheye
        # calibration diverges frequently (negative/huge focal length).  The play
        # analysis falls back to a heuristic focal length when K_rough is bad.
        printer_ready = (
            self.printer is not None
            and prt_connected
            and corners_ret
        )

        K_valid = K_rough is not None and FOCAL_LENGTH_MIN_PX <= K_rough[0, 0] <= FOCAL_LENGTH_MAX_PX
        print(
            f"[CalibWorker] printer_ready={printer_ready}  "
            f"prtconnect={prt_connected}  corners_ret={corners_ret}  "
            f"K_valid={K_valid}  K[0,0]={K_rough[0,0] if K_rough is not None else 'None':.1f}"
        )

        if not MULTI_IMAGE_CALIBRATION:
            self.status_update.emit("Multi-image calibration disabled — using single image.")
            images = [home_frame]
        elif not printer_ready:
            reason = (
                "Printer not connected"
                if not prt_connected
                else "Board corners not detected in initial frame"
            )
            self.status_update.emit(f"{reason} — using single-image calibration.")
            images = [home_frame]
        else:
            images = self._multi_capture(home_frame, corners, gray, K_rough)
            if images is None:
                return

        n = len(images)
        self.status_update.emit(f"Running calibration on {n} image(s)…")

        success, final_image, msg = calibration_service.getCheckerboardUnwarp(
            images, self.checkerboard, self.transformation
        )

        if success:
            self.result_ready.emit(final_image)
            self.finished.emit(
                True,
                f"Calibration complete — {n} image(s), "
                f"board {self.checkerboard[0]}×{self.checkerboard[1]}.",
            )
        else:
            self.finished.emit(False, msg or "Calibration failed.")

    def _wait_for_fresh_frame(self):
        """Wait for a frame newer than the one in camera.frame at call time.
        Avoids grabbing a stale frame captured during printer movement.
        Returns the new frame, or falls back to the current frame on timeout.
        """
        old_frame = self.camera.frame
        deadline_ms = FRESH_FRAME_TIMEOUT_MS
        elapsed = 0
        while elapsed < deadline_ms:
            current = self.camera.frame
            if current is not old_frame and current is not None:
                return current
            self.msleep(30)
            elapsed += 30
        # Timeout — return whatever we have
        return self.camera.frame

    def _multi_capture(self, home_frame, corners, gray, K_rough):
        start_pos = device_service.get_printer_position_timeout(self.printer)
        if start_pos is None:
            self.status_update.emit(
                "Could not read printer position — using single-image calibration."
            )
            print("[CalibWorker] get_printer_position_timeout returned None — no 'Count' in printer.line within timeout.")
            return [home_frame]

        start_x, start_y, start_z = start_pos
        self.transformation.chessboard_loc = start_pos
        self.transformation.height         = start_z

        img_shape = (gray.shape[1], gray.shape[0])
        img_w = gray.shape[1]

        # Sanity-check K_rough: single-image fisheye calibration often diverges
        # (negative or astronomically large focal lengths).  Use fx = image_width
        # as a heuristic when the result is outside plausible bounds.
        K_for_play = K_rough
        if (
            K_rough is None
            or not (FOCAL_LENGTH_MIN_PX <= K_rough[0, 0] <= FOCAL_LENGTH_MAX_PX)
        ):
            K_for_play = np.array([
                [float(img_w),          0.0, img_w / 2.0],
                [        0.0, float(img_w), gray.shape[0] / 2.0],
                [        0.0,          0.0,          1.0],
            ], dtype=np.float64)
            print(
                f"[CalibWorker] K_rough out of bounds (fx={K_rough[0,0] if K_rough is not None else 'None'}) "
                f"— using heuristic fx={img_w} for play analysis."
            )

        play  = calibration_motion_service.analyze_board_play(corners, img_shape, K_for_play, start_z)
        moves = calibration_motion_service.plan_calibration_moves(play, start_x, start_y, start_z)

        print(
            f"[CalibWorker] start_pos=({start_x:.2f}, {start_y:.2f}, {start_z:.2f})  "
            f"img={img_shape}  "
            f"Z_up={play.z_can_move_up_mm:.2f}mm  Z_down={play.z_can_move_down_mm:.2f}mm  "
            f"XY+x={play.xy_can_move_pos_x_mm:.2f}  -x={play.xy_can_move_neg_x_mm:.2f}  "
            f"+y={play.xy_can_move_pos_y_mm:.2f}  -y={play.xy_can_move_neg_y_mm:.2f}  "
            f"planned_moves={[m.label for m in moves]}"
        )

        self.status_update.emit(
            f"Planned {len(moves)} capture position(s)  "
            f"(Z headroom: +{play.z_can_move_up_mm:.1f} / -{play.z_can_move_down_mm:.1f} mm)."
        )

        # Prepare debug output directory once per run (timestamped sub-folder).
        debug_dir = None
        if DEBUG_SAVE_IMAGES:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            debug_dir = os.path.join(DEBUG_OUTPUT_DIR, timestamp)
            os.makedirs(debug_dir, exist_ok=True)

        images = []
        for i, move in enumerate(moves):
            if self._abort:
                self.finished.emit(False, "Calibration cancelled.")
                return None

            if move.label == "home":
                images.append(home_frame)
                self.status_update.emit(f"Image 1/{len(moves)}: home position.")
                if debug_dir is not None:
                    cv2.imwrite(os.path.join(debug_dir, f"01_home.png"), home_frame)
                continue

            self.status_update.emit(
                f"Image {i + 1}/{len(moves)}: moving to {move.label} "
                f"(X{move.abs_x:.1f}  Y{move.abs_y:.1f}  Z{move.abs_z:.1f})…"
            )
            device_service.move_printer_absolute(
                self.printer,
                move.abs_x, move.abs_y, move.abs_z,
                calibration_motion_service.CALIBRATION_FEED_RATE,
            )
            confirmed = device_service.get_printer_position_timeout(self.printer)
            if confirmed is None:
                self.status_update.emit(f"  ↳ Timed out — skipping {move.label}.")
                continue

            # Settle: wait for vibration to die down, then grab a fresh frame
            # that was captured *after* movement finished (not during transit).
            self.msleep(calibration_motion_service.POST_MOVE_SETTLE_MS)
            frame = self._wait_for_fresh_frame()
            if frame is None:
                self.status_update.emit(f"  ↳ No frame available — skipping {move.label}.")
                continue

            images.append(frame.copy())
            if debug_dir is not None:
                fname = f"{i + 1:02d}_{move.label}.png"
                cv2.imwrite(os.path.join(debug_dir, fname), frame)

        self.status_update.emit("Returning to starting position…")
        device_service.move_printer_absolute(
            self.printer, start_x, start_y, start_z,
            calibration_motion_service.CALIBRATION_FEED_RATE,
        )
        device_service.get_printer_position_timeout(self.printer)
        return images


# ── Page widget ────────────────────────────────────────────────────────────────

class CheckerboardDetection(QWidget):
    next = pyqtSignal()

    def __init__(self, camera, lights, printer, transformation):
        super().__init__()
        self.camera         = camera
        self.lights         = lights
        self.printer        = printer
        self.transformation = transformation

        self._worker         = None   # CalibrationWorker
        self._preview_worker = None   # CornerPreviewWorker
        self._has_unwarp_result = False

        self._loading_movie = QMovie("Unwarping_App/components/images/Loading.gif")
        self._loading_movie.setScaledSize(QSize(100, 100))

        # Latest corner-detection result — applied to every incoming camera frame.
        self._latest_corners       = None
        self._latest_corners_found = False
        self._preview_checkerboard = None   # checkerboard used for current preview

        self.initUI()

    def initUI(self):
        styling = "Unwarping_App/components/style.css"
        with open(styling, "r") as f:
            self.setStyleSheet(f.read())

        layout = QHBoxLayout(self)

        self.component_unwarpComparison = UnwarpComparison()

        right = QWidget()
        layout_right = QVBoxLayout(right)

        label_title = QLabel("Checkerboard Detection", objectName="page_title")
        component_lightControl = LightingDropdown()

        self.component_checkerboardParams = CheckerboardParamsSection()
        self.component_checkerboardParams.setFixedWidth(
            component_lightControl.sizeHint().width()
        )

        self.label_status = QLabel("Enter board dimensions to begin.", objectName="status_label")
        self.label_status.setWordWrap(True)
        self.label_status.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        button_next = QPushButton("Next", objectName="blue")
        button_next.setEnabled(False)
        button_next.clicked.connect(self.next.emit)
        self.button_next = button_next

        layout_right.addStretch()
        layout_right.addWidget(label_title,                       alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(component_lightControl,            alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(self.component_checkerboardParams, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(self.label_status,                 alignment=Qt.AlignLeft | Qt.AlignTop)
        layout_right.addWidget(button_next,                       alignment=Qt.AlignRight)
        layout_right.addStretch()

        layout.addWidget(self.component_unwarpComparison, alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(right,                           alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # TOP panel: live camera feed.  _on_camera_frame blends corner overlay
        # onto every frame so detection stays smooth at full frame-rate.
        self.camera.change_pixmap_signal.connect(self._on_camera_frame)

        component_lightControl.slider.valueChanged.connect(
            lambda: device_service.set_brightness(
                component_lightControl.slider.value(), self.lights
            )
        )

        # Restart corner detection whenever the board dimensions change.
        self.component_checkerboardParams.input_rows.textChanged.connect(self._on_dims_changed)
        self.component_checkerboardParams.input_columns.textChanged.connect(self._on_dims_changed)

        self.component_unwarpComparison.arrow.button.clicked.connect(self._start_calibration)

        # BOTTOM panel placeholder — only ever replaced by a successful calibration.
        self.component_unwarpComparison.result.image_label.setText(
            "Undistorted image will appear here."
        )

    # ── Top panel: live feed with corner overlay ───────────────────────────────

    def _on_camera_frame(self, frame):
        """Draw the latest detected corners onto the frame before display, if any."""
        if self._latest_corners_found and self._latest_corners is not None \
                and self._preview_checkerboard is not None:
            display = frame.copy()
            cv2.drawChessboardCorners(
                display, self._preview_checkerboard, self._latest_corners, True
            )
            updateFrame(self.component_unwarpComparison.feed, display)
        else:
            updateFrame(self.component_unwarpComparison.feed, frame)

    def _on_corners_updated(self, found: bool, corners):
        """Slot for CornerPreviewWorker.corners_updated — stores latest detection result."""
        self._latest_corners_found = found
        self._latest_corners       = corners
        if found:
            self.label_status.setText("Chessboard detected — ready to calibrate.")
        else:
            self.label_status.setText("Searching for chessboard corners…")

    # ── Preview management ─────────────────────────────────────────────────────

    def _on_dims_changed(self):
        """Restart corner detection whenever the user edits the board dimensions."""
        if self._worker and self._worker.isRunning():
            return  # Don't interfere while calibration is running.

        # Require a fresh successful unwarp when board dimensions change.
        self._has_unwarp_result = False
        self.button_next.setEnabled(False)

        checkerboard = self._parse_checkerboard()
        if checkerboard:
            self._start_preview(checkerboard)
        else:
            self._stop_preview()
            self.label_status.setText("Enter board dimensions to begin.")

    def _start_preview(self, checkerboard):
        self._stop_preview()
        self._preview_checkerboard = checkerboard
        self._latest_corners       = None
        self._latest_corners_found = False
        self._preview_worker = CornerPreviewWorker(self.camera, checkerboard)
        self._preview_worker.corners_updated.connect(self._on_corners_updated)
        self._preview_worker.start()
        self.label_status.setText("Searching for chessboard corners…")

    def _stop_preview(self, clear_corners=True):
        """
        Signal the preview worker to stop.  Does not block — the worker
        terminates naturally within one CORNER_PREVIEW_INTERVAL_MS cycle.

        If clear_corners is False the last detected corner positions are
        preserved so _on_camera_frame keeps showing the overlay while
        calibration runs.
        """
        if clear_corners:
            self._latest_corners       = None
            self._latest_corners_found = False
            self._preview_checkerboard = None
        if self._preview_worker is not None:
            self._preview_worker.stop()
            self._preview_worker = None

    # ── Calibration orchestration ──────────────────────────────────────────────

    def _start_calibration(self):
        checkerboard = self._parse_checkerboard()
        if not checkerboard:
            self.label_status.setText("Cannot calibrate with missing or invalid board dimensions.")
            return

        if self._worker and self._worker.isRunning():
            return

        self._has_unwarp_result = False
        self.button_next.setEnabled(False)

        # Stop the preview worker but keep the last corners visible in the top
        # panel so the user can see what was detected when calibration started.
        self._stop_preview(clear_corners=False)

        # Show loading spinner in the result panel while calibration runs.
        result_label = self.component_unwarpComparison.result.image_label
        result_label.setAlignment(Qt.AlignCenter)
        result_label.setMovie(self._loading_movie)
        self._loading_movie.start()

        self.component_unwarpComparison.arrow.button.setEnabled(False)
        self.label_status.setText("Starting calibration…")

        self._worker = CalibrationWorker(
            self.camera, self.printer, checkerboard, self.transformation
        )
        self._worker.status_update.connect(self.label_status.setText)
        self._worker.result_ready.connect(self._on_result_ready)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_result_ready(self, final_image):
        """Show the undistorted image in the bottom panel."""
        calibration_service.updateResult(final_image, self.component_unwarpComparison.result)
        self._has_unwarp_result = True
        self.button_next.setEnabled(True)

    def _on_worker_finished(self, success: bool, message: str):
        self._loading_movie.stop()
        self.component_unwarpComparison.arrow.button.setEnabled(True)
        self.label_status.setText(message)

        if success:
            # Clear the corner overlay — top panel returns to clean live feed.
            self._latest_corners       = None
            self._latest_corners_found = False
        else:
            self._has_unwarp_result = False
            self.button_next.setEnabled(False)
            # Show error in bottom panel and restart corner preview so the user
            # can reposition the board and try again without re-entering dims.
            self.component_unwarpComparison.result.image_label.setText(message)
            checkerboard = self._parse_checkerboard()
            if checkerboard:
                self._start_preview(checkerboard)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _parse_checkerboard(self):
        """Return (cols-1, rows-1) if inputs are valid, else None."""
        try:
            c = int(self.component_checkerboardParams.input_columns.text())
            r = int(self.component_checkerboardParams.input_rows.text())
            return (c - 1, r - 1) if c > 1 and r > 1 else None
        except ValueError:
            return None

    # ── Reset ──────────────────────────────────────────────────────────────────

    def clearAll(self):
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait()

        self._stop_preview()

        self.component_checkerboardParams.input_columns.clear()
        self.component_checkerboardParams.input_rows.clear()
        self.component_unwarpComparison.result.image_label.setText(
            "Undistorted image will appear here."
        )
        self._has_unwarp_result = False
        self.button_next.setEnabled(False)
        self.label_status.setText("Enter board dimensions to begin.")


# ── Reusable sub-component ─────────────────────────────────────────────────────

class CheckerboardParamsSection(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        container = QWidget(objectName="light_blue_box")
        layout_container = QVBoxLayout(container)

        label_title = QLabel("Checkerboard size", objectName="larger")
        label_title.setStyleSheet("font-weight: bold;")

        row_1 = QWidget()
        layout_row_1 = QHBoxLayout(row_1)
        layout_row_1.addWidget(QLabel("Rows: "))
        self.input_rows = QLineEdit()
        layout_row_1.addWidget(self.input_rows)

        row_2 = QWidget()
        layout_row_2 = QHBoxLayout(row_2)
        layout_row_2.addWidget(QLabel("Columns: "))
        self.input_columns = QLineEdit()
        layout_row_2.addWidget(self.input_columns)

        layout_container.addWidget(label_title)
        layout_container.addWidget(row_1)
        layout_container.addWidget(row_2)

        layout.addWidget(container)

        self.setStyleSheet("""
            QWidget   { background-color: #C8D3F1; }
            QLineEdit { background-color: white;   }
        """)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
