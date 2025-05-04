"""Message pipe."""

import asyncio
import time
from typing import Optional


class MsgPipe:
    """
    This is a pipe that can have multiple listeners.
    The main difference between this and a queue is:

    - If no clients are actively listening the messages are discarded.
      So no queue will build up if no one is interested in the message.
      This also means no maximum queue length is required since the pipe will only hold one item at a time. The producer
      will be blocked until all listeners has received the message.
    - Multiple listeners are allowed, and all listeners will get all messages.
    """

    def __init__(self):
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition()
        self._msg = None

    async def send(self, msg):
        """
        Send a message to through the pipe. All active listeners will get the message.
        If no listeners are currently listening on the pipe the message will silently be dropped.
        """

        # Use a lock to make sure all messages are sent to handlers
        # Else the listeners may miss one is messages are fed rapidly
        async with self._lock:
            async with self._condition:
                self._msg = msg
                self._condition.notify_all()
            # Make sure all listener are awake before releasing the lock
            await asyncio.sleep(0)

    async def wait_for_one(self, timeout: float):
        """Wait for next incoming message"""
        async with self._condition:
            await asyncio.wait_for(self._condition.wait(), timeout)
            return self._msg

    async def wait_for_messages(self, timeout: Optional[float]):
        """Wait for multiple incoming messages"""
        start = time.time()
        async with self._condition:
            while True:
                if timeout:
                    time_left = timeout - (time.time() - start)
                else:
                    time_left = None
                try:
                    await asyncio.wait_for(self._condition.wait(), time_left)
                    yield self._msg
                except asyncio.exceptions.TimeoutError:
                    # Timeout occured, we are done listening for messages
                    return
