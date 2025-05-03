from http.server import BaseHTTPRequestHandler
from types import NoneType
from typing import Any

from pathlib import Path

from .constants import HTTP_CODES
from .base import DB
from .utilities import checkModel, get_base_path, isPatchableBy

import json

doc_to_bytes = lambda doc: bytes(json.dumps(doc), "utf-8") if doc is not None else None

class Basic_Response ():
    """
    Base class for all PyPress HTTP Responses.

    Attributes:
        status_code (HTTP_CODES): The HTTP status code representing the request's result.
        content (bytes): The response content, if applicable.
    """
    status_code: HTTP_CODES
    content: bytes|NoneType

class Basic_GET_Response (Basic_Response):
    """
    A class that represents a PyPress HTTP Response to a GET request.

    It provides methods for redirecting requests, serving files, and retrieving database entries.

    Attributes:
        root (str): The root directory for file retrieval.
        path (str): The requested resource path or collection name.
        status_code (HTTP_CODES): The HTTP status code representing the request's result.
        content (bytes): The response content, if applicable.
    """

    root: str
    path: str
    status_code: HTTP_CODES
    content: bytes = None

    def __init__(
            self,
            path_or_collection_name: str
        ):
        """
        Initializes a `Basic_GET_Reponse` instance for a specified filepath or collection/table name

        Args:
            path_or_collection_name (str): The path or collection/table name for the request.
        """

        self.status_code = HTTP_CODES.BAD_REQUEST
        self.path = path_or_collection_name
    
    def redirect(self, handler: BaseHTTPRequestHandler, new_path: str):
        """
        Redirects the request to a new path. Sets `status_code` to `303 REDIRECT`

        Args:
            handler (BaseHTTPRequestHandler): The request handler instance.
            new_path (str): The new path to redirect to.
        """
        self.status_code = HTTP_CODES.REDIRECT
        handler.path = new_path

    def send_file (self, url_variables: dict[str, str] = {}):
        """
        Retrieves a file from the server and sets the response content if found.

        Sets `status_code` to the next values depending on the request result:
            - `SUCCESS`: The file contents are now saved on the response's content field.
            - `NOT_FOUND`: The file doesn't exists in the given path
            - `INTERNAL_SERVER_ERROR`: Something wrong happened trying to write the response content

        Args:
            url_variables (dict[str, str], optional): A dict of URL params found in the server path.
        """
        print(self.root, self.path)
        base_path = get_base_path(Path(self.path).as_posix(), url_variables)
        path = (
            Path(self.root).joinpath(base_path) if 
            self.root else 
            Path(base_path)
        )

        if path.exists() and path.is_absolute() and path.is_file():
            self.path = path.as_posix()
        else:
            self.status_code = HTTP_CODES.NOT_FOUND
            
        try:
            if path.is_file():
                with open(self.path, "rb") as file_data:
                    self.content = file_data.read()
                self.status_code = HTTP_CODES.SUCCESS

        except Exception as e:
            print(e)
            self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR

    def send_db (self, query: dict[str, Any]):
        """
        Queries a database collection and sets the response content if data is found.

        Sets `status_code` to the next values depending on the request result:
            - `SUCCESS`: The entry was found and is being retrieved as binary data formatted in JSON.
            - `NOT_FOUND`: The given query couldn't find any match in the collection.
            - `INTERNAL_SERVER_ERROR`: Something wrong happened trying to write the response content.

        Args:
            query (dict[str, Any]): The query parameters for retrieving data.
        """
        try:
            if DB.collection_or_table_exists(self.path):
                docs = DB.get_from_db(self.path, query)
                print(docs)
                if docs is not None:
                    self.content = doc_to_bytes(docs)
                    self.status_code = HTTP_CODES.SUCCESS

        except Exception as e:
            print(e.with_traceback(None))
            self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        
class Basic_POST_Response(Basic_Response):
    """
    A class that represents a PyPress HTTP Response to a POST request.

    It provides methods for handling POST requests and inserting data into a database.

    Attributes:
        status_code (HTTP_CODES): The HTTP status code representing the request's result.
        body (dict | list): The request body containing data to be inserted.
        collection_name (str): The database collection/table name where data will be stored.
        valid_model (bool): Indicates whether the provided model validation was successful.
        content (bytes): The response content, if applicable.
    """

    status_code: HTTP_CODES
    body: dict | list
    collection_name: str
    valid_model: bool
    content: bytes

    def __init__(self, collection_name: str, body: dict | list, model: Any):
        """
        Initializes a `Basic_POST_Response` instance for a specified collection name and request body.

        Args:
            collection_name (str): The database collection/table name where data should be inserted.
            body (dict | list): The data to be stored in the database.
            model (Any): The validation model for the provided body.

        Sets `status_code` to the next values depending on validation:
            - `SUCCESS`: The model validation passed.
            - `BAD_REQUEST`: The provided model or body validation failed.
            - `NOT_FOUND`: The specified collection/table does not exist.
        """
        self.valid_model = checkModel(model, body)
        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST
        self.content = b""

        if not DB.collection_or_table_exists(collection_name):
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None

    def send(self, html: bytes = b""):
        """
        Inserts data into the specified collection and sets the response content.

        Sets `status_code` to the next values depending on the request result:
            - `CREATED`: Data was successfully inserted into the database.
            - `BAD_REQUEST`: Model validation failed.
            - `INTERNAL_SERVER_ERROR`: An error occurred while inserting data.

        Args:
            html (bytes, optional): Optional HTML response content.
        """
        if self.valid_model:
            self.content = html
            try:
                DB.insert_to_db(self.collection_name, self.body)
                self.status_code = HTTP_CODES.CREATED
            except Exception as e:
                print("Internal Server Error on Post: ", e.with_traceback(None))
                self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        else:
            self.status_code = HTTP_CODES.BAD_REQUEST

