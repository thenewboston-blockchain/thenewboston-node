from thenewboston_node.core.utils.cryptography import KeyPair
from thenewboston_node.core.utils.types import hexstr

from ..blockchain.memory_blockchain import MemoryBlockchain
from ..models import (
    AccountState, Block, BlockchainState, CoinTransferSignedChangeRequest, NodeDeclarationSignedChangeRequest,
    PrimaryValidator, RegularNode
)

TREASURY_KEY_PAIR = KeyPair(
    public=hexstr('00f3d2477317d53bcc2a410decb68c769eea2f0d74b679369b7417e198bd97b6'),
    private=hexstr('f94fbd639d9507f544fb27b79b5344a2d7b461e333053ed1be45b90c988e6355'),
)

REGULAR_NODE_KEY_PAIR = KeyPair(
    public=hexstr('accf7efe1b2ae044f25b98c38cffa3d6992b82e271c71353df549cbab7abaaf9'),
    private=hexstr('0e92ed657cafd81a51cc32b867af259d8aca2446dd31d1598f0467a15904187b'),
)

PV_KEY_PAIR = KeyPair(
    public=hexstr('657cf373f6f8fb72854bd302269b8b2b3576e3e2a686bd7d0a112babaa1790c6'),
    private=hexstr('5ef5773228743963817f79ea4a4b1e7c1a270f781af44fd141dc68193bce1228'),
)

PV_FIN_ACCOUNT_KEY_PAIR = KeyPair(
    public=hexstr('7a5dc06babda703a7d2d8ea18d3309a0c5e6830a25bac03e69633d283244e001'),
    private=hexstr('d41f52e67645aea0657e2c324efa88a7583310d1e8e7e616bb1233fffeba5151'),
)

USER_KEY_PAIR = KeyPair(
    public=hexstr('7584e5ad3f3d29f44179be133790dc94b52dd2e671b9b96694faa36bcc14c135'),
    private=hexstr('ba719a713651bf1a3ea07bd6eb9bc98721546df2425941d808c2a13c7966ab1f'),
)


def make_sample_blockchain():
    blockchain = MemoryBlockchain()

    pv = PrimaryValidator(
        identifier=PV_KEY_PAIR.public,
        network_addresses=['https://pv-non-existing.thenewboston.com:8000', 'http://78.107.238.40:8000'],
        fee_amount=4,
        fee_account=PV_FIN_ACCOUNT_KEY_PAIR.public
    )
    blockchain_state = BlockchainState(
        account_states={
            TREASURY_KEY_PAIR.public: AccountState(balance=281474976710656),
            PV_KEY_PAIR.public: AccountState(node=pv),
        }
    )
    blockchain.add_blockchain_state(blockchain_state)

    node = RegularNode(
        identifier=REGULAR_NODE_KEY_PAIR.public,
        network_addresses=['https://node42-non-existing.thenewboston.com:8000', 'http://78.107.238.42:8000'],
        fee_amount=3,
    )
    regular_node_scr = NodeDeclarationSignedChangeRequest.create(
        identifier=node.identifier,
        network_addresses=node.network_addresses,
        fee_amount=node.fee_amount,
        signing_key=REGULAR_NODE_KEY_PAIR.private
    )
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, regular_node_scr, PV_KEY_PAIR.private))

    coin_transfer_scr = CoinTransferSignedChangeRequest.from_main_transaction(
        blockchain=blockchain,
        recipient=USER_KEY_PAIR.public,
        amount=1200,
        signing_key=TREASURY_KEY_PAIR.private,
        primary_validator=pv,
        node=node,
    )
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, coin_transfer_scr, PV_KEY_PAIR.private))

    blockchain.snapshot_blockchain_state()
    return blockchain


class SamplesFactory:

    def __init__(self):
        self._blockchain = None

    @property
    def blockchain(self):
        if (blockchain := self._blockchain) is None:
            self._blockchain = blockchain = make_sample_blockchain()

        return blockchain

    def get_sample_blockchain_state(self):
        return self.blockchain.get_last_blockchain_state()

    def get_sample_block_map(self):
        block_map = {}
        for block in self.blockchain.yield_blocks():
            field_type = block.message.signed_change_request.get_field_type('message')
            block_map.setdefault(field_type, block)

        return block_map
