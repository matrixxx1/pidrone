# sudo apt-get install python3-smbus

import smbus
import time

# I2C bus (usually bus 1 on Raspberry Pi)
bus = smbus.SMBus(1)

# TCA9548A I2C address (0x70 by default)
TCA9548A_ADDR = 0x70

# Function to select the channels on the TCA9548A
def select_channels(channels):
    # Channels is a bitmask to select which channels to activate
    # Example: 0x01 for channel 0, 0x03 for channels 0 and 1, etc.
    bus.write_byte(TCA9548A_ADDR, channels)

# Example function to communicate with an I2C device after selecting a channel
def communicate_with_device(channel):
    # Activate the desired channel on the TCA9548A
    select_channels(1 << channel)  # Use bit-shift to select the channel

    # Now communicate with the I2C device on the selected channel
    # Example: Reading from an I2C device with address 0x50 (adjust for your device)
    device_address = 0x50
    try:
        # Read a byte from the device (adjust register address as needed)
        data = bus.read_byte_data(device_address, 0x00)
        print(f"Data received from device: {data}")
    except Exception as e:
        print(f"Failed to communicate with device: {e}")

# Main function to test the setup
if __name__ == '__main__':
    while True:
        # Example: Communicate with devices on channel 0, 1, and 2
        for channel in range(8):  # TCA9548A has 8 channels (0-7)
            print(f"Communicating with channel {channel}...")
            communicate_with_device(channel)
            time.sleep(1)
