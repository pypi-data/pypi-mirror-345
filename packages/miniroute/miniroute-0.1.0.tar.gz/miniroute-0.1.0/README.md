# miniroute

**miniroute** is a minimal HTTP routing framework based on Python’s built-in `http.server`, designed for lightweight local servers and IPC tooling.

This module is made for users familiar with the `http.server` module, with which it shares the same qualities and flaws.

## WARNING

I've made this module when I encountered a situation where http protocol was the
simplest way to solve a LOCAL Inter-Process-Communication issue, and I did NOT
want to add a heavy dependency (like Flask or FastAPI) to the program I was coding.
I found out that the standard http module would do the job, but was a pain to integrate.

As the officiel http documentation state : **This is NOT a server to be used in PRODUCTION.
This module doesn't ADD NEW security issues to the http module, but it doesn't SOLVE them either.**

## http.server

To understand what the "handler" object passed to your route actually is, you will need to get familiar with how the http.server module operate.
**You can find its documentation [here](https://docs.python.org/3/library/http.server.html#http.server.HTTPServer)**

## Features

- Simple route declaration using decorators
- Pure standard library
- No magic, no dependencies
- Good for local-only HTTP endpoints

## Installation

```bash
pip install miniroute
```

## Usage

```python
from miniroute import Miniroute
import json

app = Miniroute()

@app.router.get("/hello")
def hello(handler):
    body = json.dumps({"message": "Hello, world!"}).encode()
    headers = [("Content-Type", "application/json")]
    return 200, headers, body

@app.router.post("/echo")
def echo(handler):
    length = int(handler.headers.get("Content-Length", 0))
    data = handler.rfile.read(length)
    return 200, [("Content-Type", "application/json")], data

if __name__ == "__main__":
    app.run()
```

## Route handlers

Each route function:

- Receives the current `BaseHTTPRequestHandler` as argument
- Must return a tuple:
  `status_code: int, headers: dict[str, str], body: bytes`

Example:

```python
return 200, [("Content-Type", "text/plain")], b"OK"
```

## License

PSF License
You are free to use, modify, and distribute this software under the terms of the Python Software Foundation License.

> This project is not affiliated with or endorsed by the Python Software Foundation.

