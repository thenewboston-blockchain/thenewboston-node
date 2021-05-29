from datetime import datetime
from unittest.mock import patch

from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.utils.iter import get_generator

USER_ACCOUNT_1 = 'a1e9104e964be38c592326792486cb70e6cde42081f4b38c0a4355a79aba254b'
USER_ACCOUNT_2 = 'a5aa1b3dadbef7b31a6bd2ff11139fc4e4b4a691a5ae9dfe69f6ba6bd01dde28'

initial_arf = factories.InitialAccountRootFileFactory(
    accounts={USER_ACCOUNT_1: factories.AccountBalanceFactory(
        balance=1000,
        balance_lock=USER_ACCOUNT_1,
    )}
)

block_0 = factories.BlockFactory(
    message=factories.BlockMessageFactory(
        block_number=0,
        block_identifier='fake-block-identifier-0',
        timestamp=datetime(2021, 1, 1),
        transfer_request=factories.CoinTransferSignedRequestFactory(
            signer=USER_ACCOUNT_1,
            message=factories.CoinTransferSignedRequestMessageFactory(
                balance_lock=USER_ACCOUNT_1,
                txs=[
                    factories.CoinTransferTransactionFactory(
                        recipient=USER_ACCOUNT_2,
                        amount=99,
                    ),
                ]
            ),
        ),
        updated_balances={
            USER_ACCOUNT_1: factories.BlockAccountBalanceFactory(
                balance=901,
                balance_lock='user-account-1-lock',
            ),
            USER_ACCOUNT_2: factories.BlockAccountBalanceFactory(
                balance=99,
                balance_lock=None,
            )
        }
    ),
    message_hash='fake-message-hash',
)


def test_generate_root_account_file(blockchain_base):
    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))

    with arf_patch, block_patch:
        generated_arf = blockchain_base.generate_account_root_file()

    assert generated_arf == factories.AccountRootFileFactory(
        accounts={
            USER_ACCOUNT_1: factories.AccountBalanceFactory(
                balance=901,
                balance_lock='user-account-1-lock',
            ),
            USER_ACCOUNT_2: factories.AccountBalanceFactory(
                balance=99,
                balance_lock=USER_ACCOUNT_2,
            )
        },
        last_block_number=0,
        last_block_identifier=block_0.message.block_identifier,
        last_block_timestamp=block_0.message.timestamp,
        next_block_identifier=block_0.message_hash,
    )
