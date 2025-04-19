



# wiring
#GY-530 (VL53L0X) Pin	Raspberry Pi Pin
#VCC	3.3V (Pin 1)
#GND	GND (Pin 6)
#SDA	SDA (Pin 3) (GPIO 2)
#SCL	SCL (Pin 5) (GPIO 3)

#Enabling on pi
# sudo raspi-config
# Interfacing Options → I2C → Enable

#install libraries
# sudo apt update
# sudo apt install -y python3-pip i2c-tools

# sudo apt update
# sudo apt install python3-smbus python3-dev
# pip3 install adafruit-circuitpython-vl53l0x

# if above fails use this:
# pip install adafruit-circuitpython-vl53l0x
# sudo apt install adafruit-circuitpython-vl53l0x
# sudo pip3 install --break-system-packages adafruit-circuitpython-vl53l0x

#check if device attached to bus1
# sudo i2cdetect -y 1
#check if device attached to bus2
# sudo i2cdetect -y 2


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
