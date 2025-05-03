from typing import Any
from pymongo import MongoClient
from pymongo.database import Database, Collection
from .base import DB, PressDB
from .mongo_utils import doc_b64_to_obj_id, doc_id_to_b64

@PressDB
class DB_Mongo(DB):
    """
    A MongoDB-based implementation of the `DB` class.

    This class extends `DB` and provides MongoDB-specific functionality.
    It uses the `PressDB` decorator to apply relevant methods to `DB`,
    allowing seamless database operations.

    Attributes:
        uri (str): The MongoDB connection URI.
        connection (MongoClient): The MongoDB client instance.
        db (Database): The active database reference.
        is_available (bool): Indicates whether the database connection is successful.
    """
    uri: str
    connection: MongoClient
    db: Database
    is_available: bool = False

    def __init__(self, uri: str, db_name: str):
        """
        Initializes a `DB_Mongo` instance and establishes a connection to MongoDB.

        Args:
            uri (str): The connection URI for MongoDB.
            db_name (str): The name of the target database.

        Raises:
            Exception: If the connection fails or the database is unavailable.
        """
        self.uri = uri
        client = MongoClient(uri)
        client.admin.command("ping")  # Ensure MongoDB connection is active
        self.connection = client

        if db_name in client.list_database_names():
            self.db = client.get_database(db_name)
            self.is_available = True

            DB(self.uri, self.is_available, self.connection, self.db)
            DB.collection_or_table_exists = self.collection_or_table_exists
            DB.get_collection_or_table = self.get_collection_or_table

    @classmethod
    def get_collection_or_table(self, collection_name: str) -> Collection | None:
        """
        Retrieves a collection from the MongoDB database.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            ### `Collection | None`
        """
        return self.db.get_collection(collection_name) if collection_name else None

    @classmethod
    def collection_or_table_exists(self, collection_name: str) -> bool:
        """
        Checks whether the specified collection exists in the MongoDB database.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            ### `bool`
        """
        return self.db.get_collection(collection_name) is not None

    def insert_to_db(self, collection_name: str, data: dict | list[dict]) -> None:
        """
        Inserts data into the specified MongoDB collection.

        Args:
            collection_name (str): The target collection name.
            data (dict | list[dict]): The data to insert.

        Returns:
            ### `None`
        """
        if not self.is_available:
            return

        collection: Collection = self.db.get_collection(collection_name)
        if isinstance(data, list):
            data = doc_b64_to_obj_id(data)
            collection.insert_many(data)
        elif isinstance(data, dict):
            data = doc_b64_to_obj_id(data)
            collection.insert_one(data)

    def replace_to_db(self, collection_name: str, query: dict[str, Any], data: dict[str, Any] | list) -> None:
        """
        Replaces a document or multiple documents in the MongoDB collection.

        Args:
            collection_name (str): The target collection name.
            query (dict[str, Any]): The query filter specifying which documents to replace.
            data (dict[str, Any] | list): The replacement data.

        Returns:
            ### `None`
        """
        if not self.is_available: return

        collection: Collection = self.db.get_collection(collection_name)
        if isinstance(data, list):
            data = doc_b64_to_obj_id(data)
            query = doc_b64_to_obj_id(query)
            collection.delete_many(query)
            collection.insert_many(data)
        elif isinstance(data, dict):
            collection.replace_one(query, data)

    def update_to_db(self, collection_name: str, query: dict[str, Any], data: dict[str, Any], update_many: bool = False) -> None:
        """
        Updates documents in the MongoDB collection based on the query.

        Args:
            collection_name (str): The target collection name.
            query (dict[str, Any]): The query filter specifying which documents to update.
            data (dict[str, Any]): The updated data.
            update_many (bool, optional): Whether to update multiple entries. Defaults to False.

        Returns:
            ### `None`
        """
        if not self.is_available:
            return

        collection: Collection = self.db.get_collection(collection_name)
        data = doc_b64_to_obj_id(data)
        query = doc_b64_to_obj_id(query)

        if update_many:
            collection.update_many(query, data)
        else:
            collection.update_one(query, data)

    def delete_to_db(self, collection_name: str, query: dict[str, Any], delete_many: bool = False) -> None:
        """
        Deletes documents in the MongoDB collection based on the query.

        Args:
            collection_name (str): The target collection name.
            query (dict[str, Any]): The query filter specifying which documents to delete.
            delete_many (bool, optional): Whether to delete multiple entries. Defaults to False.

        Returns:
            ### `None`
        """
        if not self.is_available:
            return

        collection: Collection = self.db.get_collection(collection_name)
        query = doc_b64_to_obj_id(query)

        if delete_many:
            collection.delete_many(query)
        else:
            collection.delete_one(query)

    def get_from_db(self, collection_name: str, query: dict[str, Any]) -> list[dict[str, Any]] | None:
        """
        Retrieves documents from the MongoDB collection based on the query.

        Args:
            collection_name (str): The target collection name.
            query (dict[str, Any]): The query filter specifying which documents to retrieve.

        Returns:
            ### `list[dict[str, Any]] | None`
        """

        if not self.is_available:
            return None

        collection: Collection = self.db.get_collection(collection_name)
        cursor: list[dict[str, Any]] = collection.find(query).to_list()
        docs: list[dict[str, Any]] = doc_id_to_b64(cursor)

        return docs if docs else None