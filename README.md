# Raspberry Pi Drone Control System

A Python-based drone control system for Raspberry Pi with safety features, sensor integration, and web interface control.

## Features

- Real-time flight control with safety monitoring
- Altitude control using VL53L0X distance sensor
- Orientation monitoring with ADXL345 accelerometer
- Camera feed and control
- Web interface for remote control
- Automatic emergency procedures
- Comprehensive logging system

## Hardware Requirements

- Raspberry Pi (3 or 4 recommended)
- VL53L0X Distance Sensor
- ADXL345 Accelerometer
- Drone frame with motors and ESCs
- Camera module
- Battery and power management system

## Installation

1. Clone this repository:
```bash
git clone https://github.com/matrixxx1/pidrone.git
cd pidrone
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Enable I2C and Camera interfaces on Raspberry Pi:
```bash
sudo raspi-config
# Navigate to Interface Options
# Enable I2C
# Enable Camera
```

4. Connect the hardware components:
- Connect VL53L0X to I2C pins (SDA: GPIO2, SCL: GPIO3)
- Connect ADXL345 to I2C pins
- Connect motors to appropriate GPIO pins (see motor.py for pin configuration)
- Connect and mount the camera module

## Usage

1. Start the drone controller:
```bash
python3 drone_controller.py
```

2. Access the web interface:
```
http://your_raspberry_pi_ip:8000
```

3. Before flying:
- Ensure all sensors are properly connected and initialized
- Check battery levels
- Verify motor connections
- Test emergency stop functionality

## Safety Features

- Automatic emergency landing on low battery
- Altitude limits
- Orientation monitoring
- Motor failure detection
- Emergency stop capability

## File Structure

- `drone_controller.py`: Main drone control logic
- `flight.py`: Flight movement controls
- `motor.py`: Motor control interface
- `camera.py`: Camera control and streaming
- `servos.py`: Servo motor control
- `adxl345.py`: Accelerometer interface
- `vl53l0x.py`: Distance sensor interface

## Contributing

Feel free to submit issues and pull requests.

## License

MIT License - feel free to use and modify as needed.

## Safety Warning

Always follow local regulations regarding drone operation. Test thoroughly in a safe environment before actual flight. Never operate the drone in unsafe conditions or near people/obstacles. 