from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from api_docs.api import docs_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('product_app.urls')),
    path('users/', include('users.urls')),
    path('api-docs/', docs_view, name='api'),
    path('api/', include('api.user_urls')),
    path('api/', include('api.product_urls')),
    path('paypal/', include("paypal.standard.ipn.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
