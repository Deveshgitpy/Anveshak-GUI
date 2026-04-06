#  Anveshak IRC Dashboard

A real-time robotics control and monitoring GUI built using **ROS 2 + PySide6**, designed for the Anveshak rover system.  
This dashboard integrates sensor analytics, camera feeds, and actuator control into a single interface.

---

##  Overview

The system connects a dual ESP32 architecture with a ROS 2 backend:

- ESP32 #1 → Sensors + Servo Motors  
- ESP32 #2 → Pumps + Stepper Motor  

The GUI provides:
- 📊 Live atmospheric & soil data visualization  
- 🎥 Multi-camera streaming (UDP H264)  
- ⚙️ Real-time actuator control  
- 🔗 ROS 2 communication bridge  

---

##  Features

### 📊 Sensor Analysis Dashboard
- Real-time plots using `pyqtgraph`
- Atmospheric:
  - Temperature
  - Humidity
  - Gas concentration (MQ-4)
- Soil (2 samples):
  - Temperature (DS18B20)
  - Moisture

### 🎥 Camera Streaming
- Supports 3 independent camera feeds
- UDP-based low-latency H264 streaming
- Uses FFmpeg backend

### ⚙️ Actuation Control
- Stepper motor control (angle-based)
- Servo motor control (3 channels)
- Pump system:
  - Forward / Reverse / Stop
  - Emergency stop

### 🔗 ROS 2 Integration
- Subscribes to sensor topics
- Publishes actuator commands
- Handles feedback (echo confirmation)

---

## 🏗️ Project Structure

```
astrobiology_gui/
│
├── main.py                # Entry point (GUI + ROS2 threading)
├── ros_interface.py       # ROS2 communication layer
│
├── gui/
│   ├── main_window.py     # Main window + tabs
│   ├── tab_analysis.py    # Sensor visualization tab
│   └── tab_actuation.py   # Camera + actuator control
```

---

##  Tech Stack

- Frontend: PySide6 (Qt for Python)
- Backend: ROS 2 (rclpy)
- Visualization: pyqtgraph
- Streaming: FFmpeg (UDP H264)
- Hardware: ESP32 (micro-ROS)

---

##  Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Deveshgitpy/Anveshak-GUI.git
cd Anveshak-GUI
```

---

### 2️⃣ Install Dependencies
```bash
pip install PySide6 pyqtgraph numpy
```

Install ROS 2 (Humble recommended):  
https://docs.ros.org/en/humble/

---

### 3️⃣ Run the Application
```bash
python main.py
```

---

## 🔌 ROS Topics

### 📥 Subscribed Topics (Sensors)

| Topic | Description |
|------|------------|
| `/environment/temperature` | Atmospheric temperature |
| `/environment/gas` | Gas concentration |
| `/soil/sample1/temperature` | Soil 1 temperature |
| `/soil/sample1/moisture` | Soil 1 moisture |
| `/soil/sample2/temperature` | Soil 2 temperature |
| `/soil/sample2/moisture` | Soil 2 moisture |

---

### 📤 Published Topics (Actuators)

| Topic | Description |
|------|------------|
| `/stepper/angle` | Stepper control |
| `/servo1/angle` | Servo 1 |
| `/servo2/angle` | Servo 2 |
| `/servo3/angle` | Servo 3 |
| `/pump/cmd` | Pump control |

---

## 🎥 Camera Setup

The GUI expects UDP streams:

| Camera | Port |
|--------|------|
| Camera 1 | 5000 |
| Camera 2 | 5001 |
| Camera 3 | 5002 |

Example sender:
```bash
ffmpeg -f v4l2 -i /dev/video0 -f h264 udp://<IP>:5000
```

---

## 🧩 System Architecture

```
ESP32 #1 (Sensors + Servos)
        ↓
     ROS 2 Topics
        ↓
   ROS Interface (rclpy)
        ↓
   PySide6 GUI Dashboard
        ↑
ESP32 #2 (Pumps + Stepper)
```

---

##  Status Indicators

- 🔵 ROS Node Active  
- 🟢 ESP32 Connected  
- ⚪ Disconnected  
- ✅ System Fully Operational  

---

