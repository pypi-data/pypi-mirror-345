"""Common utility functions for UART communication."""

import asyncio
from typing import Optional

from uart_ble.definitions import ENCODING


class UARTHandler:
    """BLE handler that stores only the most recent line."""

    def __init__(self, encoding: str = ENCODING):
        self._buffer = b""
        self.latest_line = None
        self._new_data_event = asyncio.Event()
        self.encoding = encoding

    def handle_rx(self, _, data):
        """Handle received data."""
        self._buffer += data
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            self.latest_line = line.decode(self.encoding).strip()
            self._new_data_event.set()  # Signal that new data is available

    async def get_latest(self) -> Optional[str]:
        """Wait for and return the latest line of data."""
        await self._new_data_event.wait()
        self._new_data_event.clear()
        return self.latest_line
