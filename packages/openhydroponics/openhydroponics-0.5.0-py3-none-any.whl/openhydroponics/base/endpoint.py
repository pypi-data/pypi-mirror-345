from enum import IntEnum
import logging
from typing import Any

from openhydroponics.signal import signal

_LOG = logging.getLogger(__name__)


class EndpointClass(IntEnum):
    NotSupported = 0
    Input = 1
    Output = 2


class EndpointInputClass(IntEnum):
    NotSupported = 0
    Temperature = 1
    Humidity = 2
    EC = 3
    PH = 4


class EndpointOutputClass(IntEnum):
    NotSupported = 0
    Variable = 1
    Binary = 2


class Endpoint:
    ENDPOINT_CLASS = EndpointClass.NotSupported

    def __init__(self, node, endpoint_id: int):
        self._node = node
        self._endpoint_id: int = endpoint_id

    @property
    def endpoint_id(self) -> int:
        """
        Get the endpoint number for this endpoint.

        :returns: The endpoint's identifier that distinguishes it from other endpoints in this node.
        """
        return self._endpoint_id

    async def interview(self):
        """
        Conducts an interactive interview process for endpoint configuration.

        This asynchronous method prompts for and collects necessary information
        to set up or configure the endpoint.
        """
        pass

    @property
    def node(self):
        """
        Returns the node associated with this endpoint.
        """
        return self._node

    @signal()
    def on_value_changed(self, value: float, scale: int):
        """
        Signal emitted when a sensor reading is received.

        :param value: The value of the sensor reading.
        :param scale: The scale of the sensor reading.
        """

    async def get_config(self, config: int) -> dict[str, Any]:
        """
        Get configuration parameters for this endpoint.

        This method retrieves the current configuration settings for the endpoint.

        :param config: The configuration number to retrieve.
        :returns: The value of the requested configuration parameter.
        """
        pass

    async def set_config(self, config: dict[str, Any]) -> bool:
        """
        Set configuration parameters for this endpoint.

        This method updates the endpoint's configuration with the provided dictionary of settings.

        :param config: A dictionary containing configuration parameters where keys are parameter names and values are the
            parameter values. This can include settings like thresholds, calibration values, or other endpoint-specific
            configurations.
        :returns: True if the configuration was successfully set, False otherwise.
        """
        pass


class InputEndpoint(Endpoint):
    ENDPOINT_CLASS = EndpointClass.Input
    INPUT_CLASS = EndpointInputClass.NotSupported

    def __init__(self, node, endpoint_id):
        super().__init__(node, endpoint_id)
        self._value = None
        self._scale = None

    def handle_sensor_reading(self, msg):
        self._value = msg.value
        self._scale = msg.scale
        self.on_value_changed(msg.value, msg.scale)

    @property
    def value(self):
        return self._value

    @property
    def scale(self):
        return self._scale


class TemperatureEndpoint(InputEndpoint):
    INPUT_CLASS = EndpointInputClass.Temperature


class HumidityEndpoint(InputEndpoint):
    INPUT_CLASS = EndpointInputClass.Humidity


class OutputEndpoint(Endpoint):
    ENDPOINT_CLASS = EndpointClass.Output
    OUTPUT_CLASS = EndpointOutputClass.NotSupported


class VariableOutputEndpoint(OutputEndpoint):
    OUTPUT_CLASS = EndpointOutputClass.Variable


class ECConfigWriteType(IntEnum):
    LOW = 0
    HIGH = 1
    GAIN = 2
    RAW = 3


class ECConfigReadType(IntEnum):
    CALIBRATION = 0
    RAW = 1


class ECEndpoint(InputEndpoint):
    INPUT_CLASS = EndpointInputClass.EC


class PHConfigType(IntEnum):
    LOW = 0
    HIGH = 1
    MID = 2  # Not all frontends support this


class PHEndpoint(InputEndpoint):
    INPUT_CLASS = EndpointInputClass.PH
