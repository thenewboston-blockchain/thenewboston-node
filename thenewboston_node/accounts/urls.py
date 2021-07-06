from rest_framework import routers

from .views.account_state import AccountStateViewSet
from .views.node import NodeViewSet

router = routers.SimpleRouter()
router.register('account-states', AccountStateViewSet, basename='account-state')
router.register('nodes', NodeViewSet, basename='node')

urlpatterns = router.urls
