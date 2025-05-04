import asyncio
import logging
from typing import Any, TypeVar
from uuid import UUID
import can
from plum import dispatch

from openhydroponics.base import NodeManagerBase
from openhydroponics.net.node import Node

from .phyinterface import CanPhyIface
import openhydroponics.net.msg as Msg
from openhydroponics.net.msg import ArbitrationId

_LOG = logging.getLogger(__name__)

NodeType = TypeVar("Node")


class NodeManager(NodeManagerBase):
    def __init__(self, phy_iface: CanPhyIface = None):
        super().__init__()
        self._loop = None
        self._node_id = 1
        self._last_node_id = 1

        self._phy_iface = phy_iface or CanPhyIface()
        self._phy_iface.add_listener(self._on_message_received)

    async def init(self):
        self._loop = asyncio.get_running_loop()
        self._phy_iface.set_event_loop(self._loop)
        async def on_node_added(node: Node):
            await node.interview()

        self.on_node_added.connect(on_node_added)

    @property
    def node_id(self) -> int:
        """
        Get the node id the manager is using on the CANbus.
        """
        return self._node_id

    def _on_message_received(self, msg: can.Message):
        arb = ArbitrationId.decode(msg.arbitration_id)
        msg = Msg.Msg.decode(arb, msg.data)
        if msg:
            self._handle_msg(arb, msg)
        else:
            _LOG.warning("Failed to decode message. Arb: %s", arb)

    @dispatch
    def _handle_msg(self, arb: ArbitrationId, msg: Msg.Heartbeat):
        node = self.get_node_by_id(arb.src)
        if node:
            # All good
            return
        node = Node(
            arb.src, UUID("00000000-00000000-00000000-00000000"), self, self._phy_iface
        )
        node.send_rtr(Msg.NodeInfo)

    @dispatch
    def _handle_msg(self, arb: ArbitrationId, msg: Msg.HeartbeatWithIdRequest):
        uuid = UUID(bytes=bytes(msg.uuid))
        if arb.src != 0:
            return
        node = self.get_node(uuid)
        if not node:
            node_id = self._last_node_id + 1
            _LOG.info(f"New node {uuid} found. Giving node id {node_id} to it")
            self._last_node_id = node_id
            node = Node(node_id, uuid, self, self._phy_iface)
            self.add_node(node_id, node)

        msg = Msg.IdSet(uuid=msg.uuid)
        node.send_msg(msg)

    @dispatch
    def _handle_msg(self, arb: ArbitrationId, msg: Msg.NodeInfo):
        uuid = UUID(bytes=bytes(msg.uuid))
        node = self.get_node_by_id(arb.src)
        if node:
            return
        _LOG.info(f"Node {uuid} detected.")
        node = Node(arb.src, uuid, self, self._phy_iface)
        node._number_of_endpoints = msg.number_of_endpoints
        self.add_node(arb.src, node)

    @dispatch
    def _handle_msg(self, arb: ArbitrationId, msg: Msg.SensorReading):
        node = self.get_node_by_id(arb.src)
        if not node:
            return
        endpoint = node.get_endpoint(msg.endpoint_id)
        if not endpoint:
            return
        endpoint.handle_sensor_reading(msg)

    @dispatch
    def _handle_msg(self, arb: ArbitrationId, msg: Any):
        pass
