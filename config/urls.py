import os
from django.conf import settings
from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import include
from django.conf.urls.static import static, serve
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
#Je l'ai commenté
# from rest_framework_swagger.views import get_swagger_view
from rest_framework import permissions
from rest_framework.authtoken import views
from decouple import config as env
# from .views import api_home
from email_verification import urls as email_urls
from email_verification import forget_password_urls
from email_verification import change_user_info_urls
# from django.conf.urls import (
#   handler400, handler403, handler404, handler500)
# from .views import error404

# handler404 = error404

# swagger_schema_view = get_swagger_view(
#     title='itrasy API',
#     url=env('SWAGGER_BASE_URL', default='https://app.itrasy.com/'),
#     urlconf=env('SWAGGER_BASE_URL', default='https://app.itrasy.com/'),
# )

schema_view = get_schema_view(
  openapi.Info(
    title="itrasy API",
    default_version='v1',
    description="REST API for itrasy backend application",
    
    # Moi Julio, j'ai commenté
    # terms_of_service=env('SWAGGER_BASE_URL', default='https://app.itrasy.com/') + 'termsofservice',
    # contact=openapi.Contact(email="contact@itrasy.com"),
    # license=openapi.License(name="itrasy"),
  ),
  # validators=['flex', 'ssv'],
  public=True,
  permission_classes=(permissions.AllowAny,),
  url=env('SWAGGER_BASE_URL', default='https://staging.itrasy.com/')
)

def trigger_error(request):
  division_by_zero = 1 / 0

urlpatterns = [
    # Admin URL
    path('super-admin/', admin.site.urls),
    path('_nested_admin/', include('nested_admin.urls')),
    # Sentry URL for remote logging
    path('sentry-debug/', trigger_error),
    # Auth URL
    path('email/', include(email_urls)),
    path('forget_password/', include(forget_password_urls)),
    path('change_user_info/', include(change_user_info_urls)),
    # API urls
    re_path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Authentication
    path('api/v1/auth/', include('authentication.urls')),
    # S3 upload url
    path('s3direct/', include('s3direct.urls')),
    # Members
    path('api/v1/member/', include('member.urls')),



    # Default url
    # path(r'^$', api_home, name='api_home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
