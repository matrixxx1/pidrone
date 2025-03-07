

/*

sudo apt update
sudo apt install python3-smbus python3-dev
pip3 install adafruit-circuitpython-vl53l0x


*/


import time
import board
import busio
import adafruit_vl53l0x

# Set up I2C connection
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the VL53L0X sensor
sensor = adafruit_vl53l0x.VL53L0X(i2c)

# Optionally, configure sensor settings (e.g., timing budget, etc.)
sensor.measurement_timing_budget = 200000  # 200 ms
sensor.integration_time = 50  # 50 ms

print("VL53L0X Sensor initialized")

# Loop to take distance measurements
try:
    while True:
        # Read the distance in mm
        distance = sensor.range
        print(f"Distance: {distance} mm")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