class Basic_PUT_Response(Basic_Response):
    """
    A class that represents a PyPress HTTP Response to a PUT request.

    It provides methods for updating or inserting data into a database based on a query.

    Attributes:
        status_code (HTTP_CODES): The HTTP status code representing the request's result.
        body (dict | list): The request body containing data to be updated or inserted.
        collection_name (str): The database collection/table name where data is stored.
        valid_model (bool): Indicates whether the provided model validation was successful.
        query (dict[str, Any]): The query parameters used to identify existing database entries.
        content (bytes): The response content, if applicable.
    """

    status_code: HTTP_CODES
    body: dict | list
    collection_name: str
    valid_model: bool
    query: dict[str, Any]
    content: bytes = None

    def __init__(self, collection_name: str, body: dict | list, query: dict[str, Any], model: Any):
        """
        Initializes a `Basic_PUT_Response` instance for a specified collection name, request body, and query.

        Example:
            ```python
            class User:
                username: str
                email: str
                age: int

            new_user = {
                "username": "johndoe05",
                "email": "some_electronicmail@crazysite.com",
                "age": 25
            }

            res = Basic_PUT_Response(
                "users_collection",
                new_user,
                { "username": "johndoe05" },
                User
            )

            res.send(f"/users/{new_user['username']}")
            ```

        Args:
            collection_name (str): The database collection/table name where data will be updated or inserted.
            body (dict | list): The data to be updated or inserted.
            query (dict[str, Any]): The query parameters to identify the existing entry in the database.
            model (Any): A class defining the expected structure of the data.
        """
        self.valid_model = checkModel(model, body)
        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST

        if not DB.collection_or_table_exists(collection_name):
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None
            self.query = query if self.valid_model else None

    def send(self, path: str = None):
        """
        Updates or inserts data into the specified collection and sets the response content.

        Sets `status_code` to the following values depending on the request result:
            - `CREATED`: The entry was not found, and a new record has been inserted.
            - `SUCCESS`: The entry was found and successfully updated.
            - `NO_CONTENT`: The request was processed, but no additional response content is provided.
            - `INTERNAL_SERVER_ERROR`: An error occurred while inserting or updating data.

        Args:
            path (str, optional): An optional path indicating the location of the resource.
        """
        if self.valid_model:
            doc = DB.get_from_db(self.collection_name, self.query)
            print(doc)

            self.content = bytes(path, "utf-8") if path else b""

            if doc is None:
                try:
                    DB.insert_to_db(self.collection_name, self.body)
                    self.status_code = HTTP_CODES.CREATED if path else HTTP_CODES.NO_CONTENT
                except:
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
            else:
                try:
                    DB.replace_to_db(self.collection_name, self.query, self.body)
                    self.status_code = HTTP_CODES.SUCCESS if path else HTTP_CODES.NO_CONTENT
                except:
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        
class Basic_PATCH_Response(Basic_Response):
    """
    A class that represents a PyPress HTTP Response to a PATCH request.

    This class enables partial updates to existing database entries.
    It supports **MongoDB-style `$ operators`** for targeted field modifications.

    Attributes:
        status_code (HTTP_CODES): The HTTP status code representing the request's result.
        body (dict): The partial data to update in the entry.
        collection_name (str): The database collection/table name where data is stored.
        valid_model (bool): Indicates whether the provided model validation was successful.
        query (dict): The query parameters used to identify existing database entries.
        content (bytes): The response content, if applicable.
    """

    status_code: HTTP_CODES
    body: dict | list
    collection_name: str
    valid_model: bool
    query: dict[str, Any]
    content: bytes = None

    def __init__(self, collection_name: str, body: dict, query: dict, model: Any):
        """
        Initializes a `Basic_PATCH_Response` instance for a specified collection name, request body, and query.

        **Important:** 
        - PATCH operations rely on **MongoDB-style `$ operators`**, meaning the `body` dictionary 
          should include operators like `$set`, `$inc`, or `$push` for modifying specific fields.

        Example:
            ```python
            # Example for MongoDB
            class User:
                username: str
                email: str
                age: int

            patch_data = {
                "$set": {"email": "newmail@example.com"},
                "$inc": {"age": 1}
            }

            res = Basic_PATCH_Response(
                "users_collection",
                patch_data,
                { "username": "johndoe05" },
                User
            )

            res.send()
            ```

        Args:
            collection_name (str): The database collection/table name where data will be updated.
            body (dict): The partial data to update in the entry (**must contain `$ operators`**).
            query (dict): The query parameters to identify the existing entry in the database.
            model (Any): A class defining the expected structure of the data.
        """
        self.valid_model = isPatchableBy(model, body)
        self.status_code = HTTP_CODES.SUCCESS if self.valid_model else HTTP_CODES.BAD_REQUEST
        self.content = b""

        if not DB.collection_or_table_exists(collection_name):
            self.status_code = HTTP_CODES.NOT_FOUND
        else:
            self.collection_name = collection_name
            self.body = body if self.valid_model else None
            self.query = query if self.valid_model else None

    def send(self, path: str = None, patch_many=False):
        """
        Applies a PATCH update to the specified entry or multiple entries in the collection.

        PATCH operations modify existing fields without replacing full documents.
        This method utilizes **MongoDB-style `$ operators`** for targeted updates.

        Sets `status_code` to the following values depending on the request result:
            - `SUCCESS`: The entry was found and successfully updated.
            - `NO_CONTENT`: The request was processed, but no additional response content is provided.
            - `NOT_FOUND`: The specified entry does not exist in the database.
            - `INTERNAL_SERVER_ERROR`: An error occurred while updating data.

        Args:
            path (str, optional): An optional path indicating the location of the resource.
            patch_many (bool, optional): If `True`, modifies **all matching entries** instead of just one.
        """
        if self.valid_model:
            doc = DB.get_from_db(self.collection_name, self.query)

            self.status_code = HTTP_CODES.SUCCESS if path else HTTP_CODES.NO_CONTENT
            self.content = bytes(path, "utf-8") if path else b""

            if doc is not None:
                try:
                    DB.update_to_db(self.collection_name, self.query, self.body, patch_many)
                except Exception as e:
                    print(e.with_traceback(None))
                    self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR


