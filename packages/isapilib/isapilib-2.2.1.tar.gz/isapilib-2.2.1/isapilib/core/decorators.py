from django.conf import settings
from django.http import JsonResponse

from rest_framework.exceptions import APIException


def safe_method(view_func):
    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except APIException as e:
            raise e
        except Exception as e:
            if settings.DEBUG: raise e
            return JsonResponse({
                'type': str(type(e)),
                'message': str(e)
            }, status=500)

    return wrapped_view
