class EndpointDisabledException(Exception):
    status_code = 405
    message = "Method Not Allowed"
    error_code = "method_not_allowed"

class Unauthorized(Exception):
    status_code = 401
    message = "Unauthorized"
    error_code = "unauthorized"

class BadRequest(Exception):
    status_code = 400
    error_code = "bad_request"
    def __init__(self, message: str | list | dict):
        """
        Args:
            message (str | list | dict): 
                A JSON-serializable error description to send to the client. 
                Typically a string, list of errors, or dictionary of field errors.
        """
        self.message = message or "Bad Request"
        super().__init__(message)

class MethodNotAllowed(Exception):
    status_code = 405
    error_code = "method_not_allowed"
    def __init__(self, method: str):
        self.method = method
        self.message = f'Method {method} not allowed'
        super().__init__(self.message)