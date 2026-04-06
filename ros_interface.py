# ros_interface.py
"""
ROS 2 Bridge Layer - Integrated with 2x ESP32 Setup
ESP32 #1: DHT11, Soil Moisture (2x), DS18B20 (2x), MQ-4, Servos (3x)
ESP32 #2: Pumps (4x), Stepper Motor
"""

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from PySide6.QtCore import QObject, Signal

from std_msgs.msg import Float32, Int32, Int32MultiArray
from sensor_msgs.msg import Image
import numpy as np


class ROSInterface(Node, QObject):
        
    # ESP32 #1 - Atmospheric signals
    atmospheric_temp_signal = Signal(float)      
    atmospheric_humidity_signal = Signal(float)  
    atmospheric_pressure_signal = Signal(float)  
    gas_concentration_signal = Signal(float)     
    soil1_temp_signal = Signal(float)
    soil1_moisture_signal = Signal(float)
    soil2_temp_signal = Signal(float)
    soil2_moisture_signal = Signal(float)
    
    # ESP32 #2 - Stepper feedback
    stepper_echo_signal = Signal(float)
    pump_echo_signal = Signal(list)
    
    # Camera signals (from Ubuntu/Orin/Xavier)
    camera1_signal = Signal(np.ndarray)
    camera2_signal = Signal(np.ndarray)
    camera3_signal = Signal(np.ndarray)
    
    
    def __init__(self):
        Node.__init__(self, 'astrobiology_gui_node')
        QObject.__init__(self)
        
        # QoS profiles
        self.sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self._setup_subscribers()
        self._setup_publishers()
        
        self.get_logger().info(' GUI Node initialized')
        self.get_logger().info(' Waiting for ESP32 #1 (sensors + servos)...')
        self.get_logger().info(' Waiting for ESP32 #2 (pumps + stepper)...')
    
    
    def _setup_subscribers(self):
        """Initialize all ROS 2 subscribers"""
        
        # ========== ESP32 #1 TOPICS ==========
        
        # Atmospheric temperature (DHT11)
        self.create_subscription(
            Float32,
            '/environment/temperature',
            self._atmospheric_temp_callback,
            self.sensor_qos
        )
        
        # Gas concentration (MQ-4)
        self.create_subscription(
            Float32,
            '/environment/gas',
            self._gas_callback,
            self.sensor_qos
        )
        
        # Soil Sample 1 (DS18B20 )
        self.create_subscription(
            Float32,
            '/soil/sample1/temperature',
            self._soil1_temp_callback,
            self.sensor_qos
        )
        
        self.create_subscription(
            Float32,
            '/soil/sample1/moisture',
            self._soil1_moisture_callback,
            self.sensor_qos
        )
        
        # Soil Sample 2 (DS18B20 )
        self.create_subscription(
            Float32,
            '/soil/sample2/temperature',
            self._soil2_temp_callback,
            self.sensor_qos
        )
        
        self.create_subscription(
            Float32,
            '/soil/sample2/moisture',
            self._soil2_moisture_callback,
            self.sensor_qos
        )
        
        # ========== ESP32 #2 FEEDBACK TOPICS ==========
        
        # Stepper echo (confirmation)
        self.create_subscription(
            Float32,
            '/stepper/angle_echo',
            self._stepper_echo_callback,
            self.reliable_qos
        )
        
        # Pump echo (confirmation)
        self.create_subscription(
            Int32MultiArray,
            '/pump/cmd_echo',
            self._pump_echo_callback,
            self.reliable_qos
        )
        
        # ========== CAMERA TOPICS (from Orin/Xavier/Ubuntu) ==========
        # Leaving for now to add camera later (not sure which cameras and how they will be used on rover)
        
        
        # self.create_subscription(
        #     Image,
        #     '/camera1/image_raw',
        #     self._camera1_callback,
        #     self.sensor_qos
        # )
        # 
        # self.create_subscription(
        #     Image,
        #     '/camera2/image_raw',
        #     self._camera2_callback,
        #     self.sensor_qos
        # )
        # 
        # self.create_subscription(
        #     Image,
        #     '/camera3/image_raw',
        #     self._camera3_callback,
        #     self.sensor_qos
        # )
    
    
    def _setup_publishers(self):
        
        
        # ========== ESP32 #2 COMMAND TOPICS ==========
        
        # Stepper motor (ESP32 #2)
        self.stepper_pub = self.create_publisher(
            Float32,
            '/stepper/angle',
            self.reliable_qos
        )
        
        # ========== ESP32 #1 SERVO TOPICS ==========
        
        # Servo 1 (ESP32 #1)
        self.servo1_pub = self.create_publisher(
            Int32,
            '/servo1/angle',
            self.reliable_qos
        )
        
        # Servo 2 (ESP32 #1)
        self.servo2_pub = self.create_publisher(
            Int32,
            '/servo2/angle',
            self.reliable_qos
        )
        
        # Servo 3 (will be adding later :D)
        self.servo3_pub = self.create_publisher(
            Int32,
            '/servo3/angle',
            self.reliable_qos
        )
        
        # ========== ESP32 #2 PUMP TOPIC ==========
        
        # Pumps (ESP32 #2)
        self.pump_pub = self.create_publisher(
            Int32MultiArray,
            '/pump/cmd',
            self.reliable_qos
        )
    
    
    # ========== SUBSCRIBER CALLBACKS ==========
    
    def _atmospheric_temp_callback(self, msg: Float32):
        """DHT11 temperature callback (ESP32 #1)"""
        try:
            self.atmospheric_temp_signal.emit(msg.data)
        except Exception as e:
            self.get_logger().error(f'Atmospheric temp callback error: {e}')
    
    
    def _gas_callback(self, msg: Float32):
        """MQ-4 gas concentration callback (ESP32 #1)"""
        try:
            self.gas_concentration_signal.emit(msg.data)
        except Exception as e:
            self.get_logger().error(f'Gas callback error: {e}')
    
    
    def _soil1_temp_callback(self, msg: Float32):
        """DS18B20 soil sample 1 temperature (ESP32 #1)"""
        try:
            self.soil1_temp_signal.emit(msg.data)
        except Exception as e:
            self.get_logger().error(f'Soil1 temp callback error: {e}')
    
    
    def _soil1_moisture_callback(self, msg: Float32):
        """Soil sample 1 moisture sensor (ESP32 #1)"""
        try:
            self.soil1_moisture_signal.emit(msg.data)
        except Exception as e:
            self.get_logger().error(f'Soil1 moisture callback error: {e}')
    
    
    def _soil2_temp_callback(self, msg: Float32):
        """DS18B20 soil sample 2 temperature (ESP32 #1)"""
        try:
            self.soil2_temp_signal.emit(msg.data)
        except Exception as e:
            self.get_logger().error(f'Soil2 temp callback error: {e}')
    
    
    def _soil2_moisture_callback(self, msg: Float32):
        """Soil sample 2 moisture sensor (ESP32 #1)"""
        try:
            self.soil2_moisture_signal.emit(msg.data)
        except Exception as e:
            self.get_logger().error(f'Soil2 moisture callback error: {e}')
    
    
    def _stepper_echo_callback(self, msg: Float32):
        """Stepper command echo (ESP32 #2 confirmation)"""
        try:
            self.stepper_echo_signal.emit(msg.data)
            self.get_logger().info(f'✅ Stepper confirmed: {msg.data}°')
        except Exception as e:
            self.get_logger().error(f'Stepper echo error: {e}')
    
    
    def _pump_echo_callback(self, msg: Int32MultiArray):
        """Pump command echo (ESP32 #2 confirmation)"""
        try:
            pump_states = list(msg.data)
            self.pump_echo_signal.emit(pump_states)
            self.get_logger().info(f'✅ Pumps confirmed: {pump_states}')
        except Exception as e:
            self.get_logger().error(f'Pump echo error: {e}')
    
    
    def _camera1_callback(self, msg: Image):
        """Camera 1 image callback (from Orin/Xavier/Ubuntu)"""
        try:
            # Convert ROS Image to numpy array
            img = np.frombuffer(msg.data, dtype=np.uint8)
            img = img.reshape((msg.height, msg.width, 3))
            self.camera1_signal.emit(img)
        except Exception as e:
            self.get_logger().error(f'Camera 1 callback error: {e}')
    
    
    def _camera2_callback(self, msg: Image):
        """Camera 2 image callback"""
        try:
            img = np.frombuffer(msg.data, dtype=np.uint8)
            img = img.reshape((msg.height, msg.width, 3))
            self.camera2_signal.emit(img)
        except Exception as e:
            self.get_logger().error(f'Camera 2 callback error: {e}')
    
    
    def _camera3_callback(self, msg: Image):
        """Camera 3 image callback"""
        try:
            img = np.frombuffer(msg.data, dtype=np.uint8)
            img = img.reshape((msg.height, msg.width, 3))
            self.camera3_signal.emit(img)
        except Exception as e:
            self.get_logger().error(f'Camera 3 callback error: {e}')
    
    
    # ========== PUBLISHER METHODS ==========
    
    def publish_stepper_angle(self, angle: float):
        """
        Publish stepper motor angle command (ESP32 #2)
        Args:
            angle: Target angle in degrees (positive or negative)
        """
        try:
            msg = Float32()
            msg.data = float(angle)
            self.stepper_pub.publish(msg)
            self.get_logger().info(f'📤 Stepper command: {angle}°')
        except Exception as e:
            self.get_logger().error(f'Failed to publish stepper angle: {e}')
    
    
    def publish_servo_angle(self, servo_id: int, angle: int):
        """
        Publish servo angle command (ESP32 #1)
        Args:
            servo_id: Servo number (1, 2, or 3)
            angle: Target angle 0-180 degrees
        """
        try:
            if not 0 <= angle <= 180:
                self.get_logger().warn(f'Servo angle {angle} out of range [0-180]')
                return
            
            msg = Int32()
            msg.data = int(angle)
            
            if servo_id == 1:
                self.servo1_pub.publish(msg)
            elif servo_id == 2:
                self.servo2_pub.publish(msg)
            elif servo_id == 3:
                self.servo3_pub.publish(msg)
            else:
                self.get_logger().error(f'Invalid servo ID: {servo_id}')
                return
            
            self.get_logger().info(f'📤 Servo {servo_id} command: {angle}°')
        except Exception as e:
            self.get_logger().error(f'Failed to publish servo angle: {e}')
    
    
    def publish_pump_commands(self, pump_states: list):
        """
        Publish pump control commands (ESP32 #2)
        Args:
            pump_states: List of 4 integers [pump1, pump2, pump3, pump4]
                         1 = forward, -1 = reverse, 0 = stop
        """
        try:
            if len(pump_states) != 4:
                self.get_logger().error('Pump states must be list of 4 integers')
                return
            
            msg = Int32MultiArray()
            msg.data = [int(s) for s in pump_states]
            self.pump_pub.publish(msg)
            self.get_logger().info(f'📤 Pump commands: {pump_states}')
        except Exception as e:
            self.get_logger().error(f'Failed to publish pump commands: {e}')
