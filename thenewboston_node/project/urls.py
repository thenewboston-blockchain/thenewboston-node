"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

import thenewboston_node.accounts.urls
import thenewboston_node.blockchain.urls
import thenewboston_node.web.urls

API_PREFIX = 'api/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(thenewboston_node.web.urls)),

    # local apps
    path(API_PREFIX + 'v1/', include(thenewboston_node.accounts.urls)),
    path(API_PREFIX + 'v1/', include(thenewboston_node.blockchain.urls)),
    path(API_PREFIX + 'schema/', SpectacularAPIView.as_view(), name='schema'),
    path(API_PREFIX + 'doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
