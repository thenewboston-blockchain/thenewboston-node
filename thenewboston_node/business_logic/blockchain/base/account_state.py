import logging
import warnings
from itertools import chain
from typing import Optional

from more_itertools import ilen

from thenewboston_node.business_logic.models import (
    AccountState, CoinTransferSignedChangeRequest, PrimaryValidatorSchedule
)
from thenewboston_node.core.logging import timeit_method
from thenewboston_node.core.utils.types import hexstr

from .base import BaseMixin

logger = logging.getLogger(__name__)


class AccountStateMixin(BaseMixin):

    def yield_known_accounts(self):
        # We keep this implementation because it is faster than using self.yield_account_states()
        known_accounts = set()
        for block in self.yield_blocks_till_snapshot():  # type: ignore
            block_accounts = set(block.message.updated_account_states.keys())
            new_accounts = block_accounts - known_accounts
            known_accounts |= new_accounts
            for new_account in new_accounts:
                yield new_account

        last_account_root_file = self.get_last_blockchain_state()  # type: ignore
        account_root_file_accounts = last_account_root_file.account_states.keys()
        new_accounts = account_root_file_accounts - known_accounts
        known_accounts |= new_accounts
        for new_account in new_accounts:
            yield new_account

    def get_number_of_accounts(self):
        warnings.warn('Low performance implementation of get_number_of_accounts() is being used')
        return ilen(self.yield_known_accounts())

    def yield_account_states(self, from_block_number: Optional[int] = None):
        # TODO(dmu) HIGH: Reuse this method where possible
        block_number = self.get_last_block_number() if from_block_number is None else from_block_number
        if block_number == -1:
            yield from self.get_first_blockchain_state().yield_account_states()
            return

        blockchain_state = self.get_blockchain_state_by_block_number(block_number, inclusive=True)
        for block in self.yield_blocks_slice_reversed(block_number, blockchain_state.last_block_number):
            yield from block.yield_account_states()

        yield from blockchain_state.yield_account_states()

    def get_account_state_attribute_value(self, account: hexstr, attribute: str, block_number: int):
        if block_number < -1:
            raise ValueError('block_number must be greater or equal to -1')
        elif block_number > self.get_last_block_number():  # type: ignore
            raise ValueError('block_number must be less than current block number')

        if block_number > -1:
            account_state = self._get_account_state_from_block(account, block_number, attribute)
            if account_state:
                return account_state.get_attribute_value(attribute, account)

            blockchain_state = self.get_blockchain_state_by_block_number(block_number, inclusive=True)
        else:
            assert block_number == -1
            blockchain_state = self.get_first_blockchain_state()

        return blockchain_state.get_account_state_attribute_value(account, attribute)

    @timeit_method(verbose_args=True)
    def get_account_balance(self, account: hexstr, on_block_number: int) -> int:
        return self.get_account_state_attribute_value(account, 'balance', on_block_number)

    @timeit_method(verbose_args=True)
    def get_account_current_balance(self, account: hexstr) -> int:
        return self.get_account_balance(account, self.get_last_block_number())  # type: ignore

    def get_account_balance_lock(self, account: hexstr, on_block_number: int) -> hexstr:
        return self.get_account_state_attribute_value(account, 'balance_lock', on_block_number)

    def get_account_current_balance_lock(self, account: hexstr) -> hexstr:
        return self.get_account_balance_lock(account, self.get_last_block_number())  # type: ignore

    def get_primary_validator_schedule(self, account: hexstr, on_block_number: int) -> PrimaryValidatorSchedule:
        return self.get_account_state_attribute_value(account, 'primary_validator_schedule', on_block_number)

    def get_account_state(self, account: hexstr) -> AccountState:
        block_number = self.get_last_block_number()  # type: ignore
        return AccountState(
            balance=self.get_account_balance(account, block_number),
            balance_lock=self.get_account_balance_lock(account, block_number),
            node=self.get_node_by_identifier(account, block_number),
            primary_validator_schedule=self.get_primary_validator_schedule(account, block_number),
        )

    @timeit_method()
    def _get_account_state_from_block(
        self,
        account: str,
        block_number: int,
        expected_attribute: str,
    ) -> Optional[AccountState]:
        for block in self.yield_blocks_till_snapshot(block_number):  # type: ignore
            account_state = block.message.get_account_state(account)
            if account_state is not None:
                value = getattr(account_state, expected_attribute, None)
                if value is not None:
                    return account_state

        return None

    def get_expected_block_identifier(self, block_number: int) -> Optional[str]:
        """
        Return expected block identifier (take from previous block message hash or account root file)
        for the `block_number` (from 0 to head block number + 1 inclusive).

        To be used for validation of existing and generation of new blocks.
        """
        if block_number < 0:
            raise ValueError('block_number must be greater or equal to 0')

        # We should try to find blockchain state first to support partial blockchains
        prev_block_number = block_number - 1
        if prev_block_number == -1:
            return self.get_first_blockchain_state().next_block_identifier

        blockchain_state = self.get_blockchain_state_by_block_number(prev_block_number, inclusive=True)
        if blockchain_state.last_block_number == prev_block_number:
            return blockchain_state.next_block_identifier

        block = self.get_block_by_number(prev_block_number)
        assert block is not None
        return block.hash

    # TODO: probably move to another new transaction related mixin
    # TODO: add caching implementation
    def yield_transactions(self, account_id, is_reversed=False):
        if is_reversed:
            blocks = self.yield_blocks_reversed()
        else:
            blocks = self.yield_blocks()
            # TODO: implement sync initialization or otherwise redirection of client to get the entire
            # list of transaction from somewhere else, for example from current PV
            try:
                first_block = next(blocks)
            except StopIteration:
                return

            if first_block.get_block_number() != 0:
                raise NotImplementedError('Yielding transactions from incomplete blockchain is not implemented')

            blocks = chain((first_block,), blocks)

        block = None
        for block in blocks:
            signed_change_request = block.message.signed_change_request
            if not isinstance(signed_change_request, CoinTransferSignedChangeRequest):
                continue

            signer = signed_change_request.signer
            for transaction in signed_change_request.message.txs:
                if account_id == signer or account_id == transaction.recipient:
                    yield transaction

        if is_reversed and block and block.get_block_number() != 0:
            # TODO: implement sync initialization or otherwise redirection of client to get the entire
            # list of transaction from somewhere else, for example from current PV
            raise NotImplementedError('Yielding transactions from incomplete blockchain is not implemented')
