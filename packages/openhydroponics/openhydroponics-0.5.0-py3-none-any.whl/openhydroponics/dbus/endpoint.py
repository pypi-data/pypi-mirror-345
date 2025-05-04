import logging

from dbus_fast import Variant, DBusError

from openhydroponics.base import endpoint as EndpointBase
from openhydroponics.lib.dbus import dict_to_variant, unpack_variant
from openhydroponics.service import endpoint as Service

_LOG = logging.getLogger(__name__)


class Endpoint:

    async def get_config(self, config: int):
        try:
            return unpack_variant(await self.dbus_interface.call_get_config(config))
        except DBusError as e:
            raise Exception(e.text)

    async def set_config(self, config) -> bool:
        try:
            return await self.dbus_interface.call_set_config(dict_to_variant(config))
        except DBusError as e:
            raise Exception(e.text)

    async def init(self):
        pass


class InputEndpoint(Endpoint):
    async def init(self):
        await super().init()
        value, scale = await self.dbus_interface.get_value()
        self._value = value
        self._scale = scale
        self.properties_interface.on_properties_changed(self.on_properties_changed)

    def on_properties_changed(
        self,
        interface_name: str,
        changed_properties: dict[str, Variant],
        invalidated_properties: dict[str, Variant],
    ):
        for changed, variant in changed_properties.items():
            if changed == "Value":
                value, scale = variant.value
                self._value = value
                self._scale = scale
                self.on_value_changed(value, scale)


class VariableOutputEndpoint(EndpointBase.VariableOutputEndpoint):
    async def set(self, value: float):
        await self.dbus_interface.call_set(value)


MAPPING = {
    Service.InputEndpointInterface.DBUS_INTERFACE: EndpointBase.InputEndpoint,
    Service.TemperatureEndpointInterface.DBUS_INTERFACE: EndpointBase.TemperatureEndpoint,
    Service.HumidityEndpointInterface.DBUS_INTERFACE: EndpointBase.HumidityEndpoint,
    Service.ECEndpointInterface.DBUS_INTERFACE: EndpointBase.ECEndpoint,
    Service.PHEndpointInterface.DBUS_INTERFACE: EndpointBase.PHEndpoint,
    Service.OutputEndpointInterface.DBUS_INTERFACE: EndpointBase.OutputEndpoint,
    Service.VariableOutputEndpointInterface.DBUS_INTERFACE: VariableOutputEndpoint,
}


async def get_endpoint_class(proxy_object, node) -> EndpointBase.Endpoint:
    interface = proxy_object.get_interface(
        "com.openhydroponics.EndpointMetaDataInterface"
    )
    endpoint_id = await interface.get_endpoint_id()

    endpoint_interface_name = await interface.get_endpoint_interface()
    endpoint_interface = proxy_object.get_interface(endpoint_interface_name)
    properties_interface = proxy_object.get_interface("org.freedesktop.DBus.Properties")

    cls = MAPPING.get(endpoint_interface_name, EndpointBase.Endpoint)
    if cls.ENDPOINT_CLASS == EndpointBase.EndpointClass.Input:
        new_cls = type(cls.__name__, (InputEndpoint, cls), {})
    else:
        new_cls = type(cls.__name__, (Endpoint, cls), {})
    obj = new_cls(node, endpoint_id)
    obj.dbus_interface = endpoint_interface
    obj.properties_interface = properties_interface
    await obj.init()
    return obj
