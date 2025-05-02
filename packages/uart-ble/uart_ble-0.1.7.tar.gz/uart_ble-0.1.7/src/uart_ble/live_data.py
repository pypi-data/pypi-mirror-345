"""Class for storing live sensor data and quaternion."""

from collections import deque

from uart_ble.definitions import BUFFER_SIZE


class SensorData:
    """Stores IMU sensor data for one axis (x, y, z)."""

    def __init__(self, buffer_size: int = BUFFER_SIZE) -> None:
        """Initialize the sensor data for one axis."""
        self.x: deque[float] = deque(maxlen=buffer_size)
        self.y: deque[float] = deque(maxlen=buffer_size)
        self.z: deque[float] = deque(maxlen=buffer_size)

    def add_data(self, x: float, y: float, z: float) -> None:
        """Add new sensor data to the buffers."""
        self.x.append(x)
        self.y.append(y)
        self.z.append(z)


class LiveData:
    """Stores live IMU data for accelerometer, gyroscope, and quaternion."""

    def __init__(self, buffer_size: int) -> None:
        """Initialize the live data with sensor buffers and quaternion."""
        self.accel = SensorData(buffer_size)
        self.gyro = SensorData(buffer_size)
        self.quat: list[float] = [1.0, 0.0, 0.0, 0.0]  # Default quaternion
