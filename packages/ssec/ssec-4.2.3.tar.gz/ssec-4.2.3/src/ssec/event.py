"""Module containing the `Event` (data-)class."""

import dataclasses


@dataclasses.dataclass
class Event:
    """A server-sent event (SSE).

    Attributes
    ----------
    type
        The type of the event.
    data
        The data of the event.
    """

    type: str = "message"
    data: str | None = None

    origin: str | None = None
    last_event_id: str | None = None
