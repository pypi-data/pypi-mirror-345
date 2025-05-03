class DB_METHODS:
    GET = "get_from_db"
    INSERT = "insert_to_db"
    REPLACE = "replace_to_db"
    UPDATE = "update_to_db"
    DELETE = "delete_to_db"

class DB_TYPES:
    MONGO_DB = "MONGO_DB"
    SQLITE3 = "SQLITE3"

class HTTP_CODES:
    REDIRECT = 303
    SUCCESS = 200
    CREATED = 201
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400
    NO_CONTENT = 204
    ACCEPTED = 202

class Mongo_Update_Operators:
    CURRENT_DATE = "$currentDate"
    INC = "$inc"
    MIN = "$min"
    MAX = "$max"
    MUL = "$mul"
    RENAME = "$rename"
    SET = "$set"
    SET_ON_INSERT = "$setOnInsert"
    UNSET = "$unset"