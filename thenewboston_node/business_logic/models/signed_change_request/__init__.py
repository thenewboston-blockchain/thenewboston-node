from .base import SignedChangeRequest  # noqa: F401
from .coin_transfer import CoinTransferSignedChangeRequest  # noqa: F401
from .node_declaration import NodeDeclarationSignedChangeRequest  # noqa: F401
from .pv_schedule import PrimaryValidatorScheduleSignedChangeRequest  # noqa: F401

SIGNED_CHANGE_REQUEST_TYPE_MAP = {
    class_.block_type: class_ for class_ in  # type: ignore
    (CoinTransferSignedChangeRequest, NodeDeclarationSignedChangeRequest, PrimaryValidatorScheduleSignedChangeRequest)
}
