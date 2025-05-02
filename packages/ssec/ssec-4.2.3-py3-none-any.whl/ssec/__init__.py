"""Yet another library for server-sent events."""

from .common import SSEConfig
from .event import Event
from .streamer import sse, sse_async, stream, stream_async

__all__ = ["Event", "SSEConfig", "sse", "sse_async", "stream", "stream_async"]
