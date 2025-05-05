import json
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation, PermissionDenied
from django.http import Http404, JsonResponse
from urllib.request import Request

from .exceptions import EndpointDisabledException, MethodNotAllowed, Unauthorized


_logger = logging.getLogger('django-small-view-set.default_handle_endpoint_exceptions')
if not _logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


def default_options_and_head_handler(request: Request, allowed_methods: list[str]):
    if request.method == 'OPTIONS':
            response = JsonResponse(
                data=None,
                safe=False,
                status=200,
                content_type='application/json')
            response['Allow'] = ', '.join(allowed_methods)
            return response

    if request.method == 'HEAD':
        response = JsonResponse(
            data=None,
            safe=False,
            status=200,
            content_type='application/json')
        response['Allow'] = ', '.join(allowed_methods)
        return response

    if request.method not in allowed_methods:
        raise MethodNotAllowed(method=request.method)


def default_exception_handler(request: Request, endpoint_name: str, exception):
    try:
        raise exception

    except json.JSONDecodeError:
        return JsonResponse(data={"errors": "Invalid JSON"}, status=400)

    except (TypeError, ValueError) as exception:
        if hasattr(exception, 'detail'):
            return JsonResponse(data={'errors': exception.detail}, status=400)
        if hasattr(exception, 'message'):
            return JsonResponse(data={'errors': exception.message}, status=400)
        return JsonResponse(data=None, safe=False, status=400)

    except Unauthorized:
        return JsonResponse(data=None, safe=False, status=401)

    except (PermissionDenied, SuspiciousOperation):
        return JsonResponse(data=None, safe=False, status=403)

    except (Http404, ObjectDoesNotExist):
        return JsonResponse(data=None, safe=False, status=404)
    
    except EndpointDisabledException:
        return JsonResponse(data=None, safe=False, status=405)

    except MethodNotAllowed as exception:
        return JsonResponse(
            data={'errors': f"Method {exception.method} is not allowed"},
            status=405)

    except Exception as exception:
        # Catch-all exception handler for API endpoints.
        # 
        # - Always defaults to HTTP 500 with "Internal server error" unless the exception provides a more specific status code and error details.
        # - Duck types to extract error information from `detail` or `message` attributes, if available.
        # - Never exposes internal exception contents to end users for 5xx server errors unless settings.DEBUG is True.
        # - Allows structured error payloads (string, list, or dict) without assumptions about the error format.
        # - Logs exceptions fully for server-side diagnostics, distinguishing handled vs unhandled cases.
        # 
        # This design prioritizes API security, developer debugging, and future portability across projects.

        status_code = getattr(exception, 'status_code', 500)
        error_contents = None

        if hasattr(exception, 'detail'):
            error_contents = exception.detail
        elif hasattr(exception, 'message') and isinstance(exception.message, str):
            error_contents = exception.message

        if 400 <= status_code <= 499:
            if status_code == 400:
                message = 'Bad request'
            elif status_code == 401:
                message = 'Unauthorized'
            elif status_code == 403:
                message = 'Forbidden'
            elif status_code == 404:
                message = 'Not found'
            elif status_code == 405:
                message = 'Method not allowed'
            elif status_code == 429:
                message = 'Too many requests'
            elif error_contents:
                message = error_contents
            else:
                message = 'An error occurred'

            if settings.DEBUG and error_contents:
                message = error_contents
        else:
            status_code = 500
            message = 'Internal server error'
            if settings.DEBUG:
                message = error_contents if error_contents else str(exception)

        e_name = type(exception).__name__
        if error_contents:
            msg = f"Handled API exception in {endpoint_name}: {e_name}: {error_contents}"
            _logger.error(msg)
                
        else:
            msg = f"Unhandled exception in {endpoint_name}: {e_name}: {exception}"
            _logger.error(msg)

        return JsonResponse(
            data={'errors': message},
            safe=False,
            status=status_code,
            content_type='application/json')