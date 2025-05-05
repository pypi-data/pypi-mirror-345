# miniroute/miniroute.py
from http.server import BaseHTTPRequestHandler, HTTPServer

class CustomHandler(BaseHTTPRequestHandler):
    ...

class MiniRouter:
    """
    This is a really SIMPLE router that's designed to
    seemlessly integrates the http module of the Python standard
    library workflow.

    Currently, if you want a quick and lightweight http server
    for prototyping, or just facilitating IPC in your projects with
    http, you have to use a SimpleHTTPRequestHandler object for a http.server.

    Which would be fine, but it handles requests in way that you have to implement
    its do_GET() & do_POST() methods, and at this point, you realize that you either
    need to make your own router, or have those methods filled with conditions for
    each path you want to have as a route.

    This router is used by Miniroute, which is JUST a really basic implementation of a
    standard BaseHTTPRequestHandler, that allows you to use it like you would with a
    Flask/FastAPI program.


    ## ATTENTION PLEASE

    - It's not supposed to be a grand revolutionnary tool.
    - It certainly DO NOT makes the http.server PRODUCTION ready.
    - It definitely did not correct nor fixed any security issues the
        http module has documented.

    ## BUT

    - It simplifies a LOT how a user would add this module to its workflow.
    - There are less than 100 lines of codes that aren't FROM the python
        standard library.
    - If I needed it, maybe you would need it too ?

    """
    def __init__(self):
        self.routes = {}

    def add(self, method, path, func):
        """ Add a new route to the routes map dict.
        """
        self.routes[(method.upper(), path)] = func

    def dispatch(self, method, path):
        """ Simple dispatcher, self-explanatory.
        """
        return self.routes.get((method.upper(), path), None)

    def get(self, path):
        """ Decorator that's used to register a route for GET requests.
        For the sake of simplicity, you will have to implement the HTTP response
        yourself the following way (or don't but it's uncool to ghost your client):

        return status: int, headers: dict, response: byte

        """
        def wrapper(func):
            self.add("GET", path, func)
            return func
        return wrapper

    def post(self, path):
        """ Decorator that's used to register a route for POST requests.
        It's the exact same as the get one.
        Hey don't blame me for the redundancy, I'm just following the http
        module design.
        Well ok ... if you're too lazy to check the get method doc, this is
        what you're expected to return:

        return status: int, headers: dict, response: byte

        """
        def wrapper(func):
            self.add("POST", path, func)
            return func
        return wrapper


class Miniroute:
    """
    Miniroute is a lightweight implementation of a standard HTTPServer
    from the http.server Python library, that comes with a BaseHTTPRequestHandler
    factory that makes this server useable the way you would a Flask or FastAPI
    app (semantic wise).

    ## Example

    ```Python
    router = Miniroute()

    @router.get("/")
    def index(handler):
        # The handler is passed here as a parameter to give you
        # access to every attributes of the BaseHTTPRequestHandler
        # you would have access to when using the http module
        # the 'normal' way

        status: int = 200
        headers: dict = {"Content-Type": "text/html", "Hello": "World"}
        response: byte = "</h1>Hello World<h1>".encode()

        return status, headers, response

    if __name__ == "__main__":
        router.run(host="127.0.0.1", port=2685)
    ```

    """
    def __init__(
            self,
            host: str = "localhost",
            port: int = 2685
        ) -> None:
        """
        router: Router() = use this to access the get and post decorators.
        host: str = IP or DOMAIN on which the serve will listen for connection.
        port: int = Well ... You should know what a port is.
        """
        self._router = MiniRouter()
        self.host: str = host
        self.port: int = port

    @property
    def router(self) -> MiniRouter:
        return self._router

    def run(self) -> None:
        handler_class = self._make_handler()
        server = HTTPServer(
                (
                    self.host,
                    self.port
                ),
                handler_class # pyright: ignore[reportArgumentType]
            )
        print(f"Serving on http://{self.host}:{self.port}")
        server.serve_forever()

    def _make_handler(self) -> CustomHandler:
        router = self._router

        class CustomHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self._handle("GET")

            def do_POST(self):
                self._handle("POST")

            def _handle(self, method):
                func = router.dispatch(method, self.path)
                if func:
                    status, headers, body = func(self)
                    self.send_response(status)
                    for key, value in headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_error(404, "Not found")

        return CustomHandler # pyright: ignore[reportReturnType]

