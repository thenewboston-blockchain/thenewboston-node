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

    # Third party
    path(API_PREFIX + 'doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path(API_PREFIX + 'schema/', SpectacularAPIView.as_view(), name='schema'),

    # Apps
    path(API_PREFIX + 'v1/', include(thenewboston_node.accounts.urls)),
    path(API_PREFIX + 'v1/', include(thenewboston_node.blockchain.urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
