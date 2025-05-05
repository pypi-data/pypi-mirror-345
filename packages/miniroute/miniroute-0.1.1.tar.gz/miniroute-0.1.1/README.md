# Miniroute

**Miniroute** is a minimal HTTP routing framework based on Python’s built-in `http.server`, designed for lightweight local servers and IPC tooling.

### Warning

I've made this module facing a situation where the http protocol was the
simplest way to solve a LOCAL Inter-Process-Communication issue, and did NOT
wanted to add any dependency (like Flask or FastAPI) to my project.
I found out that the standard `http.server` module would do the job, but was a **pain** to integrate.

As the officiel http documentation state : **This is NOT a server to be used in PRODUCTION.**

**This module doesn't address any security flaws that `http.server` may bring up.**

**It's encouraged to be familiar with [http.server documentation before using miniroute](https://docs.python.org/3/library/http.server.html#http.server.HTTPServer)**

### Features

- Simple flask-like route declaration using decorators
- Purely based on standard libraries
- No magic, no dependencies
- Good for local-only HTTP endpoints, and non-performant reliant IPC.

### Installation

```bash
pip install miniroute
```

### Usage

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

### Route handlers

Each route function:

- Receives the current `BaseHTTPRequestHandler` as argument
- Must return a tuple:
  `status_code: int, headers: dict[str, str], body: bytes`

Example:

```python
return 200, [("Content-Type", "text/plain")], b"OK"
```

### License

PSF License
You are free to use, modify, and distribute this software under the terms of the Python Software Foundation License.

> This project is not affiliated with or endorsed by the Python Software Foundation.

