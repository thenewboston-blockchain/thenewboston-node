from .base import SignedChangeRequest  # noqa: F401
from .coin_transfer import CoinTransferSignedChangeRequest  # noqa: F401
from .node_declaration import NodeDeclarationSignedChangeRequest  # noqa: F401

SIGNED_CHANGE_REQUEST_TYPE_MAP = (
    (CoinTransferSignedChangeRequest.block_type, CoinTransferSignedChangeRequest),
    (NodeDeclarationSignedChangeRequest.block_type, NodeDeclarationSignedChangeRequest),
)
