

/*
sudo apt update
sudo apt install python3-pip
pip3 install adafruit-circuitpython-pca9685
*/

import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create PCA9685 object
pca = PCA9685(i2c)
pca.frequency = 50  # Set frequency to 50Hz for servos

# Create a servo object on channel 0
servo0 = servo.Servo(pca.channels[0])

# Move servo to 0 degrees
servo0.angle = 0  

# Move servo to 90 degrees
servo0.angle = 90  

# Move servo to 180 degrees
servo0.angle = 180  

# Cleanup
pca.deinit()