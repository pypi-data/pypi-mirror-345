import asyncio
from functools import update_wrapper
import logging
import traceback

_LOG = logging.getLogger(__name__)


class SignalInstance:
    def __init__(self):
        self._fn = None
        self._listeners = []

    def connect(self, callback):
        if asyncio.iscoroutinefunction(callback):
            self._listeners.append((callback, asyncio.get_event_loop()))
        else:
            self._listeners.append((callback, None))

    def __call__(self, *args, **kwargs):
        for listener, loop in self._listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    asyncio.run_coroutine_threadsafe(listener(*args, **kwargs), loop)
                else:
                    listener(*args, **kwargs)
            except Exception as e:
                _LOG.error(f"Error in signal listener: {e}")
                traceback.print_exc()


class SignalType:
    def __new__(cls, fn=None):
        instance = super().__new__(cls)
        if fn:
            return update_wrapper(instance, fn)
        return instance

    def __init__(self, fn=None):
        self._fn = fn

    def __get__(self, instance, _base):
        if not hasattr(instance, "_signals"):
            setattr(instance, "_signals", {})
        name = self._fn.__name__
        signal = instance._signals.get(name)
        if not signal:
            signal = SignalInstance()
            instance._signals[name] = signal
        return signal

    def __call__(self, fn):
        self._fn = fn
        return update_wrapper(self, fn)


signal = SignalType
