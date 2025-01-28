import unittest
from unittest.mock import AsyncMock, patch
import asyncio
import struct

# Import functions from the script
from sample import scan_and_connect, read_sensor_data, DEVICE_NAME


class TestSampleBLE(unittest.TestCase):
    @patch("sample.BleakScanner.discover")
    @patch("sample.BleakClient")
    def test_scan_and_connect(self, mock_bleak_client, mock_discover):
        """
        Test the scan_and_connect function for scanning and connecting to a BLE device.
        """
        # Mock a BLE device
        mock_device = AsyncMock()
        mock_device.name = DEVICE_NAME
        mock_device.address = "00:11:22:33:44:55"
        mock_discover.return_value = [mock_device]

        # Mock BLE client
        mock_client = AsyncMock()
        mock_bleak_client.return_value = mock_client

        # Run the function
        asyncio.run(scan_and_connect())

        # Verify that scanning was performed
        mock_discover.assert_called_once()

        # Verify connection to the correct BLE address
        mock_bleak_client.assert_called_with("00:11:22:33:44:55")

        # Verify that the client was connected and disconnected
        mock_client.__aenter__.assert_called_once()
        mock_client.__aexit__.assert_called_once()

    @patch("sample.BleakClient")
    def test_read_sensor_data(self, mock_bleak_client):
        """
        Test the read_sensor_data function for reading and decoding sensor data.
        """
        mock_client = AsyncMock()

        # Simulate characteristic data
        mock_client.read_gatt_char.side_effect = [
            struct.pack('<f', 1.23),  # ACCEL_X
            struct.pack('<f', 4.56),  # ACCEL_Y
            struct.pack('<f', 7.89),  # ACCEL_Z
            (123).to_bytes(4, byteorder="little"),  # Hall Signal
            (456).to_bytes(4, byteorder="little"),  # Gundata
        ]

        async def test_coroutine():
            # This will call read_sensor_data and verify its behavior
            await read_sensor_data(mock_client)

        # Run the coroutine with a timeout to avoid infinite loops
        with self.assertRaises(asyncio.TimeoutError):
            asyncio.run(asyncio.wait_for(test_coroutine(), timeout=0.01))

        # Verify the number of characteristic reads
        self.assertEqual(mock_client.read_gatt_char.call_count, 5)

    @patch("sample.BleakClient")
    def test_read_sensor_data_stop(self, mock_bleak_client):
        """
        Test that read_sensor_data stops gracefully when cancelled.
        """
        mock_client = AsyncMock()

        async def test_coroutine():
            task = asyncio.create_task(read_sensor_data(mock_client))
            await asyncio.sleep(0.01)  # Let it run briefly
            task.cancel()
            await task

        # Ensure the coroutine cancels without errors
        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(test_coroutine())


if __name__ == "__main__":
    unittest.main()
