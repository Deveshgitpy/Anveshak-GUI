"""
TAB 1: Atmospheric & Soil Analysis
Real-time plots and numeric displays for all sensor data (atmospheric and soil).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, QSize
import pyqtgraph as pg
from collections import deque
import time


# ===================== SCIENTIFIC PLOT =====================

class ScientificPlot(pg.PlotWidget):


    def __init__(self, title, ylabel, unit="", window_seconds=120, color="#64b5f6"):
        super().__init__()

        self.window_seconds = window_seconds
        self.time_data = deque(maxlen=2000)
        self.value_data = deque(maxlen=2000)
        self.start_time = time.time()

        self.setBackground("#1a1a1a")
        self.setTitle(title, color=color, size="14pt")
        self.setLabel("left", ylabel, units=unit)
        self.setLabel("bottom", "Time", units="s")
        self.showGrid(x=True, y=True, alpha=0.3)

        self.curve = self.plot(
            pen=pg.mkPen(color=color, width=2)
        )

        self.enableAutoRange(axis="y", enable=True)
        self.setAntialiasing(True)

    #  FORCE SQUARE GRAPH
    def sizeHint(self):
        return QSize(300, 300)

    def minimumSizeHint(self):
        return QSize(260, 260)

    def add_data_point(self, value):
        t = time.time() - self.start_time
        self.time_data.append(t)
        self.value_data.append(value)

        cutoff = t - self.window_seconds
        while self.time_data and self.time_data[0] < cutoff:
            self.time_data.popleft()
            self.value_data.popleft()

        self.curve.setData(self.time_data, self.value_data)


#VALUE PANEL

class SensorDisplayPanel(QFrame):
    """
    Compact numeric display panel
    """

    def __init__(self, name, unit="", color="#64b5f6"):
        super().__init__()

        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {color};
                border-radius: 6px;
                background-color: #2b2b2b;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)

        title = QLabel(name)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color:{color}; font-size:11pt; font-weight:bold;")
        layout.addWidget(title)

        self.value_label = QLabel("--")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet(
            "font-size:22pt; font-weight:bold; font-family:monospace;"
        )
        layout.addWidget(self.value_label)

        unit_lbl = QLabel(unit)
        unit_lbl.setAlignment(Qt.AlignCenter)
        unit_lbl.setStyleSheet("color:#9e9e9e; font-size:10pt;")
        layout.addWidget(unit_lbl)

    def update_value(self, value):
        self.value_label.setText(f"{value:.2f}")


# ANALYSIS TAB

class AnalysisTab(QWidget):
    """
    Tab 1: Atmospheric & Soil Analysis
    """

    def __init__(self, ros_interface):
        super().__init__()
        self.ros = ros_interface

        main = QVBoxLayout(self)
        main.setSpacing(15)

        main.addWidget(self._create_atmospheric_section())
        main.addLayout(self._create_soil_section())

        self._connect_signals()

    # ATMOSPHERIC 

    def _create_atmospheric_section(self):
        group = QGroupBox("ATMOSPHERIC ANALYSIS")
        layout = QGridLayout(group)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)

        self.atmos_temp_plot = ScientificPlot(
            "Atmospheric Temperature", "Temp", "°C", color="#ff6b6b"
        )
        self.humidity_plot = ScientificPlot(
            "Atmospheric Humidity", "Humidity", "%", color="#4ecdc4"
        )
        self.gas_plot = ScientificPlot(
            "Gas Concentration (MQ-4)", "Gas", "ppm", color="#feca57"
        )

        self.atmos_temp_panel = SensorDisplayPanel("TEMP", "°C", "#ff6b6b")
        self.humidity_panel = SensorDisplayPanel("HUMIDITY", "%", "#4ecdc4")
        self.gas_panel = SensorDisplayPanel("GAS", "ppm", "#feca57")

        layout.addWidget(self.atmos_temp_plot, 0, 0)
        layout.addWidget(self.humidity_plot, 0, 1)
        layout.addWidget(self.atmos_temp_panel, 0, 2)

        layout.addWidget(self.gas_plot, 1, 0, 1, 2)
        layout.addWidget(self.gas_panel, 1, 2)

        return group

    # SOIL 

    def _create_soil_section(self):
        soil_layout = QHBoxLayout()
        soil_layout.setSpacing(15)

        # ===== SOIL 1 =====
        soil1 = QGroupBox("SOIL SAMPLE 1")
        s1 = QGridLayout(soil1)
        s1.setColumnStretch(0, 1)
        s1.setColumnStretch(1, 1)

        self.soil1_temp_plot = ScientificPlot("Temp", "°C", "°C", color="#8bc34a")
        self.soil1_moist_plot = ScientificPlot("Moisture", "%", "%", color="#81c784")
        self.soil1_temp_panel = SensorDisplayPanel("TEMP", "°C", "#8bc34a")
        self.soil1_moist_panel = SensorDisplayPanel("MOIST", "%", "#81c784")

        s1.addWidget(self.soil1_temp_plot, 0, 0)
        s1.addWidget(self.soil1_moist_plot, 0, 1)
        s1.addWidget(self.soil1_temp_panel, 1, 0)
        s1.addWidget(self.soil1_moist_panel, 1, 1)

        # ===== SOIL 2 =====
        soil2 = QGroupBox("SOIL SAMPLE 2")
        s2 = QGridLayout(soil2)
        s2.setColumnStretch(0, 1)
        s2.setColumnStretch(1, 1)

        self.soil2_temp_plot = ScientificPlot("Temp", "°C", "°C", color="#ff9800")
        self.soil2_moist_plot = ScientificPlot("Moisture", "%", "%", color="#ffb74d")
        self.soil2_temp_panel = SensorDisplayPanel("TEMP", "°C", "#ff9800")
        self.soil2_moist_panel = SensorDisplayPanel("MOIST", "%", "#ffb74d")

        s2.addWidget(self.soil2_temp_plot, 0, 0)
        s2.addWidget(self.soil2_moist_plot, 0, 1)
        s2.addWidget(self.soil2_temp_panel, 1, 0)
        s2.addWidget(self.soil2_moist_panel, 1, 1)

        soil_layout.addWidget(soil1)
        soil_layout.addWidget(soil2)

        return soil_layout

    #ROS CONNECTION 

    def _connect_signals(self):
        self.ros.atmospheric_temp_signal.connect(
            lambda v: (self.atmos_temp_plot.add_data_point(v),
                       self.atmos_temp_panel.update_value(v))
        )
        self.ros.atmospheric_humidity_signal.connect(
            lambda v: (self.humidity_plot.add_data_point(v),
                       self.humidity_panel.update_value(v))
        )
        self.ros.gas_concentration_signal.connect(
            lambda v: (self.gas_plot.add_data_point(v),
                       self.gas_panel.update_value(v))
        )

        self.ros.soil1_temp_signal.connect(
            lambda v: (self.soil1_temp_plot.add_data_point(v),
                       self.soil1_temp_panel.update_value(v))
        )
        self.ros.soil1_moisture_signal.connect(
            lambda v: (self.soil1_moist_plot.add_data_point(v),
                       self.soil1_moist_panel.update_value(v))
        )

        self.ros.soil2_temp_signal.connect(
            lambda v: (self.soil2_temp_plot.add_data_point(v),
                       self.soil2_temp_panel.update_value(v))
        )
        self.ros.soil2_moisture_signal.connect(
            lambda v: (self.soil2_moist_plot.add_data_point(v),
                       self.soil2_moist_panel.update_value(v))
        )
