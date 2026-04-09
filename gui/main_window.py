# gui/main_window.py
"""
Main Application window 
Tab 1 -Sensor data
Tab 2 -Camera feeds and other actuation control 
"""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from gui.tab_analysis import AnalysisTab
from gui.tab_actuation import ActuationTab


class MainWindow(QMainWindow):
    """
    Main application window with tabbed interface
    Tab 1: Atmospheric & Soil Analysis (Sensors)
    Tab 2: Motion, Actuation & Vision (Actuators + Cameras)
    """
    
    def __init__(self, ros_interface):
        super().__init__()
        self.ros_interface = ros_interface
        
        self.setWindowTitle(' Mars Rover Astrobiology Module - IRC Competition')
        self.setMinimumSize(1600, 950)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #0d47a1;
                border-radius: 4px;
                background-color: #2b2b2b;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #e0e0e0;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 200px;
            }
            QTabBar::tab:selected {
                background-color: #0d47a1;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #1565c0;
            }
        """)
        main_layout.addWidget(self.tabs)
        
        self.analysis_tab = AnalysisTab(ros_interface)
        self.actuation_tab = ActuationTab(ros_interface)
        
        self.tabs.addTab(self.analysis_tab, "Atmospheric & Soil Analysis")
        self.tabs.addTab(self.actuation_tab, "Actuator")
        
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #64b5f6;
                font-size: 10pt;
                border-top: 2px solid #0d47a1;
            }
        """)
        self.statusBar().showMessage(' ROS 2 Node Active - Waiting for ESP32 data...')
        
        
        self._setup_status_monitoring()
    
    
    def _setup_status_monitoring(self):
        """Setup status bar updates based on ROS data"""
        
        self.ros_interface.atmospheric_temp_signal.connect(
            lambda _: self._update_status_first_data("ESP32 #1 Connected")
        )
        
        self.ros_interface.stepper_echo_signal.connect(
            lambda _: self._update_status_first_data("ESP32 #2 Connected")
        )
        
        self._esp32_1_connected = False
        self._esp32_2_connected = False
    
    
    def _update_status_first_data(self, device):
        """Update status when device first connects"""
        if "ESP32 #1" in device and not self._esp32_1_connected:
            self._esp32_1_connected = True
            self.statusBar().showMessage(' ESP32 #1 Active (Sensors) | Waiting for ESP32 #2...')
        
        if "ESP32 #2" in device and not self._esp32_2_connected:
            self._esp32_2_connected = True
            self.statusBar().showMessage(' ESP32 #2 Active (Actuators) | Waiting for ESP32 #1...')
        
        if self._esp32_1_connected and self._esp32_2_connected:
            self.statusBar().showMessage(' All Systems Operational - ESP32 #1 & #2 Online')


