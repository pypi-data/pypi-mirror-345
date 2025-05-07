

class PlatformAPIException(Exception):
    def __init__(self, message):
        self.message = message


class WrongUsageException(PlatformAPIException):
    def __init__(self, message):
        super().__init__(message)
