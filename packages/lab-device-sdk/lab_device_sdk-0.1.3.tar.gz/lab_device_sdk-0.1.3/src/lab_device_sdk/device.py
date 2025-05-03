from typing import Any


class Device:
    """Base class for all device implementations.

    This class provides the core functionality for device management, including:
    - Device status management
    - Command execution
    - Parameter handling
    - Configuration management
    - Websocket notifications

    Attributes:
        device_type_id: Unique identifier for the device type
        manufacturer: Name of the device manufacturer
        model: Model name/number of the device
        version: Version of the device firmware/software
    """

    device_type_id: str = ""
    manufacturer: str = ""
    model: str = ""
    version: str = "0.0.0"

    def __init__(self, device_id: str, configuration: str | None = None):
        """Initialize a new device instance.

        Args:
            device_id: Unique identifier for this device instance
            configuration: Optional configuration string
        """
        super().__init__()
        self.device_id = device_id
        self.stop_requested = False
        self.configuration = configuration
        self.status = "Disconnected"
        self.status_details = ""
        self.result: Any = None
