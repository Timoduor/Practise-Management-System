from django.urls import get_resolver
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.errors import SwaggerGenerationError
from drf_yasg.generators import OpenAPISchemaGenerator
import traceback

class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        return super().get_schema(request, public)

def debug_schema():
    info = openapi.Info(
        title="Debug API",
        default_version='v1',
        description="Temporary schema for debugging",
    )

    generator = CustomOpenAPISchemaGenerator(info=info)
    resolver = get_resolver()

    for pattern in resolver.url_patterns:
        callback = pattern.callback

        if not hasattr(callback, 'cls') or not issubclass(callback.cls, APIView):
            continue

        view_class = callback.cls
        methods = [
            method.upper()
            for method in view_class.http_method_names
            if hasattr(view_class, method)
        ]

        for method in methods:
            if method in ["OPTIONS", "HEAD"]:  # skip methods Swagger doesn't handle
                continue
            try:
                view = view_class()
                path = getattr(pattern.pattern, "_route", str(pattern.pattern))
                generator.get_operation(
                    view=view,
                    path=path,
                    prefix='',
                    method=method,
                    components={},
                    request=None
                )
                print(f"✅ OK: {view_class.__name__} [{method}]")
            except SwaggerGenerationError as e:
                print(f"❌ Swagger ERROR: {view_class.__name__} [{method}]") 
                print(f"   └─ {e}")
                traceback.print_exc()
            except Exception as ex:
                print(f"⚠️ General FAILURE: {view_class.__name__} [{method}]")
                print(f"   └─ {ex}")
                traceback.print_exc()
