import json
import logging
from urllib.request import Request

from .exceptions import BadRequest

logger = logging.getLogger('app')

class SmallViewSet:
    def parse_json_body(self, request: Request):
        if request.content_type != 'application/json':
            raise BadRequest('Invalid content type')
        return json.loads(request.body)

    def protect_create(self, request: Request):
        """
        Stub for adding any custom business logic to protect the create method.
        For example:
        - Check if the user is authenticated
        - Check if the user has validated their email
        - Throttle requests

        Recommended to call super().protect_create(request) in the subclass in case
        this library adds logic in the future.
        """
        pass

    def protect_list(self, request: Request):
        """
        Stub for adding any custom business logic to protect the list method.
        For example:
        - Check if the user is authenticated
        - Check if the user has validated their email
        - Throttle requests

        Recommended to call super().protect_create(request) in the subclass in case
        this library adds logic in the future.
        """
        pass

    def protect_retrieve(self, request: Request):
        """
        Stub for adding any custom business logic to protect the retrieve method.
        For example:
        - Check if the user is authenticated
        - Check if the user has validated their email
        - Throttle requests

        Recommended to call super().protect_create(request) in the subclass in case
        this library adds logic in the future.
        """
        pass

    def protect_update(self, request: Request):
        """
        Stub for adding any custom business logic to protect the update method.
        For example:
        - Check if the user is authenticated
        - Check if the user has validated their email
        - Throttle requests

        Recommended to call super().protect_create(request) in the subclass in case
        this library adds logic in the future.
        """
        pass

    def protect_delete(self, request: Request):
        """
        Stub for adding any custom business logic to protect the delete method.
        For example:
        - Check if the user is authenticated
        - Check if the user has validated their email
        - Throttle requests

        Recommended to call super().protect_create(request) in the subclass in case
        this library adds logic in the future.
        """
        pass
