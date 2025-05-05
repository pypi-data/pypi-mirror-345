# Django Small View Set

A lightweight and explicit Django ViewSet alternative with minimal abstraction and full async support.

Designed for clear patterns, minimal magic, and complete control over your API endpoints.

### Example Usage

In settings.py
```python
# Register SmallViewSetConfig in settings
from small_view_set SmallViewSetConfig

SMALL_VIEW_SET_CONFIG = SmallViewSetConfig()
```

^^^ This will get you up and running, but it is recommended to write your own [Custom exception handler](./README_CUSTOM_EXCEPTION_HANDLER.md)

Please note, endpoints cannot be registered in `urls.py` with the
request method (like POST, or GET), therefore create a `collection` and/or `detail` orchestrator
method for the standard CRUD operations.


```python
import asyncio
from django.http import JsonResponse
from django.urls import path
from small_view_set import SmallViewSet, endpoint, endpoint_disabled
from urllib.request import Request

class BarViewSet(SmallViewSet):

    def urlpatterns(self):
        return [
            path('api/bars/',          self.collection, name='bars_collection'),
            path('api/bars/<int:pk>/', self.detail,     name='bars_detail'),
            path('api/bars/items/',    self.items,      name='bars_items'),
        ]
    @endpoint(allowed_methods=['GET', 'POST'])
    def collection(self, request: Request):
        if request.method == 'GET':
            return self.list(request)
        raise MethodNotAllowed(request.method)

    @endpoint(allowed_methods=['GET', 'PATCH'])
    async def detail(self, request: Request, pk: int):
        if request.method == 'GET':
            return await self.retrieve(request, pk)
        elif request.method == 'PATCH':
            return self.patch(request, pk)
        raise MethodNotAllowed(request.method)

    def list(self, request):
        self.protect_list(request)
        return JsonResponse({"message": "Hello, world!"}, status=200)

    async def retrieve(self, request: Request, pk: int):
        self.protect_retrieve(request)
        return JsonResponse({"message": f"Detail for ID {pk}"}, status=200)

    def patch(self, request: Request, pk: int):
        self.protect_update(request)
        return JsonResponse({"message": f"Updated {pk}"}, status=200)

    @endpoint(allowed_methods=['GET'])
    async def items(self, request: Request):
        # Pick the closest protect that matches the endoint. `GET items` is closest to a list
        self.protect_list(request)
        await asyncio.sleep(1)
        return JsonResponse({"message": "List of items"}, status=200)
```


## Registering in `urls.py`

To register the viewset in your `urls.py`:

```python
from api.views.bar import BarViewSet

urlpatterns = [
    # Other URLs like admin, static, etc.

    *BarViewSet().urlpatterns(),
]
```


## Deeper learning

- [Custom protections](./README_CUSTOM_PROTECTIONS.md): Learn how to subclass `SmallViewSet` to add custom protections like logged-in checks.
- [Custom exception handler](./README_CUSTOM_EXCEPTION_HANDLER.md): Understand how to write your own exception handler.
- [DRF compatibility](./README_DRF_COMPATIBILITY.md): Learn how to use some of Django Rest Framework's tools, like Serializers.
- [Disabling an endpoint](./README_DISABLE_ENDPOINT.md): Learn how to disable an endpoint without needing to delete it or comment it out.
- [Reason](./README_REASON.md): Reasoning behind this package.
