"""
TAB 2: Motion, Actuation & Vision
RAW H.264 over UDP (ffplay-style) integrated
LOWEST LATENCY CONFIGURATION
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QDoubleSpinBox, QSpinBox, QGridLayout,
    QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage

import subprocess
import threading
import numpy as np


# ===================== CAMERA WIDGET (UDP H264) =====================

class CameraStreamWidget(QWidget):
    def __init__(self, camera_name, default_port="5000"):
        super().__init__()

        self.is_streaming = False
        self.proc = None

        # HARD-CODED (must match sender)
        self.width = 640
        self.height = 480

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        title = QLabel(f"📷 {camera_name}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight:bold; font-size:11pt; color:#64b5f6;")
        layout.addWidget(title)

        # ---------- VIDEO ----------
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 400)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setStyleSheet("""
            background:#1e1e1e;
            border:2px solid #555;
        """)
        layout.addWidget(self.video_label, 1)

        # ---------- CONTROLS ----------
        controls = QHBoxLayout()
        controls.setSpacing(6)

        self.url_input = QLineEdit(default_port)
        self.url_input.setPlaceholderText("UDP PORT (e.g. 5000)")
        self.url_input.setStyleSheet("font-size:9pt;")

        self.connect_btn = QPushButton("▶ Connect")
        self.disconnect_btn = QPushButton("⏹ Disconnect")
        self.disconnect_btn.setEnabled(False)

        self.connect_btn.setStyleSheet("background:#2e7d32; font-size:9pt;")
        self.disconnect_btn.setStyleSheet("background:#c62828; font-size:9pt;")

        self.connect_btn.clicked.connect(self.start_stream)
        self.disconnect_btn.clicked.connect(self.stop_stream)

        controls.addWidget(QLabel("PORT:"))
        controls.addWidget(self.url_input, 1)
        controls.addWidget(self.connect_btn)
        controls.addWidget(self.disconnect_btn)

        layout.addLayout(controls)

        self.status_label = QLabel("⚪ Disconnected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size:9pt; color:#757575;")
        layout.addWidget(self.status_label)

    # ===================== STREAM CONTROL =====================

    def start_stream(self):
        port = self.url_input.text().strip()
        if not port.isdigit():
            self.status_label.setText("❌ Invalid port")
            return

        cmd = [
            "ffmpeg",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-probesize", "32",
            "-analyzeduration", "0",
            "-f", "h264",
            "-i", f"udp://0.0.0.0:{port}",
            "-pix_fmt", "rgb24",
            "-f", "rawvideo",
            "-"
        ]

        try:
            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            )

            self.is_streaming = True
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.status_label.setText("🟢 UDP STREAM ACTIVE")

            self.thread = threading.Thread(
                target=self._reader_loop, daemon=True
            )
            self.thread.start()

        except Exception:
            self.status_label.setText("❌ FFmpeg failed")

    def stop_stream(self):
        self.is_streaming = False

        if self.proc:
            self.proc.kill()
            self.proc = None

        self.video_label.clear()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.status_label.setText("⚪ Disconnected")

    def _reader_loop(self):
        frame_size = self.width * self.height * 3

        while self.is_streaming:
            raw = self.proc.stdout.read(frame_size)
            if len(raw) != frame_size:
                continue

            frame = np.frombuffer(raw, np.uint8).reshape(
                (self.height, self.width, 3)
            )

            qimg = QImage(
                frame.data,
                self.width,
                self.height,
                self.width * 3,
                QImage.Format_RGB888
            )

            pix = QPixmap.fromImage(qimg).scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.video_label.setPixmap(pix)


# ===================== ACTUATION TAB =====================

class ActuationTab(QWidget):
    def __init__(self, ros_interface):
        super().__init__()
        self.ros_interface = ros_interface
        self.pump_states = [0, 0, 0, 0]

        main = QVBoxLayout(self)
        main.setSpacing(16)

        # ---------- ROW 1: Stepper + MAIN Camera ----------
        row1 = QHBoxLayout()

        stepper = self._create_stepper_control()
        self.camera1 = CameraStreamWidget("CAMERA 1", "5000")

        row1.addWidget(stepper, 1)
        row1.addWidget(self.camera1, 4)
        main.addLayout(row1)

        # ---------- ROW 2 ----------
        row2 = QHBoxLayout()

        left_controls = QVBoxLayout()
        left_controls.addWidget(self._create_servo_control())
        left_controls.addWidget(self._create_pump_control())

        cameras = QHBoxLayout()
        self.camera2 = CameraStreamWidget("CAMERA 2", "5001")
        self.camera3 = CameraStreamWidget("CAMERA 3", "5002")
        cameras.addWidget(self.camera2)
        cameras.addWidget(self.camera3)

        row2.addLayout(left_controls, 1)
        row2.addLayout(cameras, 3)
        main.addLayout(row2)

    # ===================== CONTROLS =====================

    def _create_stepper_control(self):
        group = QGroupBox("STEPPER (ESP32 #2)")
        group.setMaximumWidth(300)

        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        angle = QDoubleSpinBox()
        angle.setRange(-360, 360)
        angle.setSuffix(" °")
        angle.setFixedWidth(110)

        rotate = QPushButton("ROTATE")
        rotate.setMinimumHeight(28)

        layout.addWidget(QLabel("Target Angle"))
        layout.addWidget(angle)
        layout.addWidget(rotate)
        layout.addStretch()
        return group

    def _create_servo_control(self):
        group = QGroupBox("SERVO MOTORS (ESP32 #1)")
        layout = QGridLayout(group)

        for i in range(3):
            layout.addWidget(QLabel(f"Servo {i+1}"), i, 0)

            spin = QSpinBox()
            spin.setRange(0, 180)
            spin.setSuffix(" °")
            spin.setFixedWidth(90)

            btn = QPushButton("SEND")
            btn.setFixedWidth(70)

            layout.addWidget(spin, i, 1)
            layout.addWidget(btn, i, 2)

        return group

    def _create_pump_control(self):
        group = QGroupBox("PUMP CONTROL (ESP32 #2)")
        layout = QGridLayout(group)

        headers = ["Pump", "FWD", "REV", "STOP"]
        for c, h in enumerate(headers):
            lbl = QLabel(h)
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl, 0, c)

        for i in range(4):
            layout.addWidget(QLabel(str(i+1)), i+1, 0)
            for c in range(1, 4):
                btn = QPushButton(headers[c])
                btn.setMinimumHeight(24)
                layout.addWidget(btn, i+1, c)

        stop_all = QPushButton("EMERGENCY STOP")
        stop_all.setMinimumHeight(34)
        stop_all.setStyleSheet("background:#d32f2f; font-weight:bold;")
        layout.addWidget(stop_all, 5, 0, 1, 4)

        return group
