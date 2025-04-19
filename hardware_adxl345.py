#adxl

import smbus
 

bus = smbus.SMBus(1)  # I2C bus number
ADXL345_ADDR = 0x53  # ADXL345 address
DATAX0_REG = 0x00  # X-axis low register
DATAX1_REG = 0x01  # X-axis high register

def read_accel_data():
  x_low = bus.read_byte_data(ADXL345_ADDR, DATAX0_REG)
  x_high = bus.read_byte_data(ADXL345_ADDR, DATAX1_REG)
  x_raw = (x_high << 8) | x_low
  y_low = bus.read_byte_data(ADXL345_ADDR, DATAX0_REG + 2)
  y_high = bus.read_byte_data(ADXL345_ADDR, DATAX1_REG + 2)
  y_raw = (y_high << 8) | y_low
  z_low = bus.read_byte_data(ADXL345_ADDR, DATAX0_REG + 4)
  z_high = bus.read_byte_data(ADXL345_ADDR, DATAX1_REG + 4)
  z_raw = (z_high << 8) | z_low
  # Convert raw data to g-forces (adjust based on sensor range)
  x_g = (x_raw / 256.0) 
  y_g = (y_raw / 256.0) 
  z_g = (z_raw / 256.0) 
  #return x_g, y_g, z_g
  return x_raw, y_raw, z_raw



    
    x, y, z = read_accel_data()
    print("X:", x, "Y:", y, "Z:", z)
    