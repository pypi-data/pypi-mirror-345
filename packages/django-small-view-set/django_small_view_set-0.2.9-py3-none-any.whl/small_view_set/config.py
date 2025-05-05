from typing import Callable
from urllib.request import Request
from .helpers import default_exception_handler, default_options_and_head_handler


class SmallViewSetConfig:
    """
    Configuration class for SmallViewSet.

    This class allows customization of exception handling and handling of
    OPTIONS and HEAD requests for endpoints.

    Args:
        exception_handler (Callable[[str, Exception], None]): A callback function
            for handling exceptions. The function takes two parameters:
            1. The name of the endpoint function (e.g., 'list', 'retrieve', or a custom endpoint name).
            2. The exception that was thrown.
        options_and_head_handler (Callable[[Request, list[str]], None]): A callback function
            for handling OPTIONS and HEAD requests. The function takes two parameters:
            1. The Django Request object.
            2. A list of allowed HTTP methods for the endpoint (e.g., ['PUT', 'PATCH']).
    """
    def __init__(
            self,
            exception_handler: Callable[[str, Exception], None] = default_exception_handler,
            options_and_head_handler: Callable[[Request, list[str]], None] = default_options_and_head_handler,
            respect_disabled_endpoints=True):
        self.exception_handler = exception_handler
        self.options_and_head_handler = options_and_head_handler
        self.respect_disabled_endpoints = respect_disabled_endpoints