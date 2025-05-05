import inspect
from django.conf import settings

from .config import SmallViewSetConfig
from .exceptions import EndpointDisabledException

def endpoint(
        allowed_methods: list[str]):
    def decorator(func):
        func_name = func.__name__
        def sync_wrapper(viewset, *args, **kwargs):
            request = args[0]
            args = args[1:]
            try:
                config: SmallViewSetConfig = getattr(settings, 'SMALL_VIEW_SET_CONFIG', SmallViewSetConfig())
                pre_response = config.options_and_head_handler(request, allowed_methods)
                if pre_response:
                    return pre_response
                pk = kwargs.pop('pk', None)
                if pk is None:
                    return func(viewset, request=request, *args, **kwargs)
                else:
                    return func(viewset, request=request, pk=pk, *args, **kwargs)
            except Exception as e:
                return config.exception_handler(request, func_name, e)

        async def async_wrapper(viewset, *args, **kwargs):
            request = args[0]
            args = args[1:]
            try:
                config: SmallViewSetConfig = getattr(settings, 'SMALL_VIEW_SET_CONFIG', SmallViewSetConfig())
                pre_response = config.options_and_head_handler(request, allowed_methods)
                if pre_response:
                    return pre_response
                pk = kwargs.pop('pk', None)
                if pk is None:
                    return await func(viewset, request=request, *args, **kwargs)
                else:
                    return await func(viewset, request=request, pk=pk, *args, **kwargs)
            except Exception as e:
                return config.exception_handler(request, func_name, e)

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def endpoint_disabled(func):
    """
    Temporarily disables an API endpoint based on the SMALL_VIEWSET_RESPECT_DISABLED_ENDPOINTS setting.

    When `SMALL_VIEWSET_RESPECT_DISABLED_ENDPOINTS` in Django settings is set to `True`, this decorator
    will raise an `EndpointDisabledException`, resulting in a 404 response. When set to `False`,
    the endpoint will remain active, which is useful for testing environments.

    Usage:
        - Apply this decorator directly to a view method or action.
        - Example:
        
        ```python
        class ExampleViewSet(SmallViewSet):

            @endpoint(allowed_method=['GET'])
            @endpoint_disabled
            def retrieve(self, request: Request) -> JsonResponse:
                self.protect_retrieve(request)
                . . .
        ```
    """
    config: SmallViewSetConfig = getattr(settings, 'SMALL_VIEW_SET_CONFIG', SmallViewSetConfig())
    def sync_wrapper(*args, **kwargs):
        if config.respect_disabled_endpoints:
            raise EndpointDisabledException()
        return func(*args, **kwargs)

    async def async_wrapper(*args, **kwargs):
        if config.respect_disabled_endpoints:
            raise EndpointDisabledException()
        return await func(*args, **kwargs)


    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

