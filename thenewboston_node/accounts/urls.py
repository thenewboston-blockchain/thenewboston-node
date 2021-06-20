from rest_framework import routers

from .views.account_state import AccountStateViewSet

router = routers.SimpleRouter()
router.register('account-states', AccountStateViewSet, basename='account-state')

urlpatterns = router.urls
