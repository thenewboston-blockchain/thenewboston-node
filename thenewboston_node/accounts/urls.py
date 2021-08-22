from django.urls import re_path

from rest_framework import routers

from .views.account_state import AccountStateViewSet
from .views.node import NodeViewSet
from .views.transactions import TransactionViewSet

router = routers.SimpleRouter()
router.register('account-states', AccountStateViewSet, basename='account-state')
router.register('nodes', NodeViewSet, basename='node')

urlpatterns = [
    re_path(
        r'^accounts/(?P<id>[0-9a-f]{64})/transactions/',
        TransactionViewSet.as_view({'get': 'list'}),
        name='transactions-list'
    ),
]

urlpatterns += router.urls
