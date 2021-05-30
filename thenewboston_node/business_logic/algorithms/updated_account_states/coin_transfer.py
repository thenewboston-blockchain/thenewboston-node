from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import AccountState, CoinTransferSignedChangeRequest


def make_balance_lock(signed_change_request):
    assert signed_change_request.message
    return signed_change_request.message.get_hash()


def get_updated_account_states_for_coin_transfer(
    signed_change_request: CoinTransferSignedChangeRequest, blockchain: BlockchainBase
) -> dict[str, AccountState]:
    updated_account_states: dict[str, AccountState] = {}
    sent_amount = 0
    for transaction in signed_change_request.message.txs:
        recipient = transaction.recipient
        amount = transaction.amount

        account_state = updated_account_states.get(recipient)
        if account_state is None:
            account_state = AccountState(balance=blockchain.get_account_balance(recipient) or 0)
            updated_account_states[recipient] = account_state

        assert account_state.balance is not None
        account_state.balance += amount
        sent_amount += amount

    coin_sender = signed_change_request.signer
    sender_balance = blockchain.get_account_balance(coin_sender)
    assert sender_balance is not None
    assert sender_balance >= sent_amount

    updated_account_states[coin_sender] = AccountState(
        balance=sender_balance - sent_amount, balance_lock=make_balance_lock(signed_change_request)
    )

    return updated_account_states