class Basic_DELETE_Response(Basic_Response):
    """
    A class that represents a PyPress HTTP Response to a DELETE request.

    This class handles the deletion of database entries based on a query.

    Attributes:
        status_code (HTTP_CODES): The HTTP status code representing the request's result.
        collection_name (str): The database collection/table name where entries will be deleted.
        query (dict[str, Any]): The query parameters used to identify the entries for deletion.
        docs (Any): The matched documents that are set for deletion.
        content (bytes): The response content, if applicable.
    """
    docs: list[dict[str, Any]] | None
    collection_name: str
    query: dict[str, Any]
    status_code: HTTP_CODES
    content: bytes

    def __init__(self, collection_name: str, query: dict[str, Any]):
        """
        Initializes a `Basic_DELETE_Response` instance for deleting database entries.

        **Note:** 
        - If the specified collection/table does not exist, deletion cannot be performed.
        - The request is marked as `ACCEPTED` while preparing for deletion.

        Example:
            ```python
            res = Basic_DELETE_Response(
                "users_collection",
                { "username": "johndoe05" }
            )

            res.send()
            ```

        Args:
            collection_name (str): The database collection/table name where entries will be deleted.
            query (dict[str, Any]): The query parameters to locate the entries for deletion.
        """
        self.docs = DB.get_from_db(collection_name, query)
        self.collection_name = collection_name
        self.query = query
        self.status_code = HTTP_CODES.ACCEPTED
        self.content = b""

    def send(self, success_msg: bytes = b"", delete_many=False):
        """
        Executes the deletion request for the specified entries in the collection.

        Sets `status_code` to the following values depending on the request result:
            - `SUCCESS`: The entries were successfully deleted.
            - `NO_CONTENT`: The deletion occurred, but no response content was provided.
            - `NOT_FOUND`: No matching entries were found for deletion.
            - `INTERNAL_SERVER_ERROR`: An error occurred during the deletion process.

        Args:
            success_msg (bytes, optional): A custom message to include in the response after successful deletion.
            delete_many (bool, optional): If `True`, deletes **all matching entries** instead of just one.
        """
        if self.docs is not None:
            try:
                DB.delete_to_db(self.collection_name, self.query, delete_many)
                self.status_code = HTTP_CODES.SUCCESS if success_msg else HTTP_CODES.NO_CONTENT
                self.content = success_msg
            except:
                self.status_code = HTTP_CODES.INTERNAL_SERVER_ERROR
        else:
            self.status_code = HTTP_CODES.NOT_FOUND