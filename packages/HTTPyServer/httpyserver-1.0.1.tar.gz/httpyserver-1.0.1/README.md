# HTTPyServer

`HTTPyServer` is a package designed to help in the development of
simple HTTP servers using Python. It lets you connect to your MongoDB
database and handle requests binded to your DB.

## HTTP Requests Handling

You can handle the HTTP requests after initialazing your `Server` instance.

The `Server` class takes 2 arguments: 

- *`address (str)`*: The server address, formatted like `"host:port"`
- *`root (Path)`*: The absolute path of the root folder of your server (Which can be obtained with `Path.cwd()`).

This class has methods that will allow you to register some handlers (callbacks) that follow some specific conventions:

- These methods are called by the `Server.[Method]` format, just like 
`Server.GET`, `Server.POST`, etc.
- They all accept the following args:

    - *`path (str)`*: The server path where this handler will be called.
    - *`handler ((RequestData) -> Basic_Response)`*: The callback that will handle the upcoming requests.

### `Server.GET`: An example
This method is used to register a GET handler that will be called when a GET
request is received by the HTTP server. Example:

```python
my_server = Server("localhost:8080", Path.cwd())

DB_Mongo("somemongodburi", "my_database_name") 
# Initializes your Mongo Database and allows all the handlers to work properly.

def home (request_data):
    res = Basic_GET_Response("main.html") # File in the same folder as this script
    res.send_file() # Sends the file contents to the response contents
    return res

def get_all_users (request_data):
    res = Basic_GET_Response("users-collection") # Collection of the MongoDB database
    res.send_db({}) # Sends a query to the collection and writes the response contents
    return res

my_server.GET("/", home)
my_server.GET("/users", get_all_users)

my_server.start()
```
