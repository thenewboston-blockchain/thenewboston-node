import logging
from itertools import chain, islice
from typing import Iterable, Optional, cast

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.logging import validates

from ...models.block import Block

logger = logging.getLogger(__name__)


class ValidationMixin:

    @validates('BLOCKCHAIN')
    def validate(self, is_partial_allowed: bool = True):
        self.validate_account_root_files(is_partial_allowed=is_partial_allowed)
        self.validate_blocks()

    @validates('account root files', is_plural_target=True)
    def validate_account_root_files(self, is_partial_allowed: bool = True):
        account_root_files_iter = self.iter_account_root_files()  # type: ignore
        with validates('number of account root files (at least one)'):
            try:
                first_account_root_file = next(account_root_files_iter)
            except StopIteration:
                raise ValidationError('Blockchain must contain at least one account root file')

        is_initial = first_account_root_file.is_initial()
        if not is_partial_allowed and not is_initial:
            raise ValidationError('Blockchain must start with initial account root file')

        is_first = True
        for counter, account_root_file in enumerate(chain((first_account_root_file,), account_root_files_iter)):
            with validates(f'account root file number {counter}'):
                self.validate_account_root_file(
                    account_root_file=account_root_file, is_initial=is_initial, is_first=is_first
                )

            is_initial = False  # only first iteration can be with initial
            is_first = False

    @validates('account root file (last_block_number={account_root_file.last_block_number})')
    def validate_account_root_file(self, *, account_root_file, is_initial=False, is_first=False):
        account_root_file.validate(is_initial=is_initial)
        if is_initial:
            return

        if is_first:
            logger.debug('First account root file is not a subject of further validations')
            return

        self.validate_account_root_file_balances(account_root_file=account_root_file)

        first_block = self.get_first_block()  # type: ignore
        if not first_block:
            return

        if first_block.message.block_number > account_root_file.last_block_number:
            logger.debug('First block is after the account root file')
            if first_block.message.block_number > account_root_file.last_block_number + 1:
                logger.warning('Unnecessary old account root file detected')

            return

        # If account root file is after first known block then we can validate its attributes
        account_root_file_last_block = self.get_block_by_number(account_root_file.last_block_number)  # type: ignore
        with validates('account root file last_block_number'):
            if account_root_file_last_block is None:
                raise ValidationError('Account root file last_block_number points to non-existing block')

        with validates('account root file last_block_identifier'):
            if account_root_file_last_block.message.block_identifier != account_root_file.last_block_identifier:
                raise ValidationError('Account root file last_block_number does not match last_block_identifier')

        with validates('account root file next_block_identifier'):
            if account_root_file_last_block.message_hash != account_root_file.next_block_identifier:
                raise ValidationError(
                    'Account root file next_block_identifier does not match last_block_number message hash'
                )

    @validates(
        'account root file balances (last_block_number={account_root_file.last_block_number})', is_plural_target=True
    )
    def validate_account_root_file_balances(self, *, account_root_file):
        generated_account_root_file = self.generate_account_root_file(
            account_root_file.last_block_number
        )  # type: ignore
        with validates('number of account root file balances'):
            expected_accounts_count = len(generated_account_root_file.account_states)
            actual_accounts_count = len(account_root_file.account_states)
            if expected_accounts_count != actual_accounts_count:
                raise ValidationError(
                    f'Expected {expected_accounts_count} accounts, '
                    f'but got {actual_accounts_count} in the account root file'
                )

        actual_accounts = account_root_file.account_states
        for account_number, account_state in generated_account_root_file.account_states.items():
            with validates(f'account {account_number} existence'):
                actual_account_state = actual_accounts.get(account_number)
                if actual_account_state is None:
                    raise ValidationError(f'Could not find {account_number} account in the account root file')

            with validates(f'account {account_number} balance value'):
                expect_balance = account_state.balance
                actual_state = actual_account_state.balance
                if actual_state != expect_balance:
                    raise ValidationError(
                        f'Expected {expect_balance} balance value, '
                        f'but got {actual_state} balance value for account {account_number}'
                    )

            with validates(f'account {account_number} balance lock'):
                expect_lock = account_state.balance_lock
                actual_lock = actual_account_state.balance_lock
                if actual_lock != expect_lock:
                    raise ValidationError(
                        f'Expected {expect_lock} balance lock, but got {actual_lock} balance '
                        f'lock for account {account_number}'
                    )

    @validates('blockchain blocks (offset={offset}, limit={limit})', is_plural_target=True, use_format_map=True)
    def validate_blocks(self, *, offset: int = 0, limit: Optional[int] = None):
        """
        Validate blocks persisted in the blockchain. Some blockchain level validations may overlap with
        block level validations. We consider it OK since it is better to double check something rather
        than miss something. We may reconsider this overlap in favor of validation performance.
        """
        assert offset >= 0

        blocks_iter = cast(Iterable[Block], self.iter_blocks())  # type: ignore
        if offset > 0 or limit is not None:
            # TODO(dmu) HIGH: Consider performance improvements when slicing
            if limit is None:
                blocks_iter = islice(blocks_iter, offset)
            else:
                blocks_iter = islice(blocks_iter, offset, offset + limit)

        try:
            first_block = next(blocks_iter)  # type: ignore
        except StopIteration:
            return

        first_account_root_file = self.get_first_account_root_file()  # type: ignore
        if first_account_root_file is None:
            raise ValidationError('Account root file prior to first block is not found')

        first_block_number = first_block.message.block_number
        if offset == 0:
            with validates('basing on an account root file'):

                if first_account_root_file.get_next_block_number() != first_block_number:
                    raise ValidationError('First block number does not match base account root file last block number')

                if first_account_root_file.get_next_block_identifier() != first_block.message.block_identifier:
                    raise ValidationError(
                        'First block identifier does not match base account root file last block identifier'
                    )

            expected_block_identifier = first_account_root_file.get_next_block_identifier()
        else:
            prev_block = self.get_block_by_number(first_block_number - 1)  # type: ignore
            if prev_block is None:
                raise ValidationError(f'Previous block for block number {first_block_number} is not found')

            assert prev_block.message_hash
            expected_block_identifier = prev_block.message_hash

        expected_block_number = first_account_root_file.get_next_block_number() + offset
        for block in chain((first_block,), blocks_iter):
            block.validate(self)

            assert block.message

            self.validate_block(
                block=block,
                expected_block_number=expected_block_number,
                expected_block_identifier=expected_block_identifier
            )
            expected_block_number += 1
            expected_block_identifier = block.message_hash

    @validates(
        'block number {block.message.block_number} (identifier: block.message.block_identifier) '
        'on blockchain level'
    )
    def validate_block(self, *, block: Block, expected_block_number: int, expected_block_identifier: str):
        actual_block_number = block.message.block_number
        actual_block_identifier = block.message.block_identifier

        if actual_block_number != expected_block_number:
            raise ValidationError(f'Expected block number {expected_block_number} but got {actual_block_number}')

        if actual_block_identifier != expected_block_identifier:
            raise ValidationError(
                f'Expected block identifier {expected_block_identifier} but got {actual_block_identifier}'
            )
