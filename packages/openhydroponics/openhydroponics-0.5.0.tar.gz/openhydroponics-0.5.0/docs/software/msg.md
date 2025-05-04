# Messages

The messages payload are encoded using the [postcard](https://postcard.jamesmunns.com/) format and has a maximum of 64 bytes.

## Low level messages

Altough most functionality is available as a high level API on the nodes it is still possible to send messages manually.
To send a message to a node use the function [Node.send_msg()](openhydroponics.net.Node.send_msg).

Example:
```python
node = nm.get_node("01020304-3e00-4800-1650-4b5332393420")
# Switch endpoint 1 to 100%
msg = ActuatorOutput(endpoint_id=u8(1), value=f32(100.0))
node.send_msg(msg)
```

If the message is of the type `request` you can send and wait for the reply using [Node.send_and_wait()](openhydroponics.net.Node.send_and_wait).

Example:
```python
node = nm.get_node("01020304-3e00-4800-1650-4b5332393420")

# Request info about the endpoint 1 in the node
endpoint_info = await node.send_and_wait(
    Msg.EndpointInfoRequest(endpoint_id=u8(1))
)
```



## API reference

```{eval-rst}
.. automodule:: openhydroponics.net.msg
    :members:
    :undoc-members:
```
