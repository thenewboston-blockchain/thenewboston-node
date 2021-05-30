from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import AccountState, NodeDeclarationSignedChangeRequest


def get_updated_account_states_for_network_address_registration(
    signed_change_request: NodeDeclarationSignedChangeRequest, blockchain: BlockchainBase
) -> dict[str, AccountState]:
    return {
        signed_change_request.signer:
            AccountState(network_addresses=signed_change_request.message.network_addresses.copy())
    }
