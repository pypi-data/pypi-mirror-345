from pymongo import MongoClient
from sqlite3 import Connection, Cursor
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Any, Callable

class DB:
    """
    A database handler class supporting MongoDB and SQLite (not yet implemented).
    
    Attributes:
        uri (str): The database connection URI.
        is_available (bool): Indicates whether the database is accessible.
        connection (MongoClient | Connection): Represents the database connection.
        db (Database | Cursor): The database instance.
    """

    def __init__(self, uri: str, is_available: bool, connection: MongoClient | Connection, db: Database | Cursor):
        """
        Initializes the DB class with connection details.

        Args:
            uri (str): The connection URI.
            is_available (bool): Whether the database is available.
            connection (MongoClient | Connection): Database connection instance.
            db (Database | Cursor): The database object.
        """
        DB.uri = uri
        DB.is_available = is_available
        DB.connection = connection
        DB.db = db

    @classmethod
    def get_collection_or_table(self, collection_name: str) -> Collection | Any | None:
        """
        Retrieves a MongoDB collection or SQLite table.
        
        Args:
            collection_name (str): Name of the collection or table.
        
        Returns:
            ### `Collection | Any | None`
            
            A collection or table depending on the type of database you're working with:
            - MongoDB: Collection
            - SQLite: Any (Table structure)
            - Not Found: None
        """
        pass

    @classmethod
    def collection_or_table_exists(self, collection_name: str) -> bool:
        """
        Checks if a MongoDB collection or SQLite table exists.

        Args:
            collection_name (str): Name of the collection or table.
        
        Returns:
            ### `bool`
        """
        pass

    @classmethod
    def insert_to_db(self, collection_name: str, data: dict | list[dict]) -> None:
        """
        Inserts data into the specified collection or table.

        Args:
            collection_name (str): Target collection or table name.
            data (dict | list[dict]): Data to insert.
        
        Returns:
            ### `None`
        """
        pass

    @classmethod
    def replace_to_db(self, collection_name: str, query: dict[str, Any], data: dict[str, Any] | list) -> None:
        """
        Replaces a document or entry in the database.

        Args:
            collection_name (str): Target collection or table.
            query (dict[str, Any]): Query filter.
            data (dict[str, Any] | list): New data to replace.
        
        Returns:
            ### `None`
        """
        pass

    @classmethod
    def update_to_db(self, collection_name: str, query: dict[str, Any], data: dict[str, Any], update_many: bool = False) -> None:
        """
        Updates existing documents or entries in the database.

        Args:
            collection_name (str): Target collection or table.
            query (dict[str, Any]): Query filter.
            data (dict[str, Any]): Updated data.
            update_many (bool | None): Whether to update multiple entries. Defaults to False.
        
        Returns:
            ### `None`
        """
        pass

    @classmethod
    def delete_to_db(self, collection_name: str, query: dict[str, Any], delete_many: bool = False) -> None:
        """
        Deletes documents or entries from the database.

        Args:
            collection_name (str): Target collection or table.
            query (dict[str, Any]): Query filter for deletion.
            delete_many (bool | None): Whether to delete multiple entries. Defaults to False.
        
        Returns:
            ### `None`
        """
        pass

    @classmethod
    def get_from_db(self, collection_name: str, query: dict[str, Any] = {}) -> list[dict[str, Any]] | None:
        """
        Retrieves data from the database based on a query.

        Args:
            collection_name (str): Target collection or table.
            query (dict[str, Any] | None): Query filter for retrieval. Defaults to an empty dict.
        
        Returns:
            ### `list[dict[str, Any]] | None`

            The return type can represent the response status:
            - Success: list[dict[str, Any]]
            - Not Found: None
        """
        pass

def PressDB(cls):
    """
    A decorator that integrates database-specific methods into the main `DB` class.

    Args:
        cls (Any): Should be a `DB` subclass but it isn't mandatory, just recommended.

    Returns:
        ### `Any`
        
        The original decorated subclass with its methods applied to `DB`.
    """
    
    try:
        delete_to_db = classmethod(cls.delete_to_db)
        insert_to_db = classmethod(cls.insert_to_db)
        get_from_db = classmethod(cls.get_from_db)
        update_to_db = classmethod(cls.update_to_db)
        replace_to_db = classmethod(cls.replace_to_db)

        DB.delete_to_db = delete_to_db
        DB.insert_to_db = insert_to_db
        DB.get_from_db = get_from_db
        DB.replace_to_db = replace_to_db
        DB.update_to_db = update_to_db
    except:
        pass

    return cls