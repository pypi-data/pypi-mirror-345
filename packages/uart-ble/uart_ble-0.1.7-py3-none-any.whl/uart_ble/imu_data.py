"""Store IMU data."""

import re
from dataclasses import dataclass
from typing import Optional

import numpy as np
from loguru import logger


@dataclass
class Vector3D:
    """A 3D vector with x, y, z components.

    :param x: X part (float)
    :param y: Y part (float)
    :param z: Z part (float)
    """

    x: float
    y: float
    z: float


@dataclass
class IMUData:
    """IMU data containing accelerometer, gyroscope, and magnetometer vectors.

    :param accel: Accelerometer data as a Vector3D
    :param gyro: Gyroscope data as a Vector3D
    :param mag: Magnetometer data as a Vector3D
    """

    dt: float
    accel: Vector3D
    gyro: Vector3D
    mag: Optional[Vector3D]


def parse_imu_data(line: Optional[str], with_mag: bool = False) -> IMUData:
    """Parse a line of data from the IMU.

    :param line: A comma-separated string of floats
    :param with_mag: Whether the line contains magnetometer data
    :return: A tuple of parsed floats (dt, ax, ay, az, gx, gy, gz)
    """
    if line is None:
        msg = "No data received from IMU."
        logger.error(msg)
        raise ValueError(msg)
    float_pattern = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
    line_as_floats = [float(match.group()) for match in float_pattern.finditer(line)]

    try:
        freq_hz, ax, ay, az, gx, gy, gz = line_as_floats[0:7]
        if freq_hz == 0.0:
            freq_hz = 50.0
        dt = 1.0 / freq_hz

        accel = Vector3D(ax, ay, az)
        gyro = Vector3D(gx, gy, gz)
        if with_mag:
            mx, my, mz = line_as_floats[7:10]
            mag = Vector3D(mx, my, mz)
        else:
            mag = None

        return IMUData(dt=dt, accel=accel, gyro=gyro, mag=mag)

    except ValueError:
        logger.error(f"Failed to parse IMU data: {line}")
        if with_mag:
            return IMUData(
                dt=np.nan,
                accel=Vector3D(np.nan, np.nan, np.nan),
                gyro=Vector3D(np.nan, np.nan, np.nan),
                mag=Vector3D(np.nan, np.nan, np.nan),
            )
        else:
            return IMUData(
                dt=np.nan,
                accel=Vector3D(np.nan, np.nan, np.nan),
                gyro=Vector3D(np.nan, np.nan, np.nan),
                mag=None,
            )
