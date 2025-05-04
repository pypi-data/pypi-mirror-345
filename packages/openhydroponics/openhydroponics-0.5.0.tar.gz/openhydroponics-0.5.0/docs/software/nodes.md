# Nodes

The Node Manager is a central component that manages all the nodes in your hydroponic system.

Nodes are individual components that perform specific tasks within the hydroponic system. They can have sensors, actuators, or controllers.

All applications need a [NodeManager](base.node_manager.NodeManagerBase)

There are currently two implementations of the [NodeManager](base.node_manager.NodeManagerBase) and their APIs are interoperable. The [NodeManager](net.NodeManager) in the `openhydroponics.net` modules offer direct access to the CANbus and can be used to send low level messages to the network. The other [NodeManager](dbus.NodeManager) in the `openhydroponics.dbus` module and offers a faster and more lightweight implementation. Instead of raw communication it connects to the openhydroponicd daemon over d-bus. [dbus.NodeManager](dbus.NodeManager) is the preffered implementation to use in third party applications.

Example:

```python
import asyncio

from openhydroponics.dbus import NodeManager


async def main():
    nm = NodeManager()
    await nm.init()
    async for node in nm:
        print(f"Node {node.uuid}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

```

Getting a reference to a node object use the function [NodeManager.get_node()](openhydroponics.base.NodeManagerBase.get_node)
or [NodeManager.request_node()](openhydroponics.base.NodeManagerBase.request_node).

## Endpoints

All nodes have one or several endpoints. A node that supports temperature and humidity may have two endpoints, one for each
sensor. If a node supports multiple variants of the same type of sensor or actuators each individual sensor/actuator will have
its own endpoint. Example: A node with 3 pump outlets will have three endpoints, one for each pump.

## API reference

```{eval-rst}
.. autoclass:: openhydroponics.base.NodeManagerBase
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: openhydroponics.base.NodeBase
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: openhydroponics.base.Endpoint
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: openhydroponics.net.NodeManager
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: openhydroponics.net.Node
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: openhydroponics.dbus.NodeManager
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: openhydroponics.dbus.Node
    :members:
    :undoc-members:
    :inherited-members:
```
