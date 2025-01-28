import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "SensorData"  # Replace with your BLE device name
CHAR_UUIDS = {
    "x": "19B10001-E8F2-537E-4F6C-D104768A1214",
    "y": "19B10002-E8F2-537E-4F6C-D104768A1214",
    "z": "19B10003-E8F2-537E-4F6C-D104768A1214",
    "hall_signal": "19B10004-E8F2-537E-4F6C-D104768A1214",
    "gundata": "19B10005-E8F2-537E-4F6C-D104768A1214",
}


async def handle_notification(characteristic, data):
    """
    Callback function to handle notifications from the BLE device.
    """
    if characteristic in CHAR_UUIDS.values():
        print(f"Notification from {characteristic}: {data}")
        try:
            # Convert the data to float or int based on the characteristic
            if "19B10004" in characteristic or "19B10005" in characteristic:
                value = int.from_bytes(data, byteorder="little")
                print(f"Value: {value}")
            else:
                value = float.fromhex(data.hex())
                print(f"Value: {value}")
        except Exception as e:
            print(f"Failed to parse data: {e}")


async def main():
    # Scan for the device
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    target_device = next((d for d in devices if d.name == DEVICE_NAME), None)

    if not target_device:
        print(f"Device '{DEVICE_NAME}' not found.")
        return

    print(f"Found device '{DEVICE_NAME}' at address: {target_device.address}")

    # Connect to the device
    async with BleakClient(target_device.address) as client:
        print(f"Connected to {DEVICE_NAME}")

        # Subscribe to notifications for each characteristic
        for name, uuid in CHAR_UUIDS.items():
            print(f"Subscribing to {name} ({uuid})")
            await client.start_notify(uuid, lambda c, d: handle_notification(c, d))

        print("Listening for notifications. Press Ctrl+C to exit.")
        try:
            while True:
                await asyncio.sleep(1)  # Keep the loop running
        except KeyboardInterrupt:
            print("Stopping notifications...")

        # Unsubscribe from notifications before exiting
        for uuid in CHAR_UUIDS.values():
            await client.stop_notify(uuid)


if __name__ == "__main__":
    asyncio.run(main())
