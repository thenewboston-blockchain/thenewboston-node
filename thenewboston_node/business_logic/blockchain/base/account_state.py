import logging
from typing import Optional

from thenewboston_node.business_logic.models import AccountState
from thenewboston_node.core.logging import timeit_method
from thenewboston_node.core.utils.types import hexstr

from .base import BaseMixin

logger = logging.getLogger(__name__)


class AccountStateMixin(BaseMixin):

    def yield_known_accounts(self):
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

    def yield_account_states(self, from_block_number: Optional[int] = None):
        # TODO(dmu) HIGH: Reuse this method where
        block_number = self.get_last_block_number() if from_block_number is None else from_block_number
        if block_number == -1:
            yield from self.get_first_blockchain_state().yield_account_states()
            return

        blockchain_state = self.get_blockchain_state_by_block_number(block_number, inclusive=True)
        # TODO(dmu) CRITICAL: yield blocks it blockchain_state.last_block number to prevent race conditions
        for block in self.yield_blocks_till_snapshot(from_block_number=from_block_number):
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

    def get_account_balance(self, account: hexstr, on_block_number: int) -> int:
        return self.get_account_state_attribute_value(account, 'balance', on_block_number)

    def get_account_current_balance(self, account: str) -> int:
        return self.get_account_balance(account, self.get_last_block_number())  # type: ignore

    def get_account_balance_lock(self, account: hexstr, on_block_number: int) -> hexstr:
        return self.get_account_state_attribute_value(account, 'balance_lock', on_block_number)

    def get_account_current_balance_lock(self, account: hexstr) -> hexstr:
        return self.get_account_balance_lock(account, self.get_last_block_number())  # type: ignore

    def get_account_state(self, account: hexstr) -> AccountState:
        block_number = self.get_last_block_number()  # type: ignore
        return AccountState(
            balance=self.get_account_balance(account, block_number),
            balance_lock=self.get_account_balance_lock(account, block_number),
            node=self.get_node_by_identifier(account, block_number),
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
            return self.get_first_blockchain_state().get_next_block_identifier()

        blockchain_state = self.get_blockchain_state_by_block_number(prev_block_number, inclusive=True)
        if blockchain_state.get_last_block_number() == prev_block_number:
            return blockchain_state.get_next_block_identifier()

        block = self.get_block_by_number(prev_block_number)
        assert block is not None
        return block.hash
