<p align="center">
    <img src="https://github.com/ReMi-HSBI/ssec/blob/main/docs/src/static/images/ssec_logo.svg?raw=true" alt="drawing" width="33%"/>
</p>

# ssec

[![ruff](https://img.shields.io/badge/ruff-⚡-261230.svg?style=flat-square)](https://docs.astral.sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-📝-2a6db2.svg?style=flat-square)](https://mypy-lang.org)
[![gitmoji](https://img.shields.io/badge/gitmoji-😜%20😍-FFDD67.svg?style=flat-square)](https://gitmoji.dev)

## Description

Python package for synchronous and asynchronous streaming of
[Server-Sent Events (SSE)](https://html.spec.whatwg.org/multipage/server-sent-events.html).
This library works with [httpx](https://github.com/encode/httpx)
to support synchronous as well as asynchronous workflows but is also
usable with other http frameworks ([see below](#aiohttp)).

## Installation

```sh
pip install ssec
```

# Usage

`sync`

```python
import logging
import ssec

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    for event in ssec.sse(
        "https://stream.wikimedia.org/v2/stream/recentchange"
    ):
        print(event)

main()
```

`async`

```python
import asyncio
import logging
import ssec

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async for event in ssec.sse_async(
        "https://stream.wikimedia.org/v2/stream/recentchange"
    ):
        print(event)

asyncio.run(main())
```

## Note

Although there are already some libraries on the subject
([aiohttp-sse-client](https://github.com/rtfol/aiohttp-sse-client),
[aiosseclient](https://github.com/ebraminio/aiosseclient)), these are
unfortunately not entirely correct. In example, both mentioned libraries
asynchronously iterate over the stream content via
`async for line in response.content`[^1][^2].
This internally calls [aiohttp](https://docs.aiohttp.org/en/stable)'s
[`readuntil`](https://docs.aiohttp.org/en/stable/streams.html#aiohttp.StreamReader.readuntil)
method with the default seperator `\n`, but the official specification
says:

> Lines must be separated by either a U+000D CARRIAGE RETURN U+000A LINE
> FEED (CRLF) character pair, a single U+000A LINE FEED (LF) character,
> or a single +000D CARRIAGE RETURN (CR) character.

Another point is the error handling, which is often not sufficient to analyze
the error or is entirely skipped.

### aiohttp

Although this library works with `httpx`, it is also possible to use it
with other http frameworks like `aiohttp` as long as they provide a
method to iterate over a byte-stream. Unfortunately, it is not possible
to handle reconnection then, so you will have to implement that by
yourself. An example could look like this:

```python
import asyncio
import logging

import aiohttp
import ssec

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    chunk_size = 1024
    connect_attempt = 1
    max_connect_attempts = 5
    config = ssec.SSEConfig(reconnect_timeout=3)
    async with aiohttp.ClientSession() as session:
        while True:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-store",
            }
            if config.last_event_id:
                headers["Last-Event-ID"] = config.last_event_id
            try:
                async with session.get(
                    "https://stream.wikimedia.org/v2/stream/recentchange",
                ) as response:
                    streamer = response.content.iter_chunked(chunk_size)
                    async for event in ssec.stream_async(streamer, config=config):
                        print(event)
            except aiohttp.ClientError:
                if connect_attempt >= max_connect_attempts:
                    logging.exception("Failed to connect!")
                    raise

                waiting_period = config.reconnect_timeout

                message = (
                    f"Failed to connect. "
                    f"Reconnect in {waiting_period} seconds "
                    f"[attempt {connect_attempt}/{max_connect_attempts}]."
                )
                logging.info(message)

                connect_attempt += 1
                await asyncio.sleep(waiting_period)

asyncio.run(main())
```

[^1]: [Code Reference](https://github.com/rtfol/aiohttp-sse-client/blob/e311075ac8b9b75d8b09512f8638f1dd03e2ef2b/aiohttp_sse_client/client.py#L157)  
[^2]: [Code Reference](https://github.com/ebraminio/aiosseclient/blob/375d597bcc3a7bf871b65913b366d515b300dc93/aiosseclient.py#L131)

## Miscellaneous

### Installation (Developer)

```sh
pip install ssec[dev]
```

### Documentation

Build the documentation by running the following command in the root
directory of the project:

```sh
sphinx-build -b html docs/src docs/build
```

> The command requires the [developers edition](#installation-developer)
> of `ssec`.

The documentation is then accessible via `docs/build/index.html`.

### Set up Visual Studio Code for Development

To edit the code base with [Visual Studio Code](https://code.visualstudio.com),
you should install the `@recommended` extensions. Other necessary
settings are already included in the `.vscode` directory and should be
enabled by default.

## Contributing

Contributing to `ssec` is highly appreciated, but comes with some
requirements:

1. **Type Hints**

    Write modern python code using
    [type annotations](https://peps.python.org/pep-0484/)
    to enable static analysis and potential runtime type checking.

2. **Documentation**

    Write quality documentation using
    [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
    docstring conventions.

3. **Linting**

   Lint your code with [ruff](https://github.com/charliermarsh/ruff) and
   [mypy](http://mypy-lang.org).

4. **Style**

    Format your code using [ruff](https://github.com/charliermarsh/ruff).

5. **Testing**

    Write tests for your code using [pytest](https://pypi.org/project/pytest).
