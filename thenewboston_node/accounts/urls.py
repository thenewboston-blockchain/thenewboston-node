from rest_framework import routers

from .views.account_balance import AccountBalanceViewSet

router = routers.SimpleRouter()
router.register('account-states', AccountBalanceViewSet, basename='account-balance')

urlpatterns = router.urls
