"""Module containing the `stream` and `stream_async` functions."""

from __future__ import annotations

import asyncio
import http
import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
    from typing import Literal

    from .event import Event

import httpx

from .common import (
    SSEConfig,
    create_session,
    extract_lines,
    parse_events,
    validate_sse_response,
)
from .constants import (
    DECODER,
    DEFAULT_BACKOFF_DELAY,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_MAX_CONNECT_ATTEMPTS,
    DEFAULT_RECONNECT_TIMEOUT,
    SSE_HEADERS,
)

_logger = logging.getLogger("ssec")


def stream(
    streamer: Iterator[bytes],
    *,
    config: SSEConfig,
) -> Iterator[Event]:
    """Stream server-sent events (SSEs), synchronously.

    Low level function to synchronously stream server-sent events (SSEs) from
    a streamer object (Iterator[bytes]). This function is useful when you have
    a custom way of streaming data and want to parse the SSEs from it.
    Unfortunately, this function does not handle reconnections, so you will
    have to handle that yourself.

    Parameters
    ----------
    streamer
        The synchronous streamer object to read (byte-)data from.
    config
        A configuration object containing runtime settable values.

    Yields
    ------
    Event
        Server-sent event (SSE).
    """
    buffer = ""
    for chunk in streamer:
        buffer += DECODER.decode(chunk)
        lines, buffer = extract_lines(buffer)
        yield from parse_events(lines, config)


async def stream_async(
    streamer: AsyncIterator[bytes],
    *,
    config: SSEConfig,
) -> AsyncIterator[Event]:
    """Stream server-sent events (SSEs), asynchronously.

    Low level function to asynchronously stream server-sent events (SSEs)
    from a streamer object (AsyncIterator[bytes]). This function is
    useful when you have a custom way of streaming data and want to
    parse the SSEs from it. Unfortunately, this function does not handle
    reconnection, so you will have to handle that yourself.

    Parameters
    ----------
    streamer
        The asynchronous streamer object to read (byte-)data from.
    config
        A configuration object containing runtime settable values.

    Yields
    ------
    Event
        Server-sent event (SSE).
    """
    buffer = ""
    async for chunk in streamer:
        buffer += DECODER.decode(chunk)
        lines, buffer = extract_lines(buffer)
        for event in parse_events(lines, config):
            yield event


def sse(  # noqa: PLR0913
    url: str,
    *,
    session: httpx.Client | None = None,
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
    headers: dict[str, str] | None = None,
    method: Literal["GET", "POST"] = "GET",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    max_connect_attempts: int = DEFAULT_MAX_CONNECT_ATTEMPTS,
    reconnect_timeout: float = DEFAULT_RECONNECT_TIMEOUT,
    backoff_delay: float = DEFAULT_BACKOFF_DELAY,
) -> Iterator[Event]:
    """Stream server-sent events (SSEs), synchronously.

    High level function to synchronously stream server-sent events (SSEs)
    from a URL. This function handles reconnections and parsing of the
    SSEs.

    Parameters
    ----------
    url
        The URL to stream server-sent events from.
    session
        An optional HTTP session to use for the request.
    connect_timeout
        The timeout for connecting to the server, in seconds.
        Only used if `session` is `None`.
    headers
        Optional headers to include in the session.
        Only used if `session` is `None`.
    method
        The HTTP method to use for the request.
    chunk_size
        The size of the chunks to read from the response, in bytes.
    max_connect_attempts
        The maximum number of attempts to connect to the server.
    reconnect_timeout
        The time to wait before reconnecting to the server, in seconds.
    backoff_delay
        The additional time to wait to ease a potentially overloaded
        server, in seconds. This time is exponentiated by the number of
        connectioin attempts.

    Yields
    ------
    Event
        Server-sent event (SSE).

    Raises
    ------
    httpx.HTTPError
        If the maximum number of connection attempts is reached.
    """
    session_must_be_closed = False
    if session is None:
        session = create_session(
            httpx.Client,
            connect_timeout=connect_timeout,
            headers=headers,
        )
        session_must_be_closed = True

    config = SSEConfig(reconnect_timeout=reconnect_timeout, last_event_id="")
    try:
        connect_attempt = 0
        while True:
            headers = SSE_HEADERS.copy()
            if config.last_event_id:
                headers["Last-Event-ID"] = config.last_event_id

            try:
                with session.stream(method, url, headers=headers) as response:
                    validate_sse_response(response)

                    if response.status_code == http.HTTPStatus.NO_CONTENT:
                        _logger.info("Client was told to stop reconnecting.")
                        break

                    config.origin = str(response.url)

                    connect_attempt = 0
                    _logger.info("Connected to %r.", url)

                    streamer = response.iter_bytes(chunk_size=chunk_size)
                    yield from stream(streamer, config=config)

            except httpx.HTTPError:
                if connect_attempt >= max_connect_attempts:
                    _logger.exception("Failed to connect to %r", url)
                    raise

                waiting_period = config.reconnect_timeout
                if connect_attempt > 0:
                    waiting_period += backoff_delay**connect_attempt

                message = (
                    f"Failed to connect to {url!r}. "
                    f"Reconnect in {waiting_period} seconds "
                    f"[attempt {connect_attempt + 1}/{max_connect_attempts}]."
                )
                _logger.info(message)

                connect_attempt += 1
                time.sleep(waiting_period)
    finally:
        if session_must_be_closed:
            session.close()


