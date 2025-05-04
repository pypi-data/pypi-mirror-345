import asyncio
import errno
import logging
import traceback
from typing import AsyncIterator, Callable, Awaitable, List, Optional
import can
import serial.tools.list_ports

from openhydroponics.msg_pipe import MsgPipe

_LOG = logging.getLogger(__name__)

# Suppress info and debug log messages from can module
logging.getLogger("can.interfaces.socketcan.socketcan").setLevel(logging.ERROR)

class Listener(can.Listener):
    def __init__(self, phy_iface):
        self._phy_iface = phy_iface

    def on_message_received(self, msg):
        self._phy_iface.on_message_received(msg)

    def on_error(self, exc: Exception) -> None:
        if not isinstance(exc, can.CanOperationError):
            _LOG.error(f"Unknown error: {exc}")
            return
        if exc.error_code == errno.ENETDOWN:
            _LOG.error("Network is down, reconnect bus...")
            self._phy_iface.reconnect()


class CanPhyIface:
    MsgCallback = Callable[[bytes], Awaitable[None]]

    def __init__(self):
        self._loop = None
        self._bus = None
        self._listeners: List[CanPhyIface.MsgCallback] = []
        self._msg_pipe = MsgPipe()
        self._init_kwargs = {
            "interface": "socketcan",
            "channel": "can0",
            "bitrate": 1000000,
            "receive_own_messages": False,
            "fd": True,
        }

        self._listener = Listener(self)
        self._bus = can.Bus(**self._init_kwargs)
        self._notifier = can.Notifier(self._bus, [self._listener])

    def add_listener(self, callback: MsgCallback) -> None:
        """Add a listener callback that will be called on for every message received"""
        self._listeners.append(callback)

    def reconnect(self):
        """Reconnect the bus"""
        async def do_it():
            if self._bus:
                self._notifier.stop()
                self._bus.shutdown()
                await asyncio.sleep(1)
            self._bus = can.Bus(**self._init_kwargs)
            self._notifier = can.Notifier(self._bus, [self._listener])

        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(do_it(), self._loop)
        else:
            _LOG.warning("No loop running, cannot reconnect to bus")

    def on_message_received(self, msg: can.Message) -> None:
        # LOG.warn(f"Received message: {msg}")
        for listener in self._listeners:
            try:
                listener(msg)
            except Exception as exception:  # pylint: disable=broad-except
                _LOG.exception(exception)
                traceback.print_exception(exception)
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._msg_pipe.send(msg), self._loop)

    def send_message(self, arb: int, msg: bytes, is_remote=False) -> None:
        """Send a message over the CAN bus"""
        try:
            if is_remote:
                self._bus.send(
                    can.Message(arbitration_id=arb, data=b"", is_fd=True, is_remote_frame=False)
                )
            else:
                msg = CanPhyIface.pad_data(msg)
                self._bus.send(can.Message(arbitration_id=arb, data=msg, is_fd=True))
        except:
            LOG.error("Error sending message!!!!!!!!!!")


    def set_event_loop(self, loop):
        self._loop = loop

    async def wait_for(self, arb: int, timeout: Optional[float] = 2.0) -> can.Message:
        """Listen on incoming can frames and wait for a specific arbitration id"""
        async for msg in self.wait_for_many(arb, timeout):
            return msg

    async def wait_for_many(
        self, arb: int, timeout: Optional[float] = 2.0
    ) -> AsyncIterator[can.Message]:
        """Listen on incoming can frames and wait for multiple frames with a specific arbitration id"""

        async for msg in self._msg_pipe.wait_for_messages(timeout):
            if msg.arbitration_id == arb:
                yield msg
        raise asyncio.exceptions.TimeoutError()

    @staticmethod
    def get_slcan_channel():
        SUPPORTED_SLCAN_VIDS = [
            0xAD50,  # CANABLE
            0x16D0,  # CANABLE 2.0
            0x1E3,  # KORLAN_USB2CAN
        ]
        for port in serial.tools.list_ports.comports():
            if port.vid in SUPPORTED_SLCAN_VIDS:
                return port.device
        LOG.error("No supported slcan device found")
        return None

    @staticmethod
    def pad_data(data: bytes) -> bytes:
        """Pad data to valid CAN FD frame length"""
        if len(data) <= 8:
            return data
        for fdlen in (12, 16, 20, 24, 32, 48, 64):
            if fdlen >= len(data):
                return data.ljust(fdlen, b"\x00")
        raise ValueError("Data too long for CAN FD frame")
