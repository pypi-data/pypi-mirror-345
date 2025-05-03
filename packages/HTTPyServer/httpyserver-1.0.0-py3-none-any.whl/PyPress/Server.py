from http.server import HTTPServer
from pathlib import Path
from typing import Any, Callable
from . import RequestData
from .RequestHandler import RequestHandler
from .ResponseManagers import (
    Basic_DELETE_Response,
    Basic_GET_Response,
    Basic_PATCH_Response,
    Basic_POST_Response,
    Basic_PUT_Response,
    Basic_Response
)

from .Server_Exceptions import *

class Server:
    """
    A class that represents a PyPress HTTP server.

    The `Server` class initializes an HTTP server, sets the root folder for `Basic_GET_Response`,
    and registers request handlers for various HTTP methods via `RequestHandler`.

    Attributes:
        root (str): The root directory for file retrieval in GET responses.
        address (str): The network address where the server is hosted.
        session (HTTPServer): The active HTTP server instance.
    """

    root: str

    def __init__(self, address: str, root_folder: Path):
        """
        Initializes a `Server` instance and sets up an HTTP server.

        **Note:**
        - The `root_folder` must be an **absolute path**, otherwise an `InvalidRootError` is raised.
        - The server binds to the provided `address` and uses `RequestHandler` to manage requests.

        Example:
            ```python
            from pathlib import Path
            server = Server("127.0.0.1:8080", Path.cwd())
            server.start()
            ```

        Args:
            address (str): The address where the server should listen, formatted as `host:port`.
            root_folder (Path): The absolute path serving as the root directory for GET responses.
        """
        inet_address = address.split(":")[0:2]
        inet_address[1] = int(inet_address[1])
        self.session = HTTPServer(tuple(inet_address), RequestHandler)
        self.address = address

        if root_folder.is_absolute():
            Basic_GET_Response.root = root_folder.as_posix()
        else:
            raise InvalidRootError("Path is not absolute. Try using Path.cwd() for root_folder argument.")

    def CALL(
        self,
        path: str,
        callback: Callable[[RequestData], type[Basic_Response]],
        caller_lib: dict[str, Callable[[RequestData], type[Basic_Response]]],
    ):
        """
        Registers a callback function for handling requests at a specified path.

        Args:
            path (str): The server path where the callback should be triggered.
            callback (Callable): The function handling requests for the given path.
            caller_lib (dict[str, Callable]): The dictionary mapping paths to callback functions.
        """
        if callback and path:
            caller_lib[path] = callback

    def GET(self, path: str, callback: Callable[[RequestData], Basic_GET_Response]):
        """
        Registers a handler for GET requests.

        Args:
            path (str): The server path where the GET callback should be triggered.
            callback (Callable): The function handling GET requests at the given path.
        """
        self.CALL(path, callback, RequestHandler.get_callers)

    def POST(self, path: str, callback: Callable[[RequestData], Basic_POST_Response]):
        """
        Registers a handler for POST requests.

        Args:
            path (str): The server path where the POST callback should be triggered.
            callback (Callable): The function handling POST requests at the given path.
        """
        self.CALL(path, callback, RequestHandler.post_callers)

    def PUT(self, path: str, callback: Callable[[RequestData], Basic_PUT_Response]):
        """
        Registers a handler for PUT requests.

        Args:
            path (str): The server path where the PUT callback should be triggered.
            callback (Callable): The function handling PUT requests at the given path.
        """
        self.CALL(path, callback, RequestHandler.put_callers)

    def PATCH(self, path: str, callback: Callable[[RequestData], Basic_PATCH_Response]):
        """
        Registers a handler for PATCH requests.

        Args:
            path (str): The server path where the PATCH callback should be triggered.
            callback (Callable): The function handling PATCH requests at the given path.
        """
        self.CALL(path, callback, RequestHandler.patch_callers)

    def DELETE(self, path: str, callback: Callable[[RequestData], Basic_DELETE_Response]):
        """
        Registers a handler for DELETE requests.

        Args:
            path (str): The server path where the DELETE callback should be triggered.
            callback (Callable): The function handling DELETE requests at the given path.
        """
        self.CALL(path, callback, RequestHandler.delete_callers)

    def start(self):
        """
        Starts the HTTP server and listens for incoming requests.

        **Note:**
        - The server runs indefinitely, handling requests using `RequestHandler`.
        - If no session is available, it prints an error message.

        Example:
            ```python
            server = Server("127.0.0.1:8080", Path.cwd())
            server.start()
            ```

        """
        print("Starting Server...")
        if self.session:
            print(f"Session started at http://{self.address}")
            with self.session as Http_Server:
                Http_Server.serve_forever()
        else:
            print("There's no session available.")