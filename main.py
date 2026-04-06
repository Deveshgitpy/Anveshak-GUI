# main.py
"""
Main file 
ROS 2 Humble + PySide6 + micro-ROS (ESP32)
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import rclpy
from threading import Thread

from gui.main_window import MainWindow
from ros_interface import ROSInterface


def main():

    rclpy.init()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  
    apply_dark_theme(app)
    
    
    ros_interface = ROSInterface()
    
    window = MainWindow(ros_interface)
    window.show()
    
    ros_thread = Thread(target=rclpy.spin, args=(ros_interface,), daemon=True)
    ros_thread.start()
    
    exit_code = app.exec()
    
    ros_interface.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


def apply_dark_theme(app):
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: 'Segoe UI', 'Ubuntu', Arial, sans-serif;
            font-size: 10pt;
        }
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #3d3d3d;
            color: #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #0d47a1;
            color: white;
        }
        QGroupBox {
            border: 2px solid #0d47a1;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
            color: #64b5f6;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            background-color: #0d47a1;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QPushButton:pressed {
            background-color: #0a3d91;
        }
        QPushButton:disabled {
            background-color: #424242;
            color: #757575;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox {
            background-color: #3d3d3d;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 4px;
            color: #e0e0e0;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #64b5f6;
        }
        QLabel {
            color: #e0e0e0;
        }
    """)


if __name__ == '__main__':
    main()
