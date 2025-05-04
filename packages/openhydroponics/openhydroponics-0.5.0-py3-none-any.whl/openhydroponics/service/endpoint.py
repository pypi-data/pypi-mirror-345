from dbus_fast.service import ServiceInterface, method, dbus_property
from dbus_fast import DBusError, ErrorType, PropertyAccess

from openhydroponics.base.endpoint import (
    Endpoint,
    EndpointClass,
    EndpointInputClass,
    EndpointOutputClass,
    OutputEndpoint,
)
from openhydroponics.lib.dbus import dict_to_variant, unpack_variant


class EndpointInterface(ServiceInterface):
    DBUS_INTERFACE = "com.openhydroponics.EndpointInterface"

    def __init__(self, endpoint: Endpoint):
        super().__init__(self.DBUS_INTERFACE)
        self._endpoint = endpoint

    @method()
    async def GetConfig(self, config: "y") -> "a{sv}":
        try:
            config = await self._endpoint.get_config(config)
            return dict_to_variant(config)
        except Exception as e:
            raise DBusError(ErrorType.SERVICE_ERROR, str(e))

    @method()
    async def SetConfig(self, config: "a{sv}") -> "b":
        try:
            # Unpack variants
            return await self._endpoint.set_config(unpack_variant(config))
        except Exception as e:
            raise DBusError(ErrorType.SERVICE_ERROR, str(e))


class InputEndpointInterface(EndpointInterface):
    DBUS_INTERFACE = "com.openhydroponics.endpoint.InputInterface"

    def __init__(self, endpoint: Endpoint):
        super().__init__(endpoint)
        self._endpoint.on_value_changed.connect(self._on_value_changed)

    @dbus_property(access=PropertyAccess.READ)
    def Value(self) -> "(dy)":
        if not self._endpoint.value:
            return [0.0, 0]
        return [self._endpoint.value, self._endpoint.scale]

    def _on_value_changed(self, value: float, scale: int):
        self.emit_properties_changed({"Value": [value, scale]})


class TemperatureEndpointInterface(InputEndpointInterface):
    DBUS_INTERFACE = "com.openhydroponics.endpoint.TemperatureInterface"


class HumidityEndpointInterface(InputEndpointInterface):
    DBUS_INTERFACE = "com.openhydroponics.endpoint.HumidityInterface"


class ECEndpointInterface(InputEndpointInterface):
    DBUS_INTERFACE = "com.openhydroponics.endpoint.ECInterface"


class PHEndpointInterface(InputEndpointInterface):
    DBUS_INTERFACE = "com.openhydroponics.endpoint.PHInterface"


class OutputEndpointInterface(EndpointInterface):
    DBUS_INTERFACE = "com.openhydroponics.endpoint.OutputInterface"


class VariableOutputEndpointInterface(OutputEndpointInterface):
    DBUS_INTERFACE = "com.openhydroponics.endpoint.VariableOutputInterface"

    @method()
    async def Set(self, value: "d"):
        await self._endpoint.set(value)


def wrap_input_endpoint(endpoint: Endpoint) -> InputEndpointInterface:
    if endpoint.INPUT_CLASS == EndpointInputClass.Temperature:
        return TemperatureEndpointInterface(endpoint)
    if endpoint.INPUT_CLASS == EndpointInputClass.Humidity:
        return HumidityEndpointInterface(endpoint)
    if endpoint.INPUT_CLASS == EndpointInputClass.EC:
        return ECEndpointInterface(endpoint)
    if endpoint.INPUT_CLASS == EndpointInputClass.PH:
        return PHEndpointInterface(endpoint)
    return InputEndpointInterface(endpoint)


def wrap_output_endpoint(endpoint: OutputEndpoint) -> OutputEndpointInterface:
    if endpoint.OUTPUT_CLASS == EndpointOutputClass.Variable:
        return VariableOutputEndpointInterface(endpoint)
    return OutputEndpointInterface(endpoint)


def wrap_endpoint(endpoint: Endpoint) -> EndpointInterface:
    if endpoint.ENDPOINT_CLASS == EndpointClass.Input:
        return wrap_input_endpoint(endpoint)
    if endpoint.ENDPOINT_CLASS == EndpointClass.Output:
        return wrap_output_endpoint(endpoint)
    return EndpointInterface(endpoint)
