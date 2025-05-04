from abc import ABC
import functools
import logging
from typing import Dict, Tuple, Union
from uuid import UUID

from openhydroponics.signal import signal
from openhydroponics.base.endpoint import Endpoint

_LOG = logging.getLogger(__name__)

class NodeBase(ABC):
    def __init__(self, uuid: UUID):
        self._endpoints = {}
        self._uuid = uuid
        self._number_of_endpoints = -1

    def add_endpoint(self, endpoint_no: int, instance: Endpoint):
        """
        Adds an endpoint to this node and sets up its value change tracking. This method is meant to be called
        by the node subclass when a new endpoint is added to the node.

        :param endpoint_no: A unique identifier for the endpoint within this node.
        :type endpoint_no: int
        :param instance: The endpoint instance to be added.
        :type instance: Endpoint
        """
        self._endpoints[endpoint_no] = instance
        instance.on_value_changed.connect(
            functools.partial(self.on_endpoint_value_changed, instance)
        )
        self.on_endpoint_added(instance)

    @property
    def endpoints(self) -> Dict[int, Endpoint]:
        """
        Returns the endpoints collection of this node.

        :returns: The collection of endpoint objects registered with this node.
        """
        return self._endpoints

    def get_endpoint(self, endpoint_id: int) -> Union[Endpoint, None]:
        """
        Retrieves an endpoint by its ID.

        :param endpoint_id: The ID of the endpoint to retrieve.
        :type endpoint_id: int

        :returns: The endpoint with the specified ID if it exists, None otherwise.
        """
        return self._endpoints.get(endpoint_id)

    def get_endpoint_value(self, endpoint_id: int) -> Tuple[float, int]:
        """
        Retrieves the value and scale of a specific endpoint by its ID.

        :param endpoint_id: The unique identifier of the endpoint to retrieve.

        :returns: A tuple containing the endpoint value (float or None if endpoint not found) and the endpoint scale
            (int or None if endpoint not found)
        """
        endpoint = self._endpoints.get(endpoint_id)
        if not endpoint:
            _LOG.warning(
                f"Endpoint with ID {endpoint_id} not found in node {self._uuid}"
            )
            return (0.0, 0)
        return endpoint.value, endpoint.scale

    @property
    def number_of_endpoints(self) -> int:
        """
        Returns the number of endpoints provided by this node.

        :returns: The number of endpoints that this node exposes.
        """
        return self._number_of_endpoints

    @number_of_endpoints.setter
    def number_of_endpoints(self, value: int):
        self._number_of_endpoints = value

    @signal
    def on_endpoint_added(self, endpoint: Endpoint):
        """
        Signal emitted when a new endpoint is added.

        :param endpoint: The endpoint object that has been added.
        :type endpoint: Endpoint
        """

    @signal
    def on_endpoint_value_changed(endpoint: Endpoint, value: float, scale: int):
        """
        Signal emitted when an endpoint's value changes.

        :param endpoint: The endpoint whose value has changed.
        :type endpoint: Endpoint
        :param value: The new value of the endpoint.
        :type value: float
        :param scale: The scaling factor or unit for the value.
        :type scale: int
        """
        pass

    @property
    def uuid(self) -> UUID:
        """
        Returns the UUID of the node.
        """
        return self._uuid

    def __iter__(self):
        return iter(self._endpoints.values())
