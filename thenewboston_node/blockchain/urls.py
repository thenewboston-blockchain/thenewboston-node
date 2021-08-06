from rest_framework import routers

from thenewboston_node.blockchain.views.blockchain_states_meta import BlockchainStatesMetaViewSet

router = routers.SimpleRouter()
router.register('blockchain-states-meta', BlockchainStatesMetaViewSet, basename='blockchain-states-meta')

urlpatterns = router.urls
