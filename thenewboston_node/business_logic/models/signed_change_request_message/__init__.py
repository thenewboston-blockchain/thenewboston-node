from .base import SignedChangeRequestMessage  # noqa: F401
from .coin_transfer import CoinTransferSignedChangeRequestMessage  # noqa: F401
from .coin_transfer_transaction import CoinTransferTransaction  # noqa: F401
from .node_declaration import NodeDeclarationSignedChangeRequestMessage  # noqa: F401
from .pv_schedule import PrimaryValidatorSchedule, PrimaryValidatorScheduleSignedChangeRequestMessage  # noqa: F401

SIGNED_CHANGE_REQUEST_MESSAGE_TYPE_MAP = {
    class_.get_field('signed_change_request_type').default: class_ for class_ in  # type: ignore
    (
        CoinTransferSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage,
        PrimaryValidatorScheduleSignedChangeRequestMessage
    )
}
