class InvalidRootError (BaseException):
    def __str__(self):
        return "Path is not absolute. Try using Path.cwd() for root_folder argument"