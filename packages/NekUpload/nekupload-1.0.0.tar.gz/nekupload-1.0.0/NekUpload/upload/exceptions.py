class APIError(Exception):
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response

class ClientError(APIError):
    pass

class ServerError(APIError):
    pass