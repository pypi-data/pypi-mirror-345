from uuid import UUID

from dbus_fast.aio import MessageBus
from dbus_fast.constants import BusType

from openhydroponics.base import NodeManagerBase
from openhydroponics.dbus import Node

BUS_NAME = "com.openhydroponics"


class NodeManager(NodeManagerBase):

    def __init__(self, bus_type: BusType = BusType.SYSTEM):
        super().__init__()
        self._bus = None
        self._bus_type: BusType = bus_type
        self._initialized = False

    async def init(self):
        if self._initialized:
            return
        self._bus = await MessageBus(bus_type=self._bus_type).connect()

        introspection = await self._bus.introspect(
            BUS_NAME, "/com/openhydroponics/nodes"
        )

        proxy_object = self._bus.get_proxy_object(
            BUS_NAME, "/com/openhydroponics/nodes", introspection
        )

        self._interface = proxy_object.get_interface("com.openhydroponics.NodeManager")
        self._interface.on_node_added(self._add_node_from_path)

        for child in introspection.nodes:
            path = f"{introspection.name}/{child.name}"
            await self._add_node_from_path(path)
        self._initialized = True

    async def _add_node_from_path(self, object_path: str):
        introspection = await self._bus.introspect(BUS_NAME, object_path)
        proxy_object = self._bus.get_proxy_object(BUS_NAME, object_path, introspection)

        interface = proxy_object.get_interface("com.openhydroponics.NodeInterface")
        uuid = UUID(await interface.get_uuid())
        node = Node(uuid, proxy_object)
        await node.init(self._bus, introspection)
        self.add_node(uuid, node)
