
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Documentation for Ecommerce project API",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="oripovmirshod9@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)


def docs_view(request):
    return schema_view.with_ui('swagger', cache_timeout=0)(request)
