"""Module containing common utilities."""

from __future__ import annotations

import dataclasses
import http
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

import httpx

from .constants import DEFAULT_RECONNECT_TIMEOUT, DELIMITER, SSE_CONTENT_TYPE
from .event import Event


def create_session[T: (httpx.Client, httpx.AsyncClient)](
    session_class: type[T],
    connect_timeout: float,
    headers: dict[str, str] | None = None,
) -> T:
    """Create an `httpx` session with a custom connect timeout.

    Parameters
    ----------
    session_class
        The `httpx` session class to create.
    connect_timeout
        The connect timeout, in seconds.
    headers
        Optional headers to include in the session.

    Returns
    -------
    T
        An `httpx` session with a custom connect timeout.
    """
    timeout = httpx.Timeout(
        connect=connect_timeout,
        read=None,
        write=None,
        pool=None,
    )
    return session_class(timeout=timeout, headers=headers)


@dataclasses.dataclass(
    repr=False,
    eq=False,
    kw_only=True,
    slots=True,
    weakref_slot=True,
)
class SSEConfig:
    """Mutable configuration for runtime settable values.

    Attributes
    ----------
    reconnect_timeout
        The time to wait before reconnecting to a server, in seconds.
    last_event_id
        The last event ID received from the server.
    origin
        The origin of the server.
    """

    reconnect_timeout: float = DEFAULT_RECONNECT_TIMEOUT
    last_event_id: str = ""
    origin: str | None = None


def validate_sse_response(response: httpx.Response) -> None:
    """Validate a (SSE-)response.

    Parameters
    ----------
    response
        The response to check for errors.

    Raises
    ------
    ValueError
        If the response is invalid.
    """
    if response.status_code != http.HTTPStatus.OK:
        message = f"Unexpected status code: {response.status_code}!"
        raise ValueError(message)

    if SSE_CONTENT_TYPE not in response.headers.get("content-type"):
        message = f"Invalid content type: expected {SSE_CONTENT_TYPE}!"
        raise ValueError(message)


def extract_lines(buffer: str) -> tuple[list[str], str]:
    """Extract all lines from a string buffer.

    Parameters
    ----------
    buffer
        The buffer potentially containing lines.

    Returns
    -------
    tuple[list[str], str]
        A tuple containing extracted lines of the buffer and the buffers
        remnant.
    """
    lines: list[str] = []
    for line in buffer.splitlines(keepends=True):
        if line.endswith(("\r\n", "\n", "\r")):
            # Using '\r\n' as the parameter to rstrip means that it will strip
            # out any trailing combination of '\r' or '\n'.
            lines.append(line.rstrip("\r\n"))
            buffer = buffer.removeprefix(line)
    return lines, buffer


def parse_events(lines: list[str], config: SSEConfig) -> Iterator[Event]:  # noqa: C901
    """Parse SSEs from a list of lines.

    Parameters
    ----------
    lines
        A list of lines to parse SSEs from.
    config
        A configuration object containing runtime settable values.

    Yields
    ------
    Event
        Parsed event.
    """
    event_type = ""
    event_data = ""
    for line in lines:
        # If the line is empty (a blank line) -> Dispatch the event.
        if not line:
            if not event_type:
                event_type = "message"

            # Remove last character of data if it is a U+000A LINE FEED (LF)
            # character.
            event_data = event_data.rstrip("\n")

            yield Event(
                event_type,
                event_data,
                origin=config.origin,
                last_event_id=config.last_event_id,
            )

            # Reset buffers.
            event_type = ""
            event_data = ""

            continue

        # If the line starts with a U+003A COLON character (:) -> Ignore.
        if line.startswith(DELIMITER):
            continue

        name, _, value = line.partition(DELIMITER)

        # Space after the colon is ignored if present.
        value = value.removeprefix(" ")

        match name:
            case "event":
                # If the field name is "event"
                # -> Set the event type buffer to field value.
                event_type = value
            case "data":
                # If the field name is "data"
                # -> Append the field value to the data buffer, then
                # append a single U+000A LINE FEED (LF) character to the
                # data buffer.
                event_data += f"{value}\n"
            case "id":
                # If the field name is "id"
                # -> If the field value does not contain U+0000 NULL,
                # then set the last event ID buffer to the field value.
                # Otherwise, ignore the field. The specification is not
                # clear here. In an example it says: "If the "id" field
                # has no value, this will reset the last event ID to the
                # empty string".
                if "\u0000" not in value:
                    config.last_event_id = value
            case "retry":
                # If the field name is "retry"
                # -> If the field value consists of only ASCII digits,
                # then interpret the field value as an integer in base
                # ten, and set the event stream's reconnection time to
                # that integer. Otherwise, ignore the field.
                if value.isdigit():
                    config.reconnect_timeout = float(value)
            case _:
                # Otherwise -> The field is ignored.
                continue
