from rest_framework import routers

from thenewboston_node.blockchain.views.block_chunks_meta import BlockChunksMetaViewSet
from thenewboston_node.blockchain.views.block_confirmation import BlockConfirmationViewSet
from thenewboston_node.blockchain.views.blockchain_states_meta import BlockchainStatesMetaViewSet
from thenewboston_node.blockchain.views.signed_change_request import SignedChangeRequestViewSet

router = routers.SimpleRouter()
router.register('blockchain-states-meta', BlockchainStatesMetaViewSet, basename='blockchain-states-meta')
router.register('block-chunks-meta', BlockChunksMetaViewSet, basename='block-chunks-meta')
router.register('signed-change-request', SignedChangeRequestViewSet, basename='signed-change-request')
router.register('block-confirmations', BlockConfirmationViewSet, basename='block-confirmations')

urlpatterns = router.urls
