from http.server import SimpleHTTPRequestHandler
from typing import Callable
from urllib.parse import parse_qs, urlparse

from requests import HTTPError

from .constants import HTTP_CODES
from .ResponseManagers import (
    Basic_DELETE_Response, 
    Basic_GET_Response, 
    Basic_PATCH_Response, 
    Basic_POST_Response, 
    Basic_PUT_Response,
    Basic_Response
)
from .utilities import get_complete_path, get_url_variables, is_var_url

def find_base_for_caller(path:str, callers: list[Callable]) -> str: 
    path = path.split("?")[0]
    exists = path in callers
    base: str = None
    if not exists:
        for base_path in callers:
            if is_var_url(base_path, path):
                exists = True
                base = base_path
    else:
        base = path
    return base

class BodyUtilities:
    def __init__(self, c: Callable, url_v: dict[str, str]):
        self.caller = c
        self.url_variables = url_v

class RequestData:
    """
    A class that represents the data passed to `RequestHandler` custom methods

    Attributes:
        handler (type[SimpleHTTPRequestHandler]): Contains the current server path, client address, etc.
        body (bytes | None): The request body, in bytes.
        url_query (dict[str, str] | None): The dict-formatted query from the current url.
        url_variables (dict[str, str]): The URL params found in the current url.
    """
    handler: type[SimpleHTTPRequestHandler]
    url_query: dict[str, str] | None
    body: bytes | None
    url_variables: dict[str, str]

    def __init__(
            self, 
            handler: type[SimpleHTTPRequestHandler], 
            body: bytes | None, 
            url_query: dict[str, str], 
            url_variables: dict[str, str]):
        
        """
        Initializes a RequestData instance.

        Args:
            handler (type[SimpleHTTPRequestHandler]): Contains the current server path, client address, etc.
            body (bytes | None): The request body, in bytes.
            url_query (dict[str, str] | None): The dict-formatted query from the current url.
            url_variables (dict[str, str]): The URL params found in the current url.
        """

        self.handler = handler
        self.body = body
        self.url_variables = url_variables
        self.url_query = url_query
    
    
class RequestHandler(SimpleHTTPRequestHandler):
    """
    A class that represents a PyPress Request Handler.
        `RequestHandler` handles the upcoming requests through
        user-defined callbacks. 
    
        Supports GET, POST, PUT, PATCH and DELETE request handling.

    **Note**: 
        Its supposed to be used for internal functionality only. 
        If you wanna create a HTTP Server, you should try 
        the `Server` class instead.

    Attributes:
        get_callers (dict[str, Callable[[RequestData], Basic_GET_Response]]): 
            Stores callbacks for handling GET requests.
        post_callers (dict[str, Callable[[RequestData], Basic_POST_Response]]): 
            Stores callbacks for handling POST requests.
        put_callers (dict[str, Callable[[RequestData], Basic_PUT_Response]]): 
            Stores callbacks for handling PUT requests.
        patch_callers (dict[str, Callable[[RequestData], Basic_PATCH_Response]]): 
            Stores callbacks for handling PATCH requests.
        delete_callers (dict[str, Callable[[RequestData], Basic_DELETE_Response]]): 
            Stores callbacks for handling DELETE requests.
    """

    get_callers: dict[str, Callable[[RequestData], Basic_GET_Response]] = {}
    post_callers: dict[str, Callable[[RequestData], Basic_POST_Response]] = {}
    put_callers: dict[str, Callable[[RequestData], Basic_PUT_Response]] = {}
    patch_callers: dict[str, Callable[[RequestData], Basic_PATCH_Response]] = {}
    delete_callers: dict[str, Callable[[RequestData], Basic_DELETE_Response]] = {}
    root: str

    def read_content(self) -> bytes:
        """
        Reads the request body content if available.

        Returns:
            bytes: The raw request body content.
        """
        content: bytes = b""
        if "Content-Length" in dict(self.headers):
            c_length = int(self.headers["Content-Length"])
            content = self.rfile.read(c_length)

        return content

    def write_content(self, content: bytes):
        """
        Writes response content to the output stream.

        Args:
            content (bytes): The response content to send back to the client.
        """
        try:
            if content is not None:
                self.wfile.write(content)
        except Exception as e:
            print("Error while writing data:", e)

    def get_utilities(
        self, 
        callers: dict[str, Callable[[RequestData], type[Basic_Response]]]
    ) -> BodyUtilities | None:
        """
        Retrieves the appropriate request handler based on the requested path.

        Args:
            callers (dict[str, Callable[[RequestData], type[Basic_Response]]]): 
                A dictionary of available handlers for the current HTTP method.

        Returns:
            BodyUtilities | None: The resolved request handler and associated URL parameters.
        """
        base_path = find_base_for_caller(self.path, callers)
        url_variables = {}

        if base_path:
            caller = callers[base_path]
            url_variables = get_url_variables(base_path, self.path)

        return BodyUtilities(caller, url_variables) if base_path else None

    def send_res(self, res: type[Basic_Response]):
        """
        Sends the response back to the client.

        Args:
            res (type[Basic_Response]): The response object containing status codes and content.
        """
        try:
            self.send_response(res.status_code, "CONTENT")
        except HTTPError as e:
            self.send_error(e.response.status_code, e.response.reason)

        self.send_header("Location", get_complete_path(self))
        self.end_headers()

    def do_PUT(self):
        """
        Handles incoming PUT requests.

        Calls the appropriate callback mapped to the request path if available.
        """
        utilities = self.get_utilities(self.put_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            content = self.read_content()
            res: Basic_PUT_Response = utilities.caller(RequestData(self, content, None, utilities.url_variables))
            self.send_res(res)

    def do_PATCH(self):
        """
        Handles incoming PATCH requests.

        Calls the appropriate callback mapped to the request path if available.
        Sends response content if applicable.
        """
        utilities = self.get_utilities(self.patch_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            content = self.read_content()
            res: Basic_PATCH_Response = utilities.caller(RequestData(self, content, None, utilities.url_variables))
            self.send_res(res)
            self.write_content(res.content)

    def do_DELETE(self):
        """
        Handles incoming DELETE requests.

        Calls the appropriate callback mapped to the request path if available.
        """
        utilities = self.get_utilities(self.delete_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.BAD_REQUEST)
        else:
            content = self.read_content()
            res: Basic_DELETE_Response = utilities.caller(RequestData(self, content, None, utilities.url_variables))
            self.send_res(res)
            self.write_content(res.content)

    def do_POST(self):
        """
        Handles incoming POST requests.

        Calls the appropriate callback mapped to the request path if available.
        """
        utilities = self.get_utilities(self.post_callers)
        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            content = self.read_content()
            res: Basic_POST_Response = utilities.caller(RequestData(self, content, None, utilities.url_variables))
            self.send_res(res)
            self.write_content(res.content)

    def do_GET(self):
        """
        Handles incoming GET requests.

        Calls the appropriate callback mapped to the request path if available.
        """
        utilities = self.get_utilities(self.get_callers)

        if utilities is None:
            self.send_error(HTTP_CODES.NOT_FOUND)
        else:
            query = parse_qs(urlparse(self.path).query)
            res: Basic_GET_Response = utilities.caller(RequestData(self, None, query, utilities.url_variables))
            self.send_res(res)
            self.write_content(res.content)