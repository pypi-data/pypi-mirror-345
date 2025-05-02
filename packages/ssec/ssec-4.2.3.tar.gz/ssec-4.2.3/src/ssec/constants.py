"""Module containing constant values."""

from __future__ import annotations

import codecs
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

#: The default timeout for connecting to a server, in seconds.
DEFAULT_CONNECT_TIMEOUT: Final[float] = 3.0

#: The default chunk size for streaming server-sent events, in bytes.
DEFAULT_CHUNK_SIZE: Final[int] = 1024

#: The default maximum number of attempts to connect to a server.
DEFAULT_MAX_CONNECT_ATTEMPTS: Final[int] = 3

#: The default time to wait before reconnecting to a server, in seconds.
DEFAULT_RECONNECT_TIMEOUT: Final[float] = 3.0

#: The default additional time to wait to ease a potentially overloaded
#: server, in seconds.
DEFAULT_BACKOFF_DELAY: Final[float] = 2.5

#: The incremental UTF-8 decoder with replacement error handling.
DECODER = codecs.getincrementaldecoder("utf-8")(errors="replace")

#: The delimiter used in server-sent events.
DELIMITER: Final[str] = ":"

#: The content type used in server-sent events.
SSE_CONTENT_TYPE: Final[str] = "text/event-stream"

#: The cache control used in server-sent events.
SSE_CACHE_CONTROL: Final[str] = "no-store"

#: The headers used in server-sent events.
SSE_HEADERS: Final[dict[str, str]] = {
    "Accept": SSE_CONTENT_TYPE,
    "Cache-Control": SSE_CACHE_CONTROL,
}
