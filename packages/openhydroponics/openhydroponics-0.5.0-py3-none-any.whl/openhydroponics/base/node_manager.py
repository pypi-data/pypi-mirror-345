from abc import ABC, abstractmethod
import asyncio
import functools
import time
from typing import Any, AsyncGenerator, TypeVar, Union
from uuid import UUID

from openhydroponics.base.endpoint import Endpoint
from openhydroponics.signal import signal

NodeType = TypeVar("Node")


class NodeManagerBase(ABC):

    def __init__(self):
        self._nodes = {}

    def add_node(self, node_id: Any, node: NodeType):
        """
        Add a new node to the manager. This method is only meant to be called by a subclass implementing the NodeManager
        interface.

        :param node_id: The unique identifier for the node. What this is depends on the implementation.
        :type node_id: Any
        :param node: The node instance to be added
        :type node: Node

        :raises: ValueError: If a node with the given ID already exists
        """
        if node_id in self._nodes:
            raise ValueError(f"Node with ID {node_id} already exists")
        node.on_endpoint_value_changed.connect(
            functools.partial(self.on_node_endpoint_value_changed, node)
        )
        self._nodes[node_id] = node
        self.on_node_added(node)

    def get_node(self, uuid: Union[str, UUID]) -> Union[NodeType, None]:
        """
        Retrieves a node by its UUID.

        :param: uuid (Union[str, UUID]): The UUID of the node to retrieve, either as a string or a UUID object.

        :returns: Union[NodeType, None]: The node with the specified UUID if found, None otherwise.
        """
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        for node in self._nodes.values():
            if node.uuid == uuid:
                return node
        return None

    def get_node_by_id(self, node_id: Any) -> Union[NodeType, None]:
        """
        Retrieves a node by its internal ID. This is typically used for internal management
        and is not meant to be used by external code.
        This method is only meant to be called by a subclass implementing the NodeManager
        interface.

        :param node_id: The internal ID of the node to retrieve.
        :type node_id: Any

        :returns: Union[NodeType, None]: The node with the given ID if found, or None if not found.
        """
        return self._nodes.get(node_id, None)

    @abstractmethod
    async def init(self):
        """
        Initialize the node manager.

        This asynchronous method performs initialization tasks for the node manager.
        It should be called once after the node manager instance is created.

        :returns: None
        """
        pass

    @signal
    def on_node_added(self, node: NodeType):
        """
        Signal emitted when a node is added to the manager.

        :param node: The node that was added.
        """

    @signal
    def on_node_endpoint_value_changed(
        self, node: NodeType, endpoint: Endpoint, value: float, scale: int
    ):
        """
        Signal emitted when the value of a node's endpoint changes.

        :param node: The identifier of the node where the change occurred.
        :param endpoint: The specific endpoint of the node that changed.
        :param value: The new value of the endpoint.
        :param scale: The scale or unit associated with the value.

        """

    async def request_node(
        self, uuid: Union[str, UUID], timeout_s: float = 2.0
    ) -> Union[NodeType, None]:
        """
        Attempts to retrieve a node with the specified UUID, if the node is not found it will wait for the node to be
        available for a specified timeout period.
        This method is useful for ensuring that the node is available before proceeding with further operations.

        :param uuid: The UUID of the node to retrieve, either as a string or UUID object.
        :type uuid: str | UUID
        :param timeout_s: The maximum time in seconds to wait for the node to be available. Defaults to 2.0 seconds.
        :type timeout_s: float

        :returns: Node | None: The node with the specified UUID if found within the timeout period, None otherwise.
        """
        timeout = time.time() + timeout_s
        while time.time() < timeout:
            node = self.get_node(uuid)
            if node:
                return node
            await asyncio.sleep(0.1)
        return None

    def __iter__(self):
        return iter(self._nodes.values())

    def __aiter__(self):
        return aiter(self.nodes())

    async def nodes(self) -> AsyncGenerator[NodeType, None]:
        """
        Asynchronously yields all registered nodes.

        If no nodes are currently available, this method will wait for 1 second
        to allow for potential heartbeats from nodes to be received before continuing.

        :yields: Each node registered with the manager.
        """
        if not self._nodes:
            # No nodes found. Sleep to wait for heartbeats
            await asyncio.sleep(1)
        for node in self._nodes.values():
            yield node