async def sse_async(  # noqa: PLR0913
    url: str,
    *,
    session: httpx.AsyncClient | None = None,
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
    headers: dict[str, str] | None = None,
    method: Literal["GET", "POST"] = "GET",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    max_connect_attempts: int = DEFAULT_MAX_CONNECT_ATTEMPTS,
    reconnect_timeout: float = DEFAULT_RECONNECT_TIMEOUT,
    backoff_delay: float = DEFAULT_BACKOFF_DELAY,
) -> AsyncIterator[Event]:
    """Stream server-sent events (SSEs), asynchronously.

    High level function to asynchronously stream server-sent events (SSEs)
    from a URL. This function handles reconnections and parsing of the
    SSEs.

    Parameters
    ----------
    url
        The URL to stream server-sent events from.
    session
        An optional HTTP session to use for the request.
    connect_timeout
        The timeout for connecting to the server, in seconds.
        Only used if `session` is `None`.
    headers
        Optional headers to include in the session.
        Only used if `session` is `None`.
    method
        The HTTP method to use for the request.
    chunk_size
        The size of the chunks to read from the response, in bytes.
    max_connect_attempts
        The maximum number of attempts to connect to the server.
    reconnect_timeout
        The time to wait before reconnecting to the server, in seconds.
    backoff_delay
        The additional time to wait to ease a potentially overloaded
        server, in seconds. This time is exponentiated by the number of
        connectioin attempts.

    Yields
    ------
    Event
        Server-sent event (SSE).

    Raises
    ------
    httpx.HTTPError
        If the maximum number of connection attempts is reached.
    """
    session_must_be_closed = False
    if session is None:
        session = create_session(
            httpx.AsyncClient,
            connect_timeout=connect_timeout,
            headers=headers,
        )
        session_must_be_closed = True

    config = SSEConfig(reconnect_timeout=reconnect_timeout, last_event_id="")
    try:
        connect_attempt = 0
        while True:
            headers = SSE_HEADERS.copy()
            if config.last_event_id:
                headers["Last-Event-ID"] = config.last_event_id

            try:
                async with session.stream(
                    method,
                    url,
                    headers=headers,
                ) as response:
                    validate_sse_response(response)

                    if response.status_code == http.HTTPStatus.NO_CONTENT:
                        _logger.info("Client was told to stop reconnecting.")
                        break

                    config.origin = str(response.url)

                    connect_attempt = 0
                    _logger.info("Connected to %r", url)

                    streamer = response.aiter_bytes(chunk_size=chunk_size)
                    async for event in stream_async(streamer, config=config):
                        yield event

            except httpx.HTTPError:
                if connect_attempt >= max_connect_attempts:
                    _logger.exception("Failed to connect %r", url)
                    raise

                waiting_period = config.reconnect_timeout
                if connect_attempt > 0:
                    waiting_period += backoff_delay**connect_attempt

                message = (
                    f"Failed to connect to {url!r}. "
                    f"Reconnect in {waiting_period} seconds "
                    f"[attempt {connect_attempt + 1}/{max_connect_attempts}]."
                )
                _logger.info(message)

                connect_attempt += 1
                await asyncio.sleep(waiting_period)
    finally:
        if session_must_be_closed:
            await session.aclose()
