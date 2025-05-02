"""A utility function to start a BLE listener in a separate thread."""

import asyncio
import threading

from loguru import logger
from py_imu.madgwick import Madgwick
from py_imu.quaternion import Vector3D

from uart_ble import BLEDevice, parse_imu_data
from uart_ble.definitions import FILTER_GAIN, FREQUENCY
from uart_ble.live_data import LiveData


def start_imu_thread(
    device_name: str, live_data: LiveData, filter_gain: float = FILTER_GAIN
) -> None:
    """Start a BLE listener that runs asynchronously in a separate daemon thread."""

    async def run() -> None:
        imu_device = BLEDevice(device_name)
        if not await imu_device.find_device():
            return

        imu_handler = await imu_device.connect_and_subscribe()

        madgwick = Madgwick(frequency=FREQUENCY, gain=filter_gain)

        while True:
            try:
                line = await imu_handler.get_latest()

                imu_data = parse_imu_data(line)
                gyro = Vector3D(imu_data.gyro.x, imu_data.gyro.y, imu_data.gyro.z)
                accel = Vector3D(imu_data.accel.x, imu_data.accel.y, imu_data.accel.z)
                q = madgwick.update(gyr=gyro, acc=accel, dt=imu_data.dt)

                # Update live buffers
                live_data.accel.add_data(
                    imu_data.accel.x, imu_data.accel.y, imu_data.accel.z
                )
                live_data.gyro.add_data(
                    imu_data.gyro.x, imu_data.gyro.y, imu_data.gyro.z
                )
                live_data.quat = [float(q.w), float(q.x), float(q.y), float(q.z)]

            except Exception as e:
                logger.error(f"Error in BLE listener: {e}, retrying...")
                await asyncio.sleep(0.1)

    def run_in_thread():
        asyncio.run(run())

    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()
