
import asyncio
from bleak import BleakScanner, BleakClient

#pip install bleak



async def scan_devices():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device Name: {device.name}, Address: {device.address}")


async def main():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device Name: {device.name}, Address: {device.address}")

    target_address = "XX:XX:XX:XX:XX:XX"  # Replace with your device address
    
    try:
        async with BleakClient(target_address) as client:
            print(f"Connected: {client.is_connected}")
            # Perform operations with the connected device
            # Example: Read a characteristic
            # characteristic_uuid = "0000XXXX-0000-1000-8000-00805f9b34fb" # Replace with actual UUID
            # value = await client.read_gatt_char(characteristic_uuid)
            # print(f"Received value: {value}")
    except Exception as e:
        print(f"Error during communication: {e}")

if __name__ == "__main__":
    asyncio.run(scan_devices())
    #asyncio.run(main())