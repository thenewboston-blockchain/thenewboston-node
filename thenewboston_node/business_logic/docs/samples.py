import datetime

from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.models.base import BlockType
from thenewboston_node.core.utils.types import hexstr

BLOCK_SAMPLE = models.Block(
    signer=hexstr('4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'),
    message_hash=hexstr('9677f4cbd7aaf32ba9615416f7bd0991b7de1434a7fa2c31add25c3355ef3959'),
    signature=hexstr(
        'd1c49087103b631a58228bdf8fb70d4789259cf22d815e207660cfe8d478ad'
        'ad9c7affe587942203e08be1dc1e14c6dd5a8abd8640f328e45f667a91a7c06a06'
    ),
    message=models.BlockMessage(
        block_type=BlockType.COIN_TRANSFER.value,
        block_identifier=hexstr('d606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc'),
        block_number=0,
        timestamp=datetime.datetime(2021, 1, 1),
        signed_change_request=models.CoinTransferSignedChangeRequest(
            message=models.CoinTransferSignedChangeRequestMessage(
                balance_lock=hexstr('cb0467e380e032881e3f5c26878da3584f1dc1f2262ef77ba5e1fa7ef4b2821c'),
                txs=[
                    models.CoinTransferTransaction(
                        amount=54,
                        recipient=hexstr('8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff'),
                    ),
                    models.CoinTransferTransaction(
                        amount=5,
                        recipient=hexstr('4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'),
                        fee=True,
                    ),
                    models.CoinTransferTransaction(
                        amount=1,
                        recipient=hexstr('1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a'),
                        fee=True,
                    )
                ]
            ),
            signature=hexstr(
                'ae74562897f228a3d9bc388eba5037f34393e33813086c103bb5d6fc39a0'
                '23408655057f4ed8593c2d36bc98fb468112fdac186bec616ec2f2ba45c579c02108'
            ),
            signer=hexstr('cb0467e380e032881e3f5c26878da3584f1dc1f2262ef77ba5e1fa7ef4b2821c'),
        ),
        updated_account_states={
            hexstr('1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a'):
                models.AccountState(balance=1),
            hexstr('4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'):
                models.AccountState(balance=4),
            hexstr('8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff'):
                models.AccountState(balance=54),
        },
    ),
)

BLOCKCHAIN_STATE_SAMPLE = models.BlockchainState(
    account_states={
        hexstr('1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a'):
            models.AccountState(
                balance=1,
                balance_lock=hexstr('1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a'),
            ),  # noqa: E123
        hexstr('4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'):
            models.AccountState(
                balance=4,
                balance_lock=hexstr('4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'),
            ),  # noqa: E123
        hexstr('8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff'):
            models.AccountState(
                balance=54,
                balance_lock=hexstr('8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff'),
            ),  # noqa: E123
    },
    last_block_number=100,
    last_block_identifier=hexstr('d606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc'),
    last_block_timestamp=datetime.datetime(2021, 1, 1),
    next_block_identifier=hexstr('18266e8fb5fba0ca9a0078d799c73ca34512c229519b1d021b8c2b78ef5f70b7'),
)
