class NotAFileException (BaseException):
    def __str__(self):
        return "Not a file path"