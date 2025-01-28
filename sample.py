import asyncio
from bleak import BleakScanner, BleakClient
import struct  # For unpacking binary data

# Replace with the name of your BLE device
DEVICE_NAME = "SensorData"

# UUIDs of the service and characteristics
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
ACCEL_X_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
ACCEL_Y_UUID = "19B10002-E8F2-537E-4F6C-D104768A1214"
ACCEL_Z_UUID = "19B10003-E8F2-537E-4F6C-D104768A1214"
HALL_SIGNAL_UUID = "19B10004-E8F2-537E-4F6C-D104768A1214"
GUNDATA_UUID = "19B10005-E8F2-537E-4F6C-D104768A1214"

async def read_sensor_data(client):
    """
    Continuously read and print sensor data from the BLE device.
    """
    try:
        while True:
            # Read the accelerometer and hall sensor data
            x_bytes = await client.read_gatt_char(ACCEL_X_UUID)
            y_bytes = await client.read_gatt_char(ACCEL_Y_UUID)
            z_bytes = await client.read_gatt_char(ACCEL_Z_UUID)
            hall_signal_bytes = await client.read_gatt_char(HALL_SIGNAL_UUID)
            gundata_bytes = await client.read_gatt_char(GUNDATA_UUID)

            # Decode the binary data to float and integer values
            x = struct.unpack('<f', x_bytes)[0]  
            y = struct.unpack('<f', y_bytes)[0]
            z = struct.unpack('<f', z_bytes)[0]
            hall_signal = int.from_bytes(hall_signal_bytes, byteorder='little')
            gundata = int.from_bytes(gundata_bytes, byteorder='little')

            # Print the decoded values
            print(f"Accelerometer Data: X = {x:.2f}, Y = {y:.2f}, Z = {z:.2f}")
            print(f"Hall Signal: {hall_signal}")
            print(f"Gundata: {gundata}")
            print("-" * 30)  # Separator for readability

            # Add a small delay to avoid overwhelming the BLE connection
            await asyncio.sleep(0.0001)  # 1000 ms

    except asyncio.CancelledError:
        print("Stopped reading sensor data.")

async def scan_and_connect():
    """
    Scan for the BLE device, connect to it, and start reading sensor data.
    """
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    target_device = None
    for device in devices:
        if device.name == DEVICE_NAME:
            print(f"Found target device: {device.name} - {device.address}")
            target_device = device
            break

    if not target_device:
        print(f"Device with name '{DEVICE_NAME}' not found.")
        return

    print(f"Connecting to {target_device.address}...")
    async with BleakClient(target_device.address) as client:
        print(f"Connected to {target_device.address}")

        # Start reading sensor data in real-time
        await read_sensor_data(client)

if __name__ == "__main__":
    try:
        asyncio.run(scan_and_connect())
    except KeyboardInterrupt:
        print("Program stopped by user.")