"""Sample doc string."""

# Bluetooth Low Energy values
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # from device → host
RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # from host → device
BLE_TIMEOUT = 5.0

# Madgwick filter
FILTER_GAIN = 0.033
FREQUENCY = 50.0

# UART encoding
ENCODING = "utf-8"

BUFFER_SIZE = 500
