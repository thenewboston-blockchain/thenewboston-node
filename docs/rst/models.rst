
Models
******

**class thenewboston_node.business_logic.models.AccountBalance(value,
lock)**

   Account balance state

   ``value: int``

      Amount balance value in coins

   ``lock: str``

      Account balance lock

**class
thenewboston_node.business_logic.models.BlockAccountBalance(value:
int, lock: Optional[str] = None)**

   Bases:
   ``thenewboston_node.business_logic.models.account_balance.AccountBalance``

**class
thenewboston_node.business_logic.models.AccountRootFile(accounts,
last_block_number=None, last_block_identifier=None,
last_block_timestamp=None, next_block_identifier=None)**

   Historical snapshot of all account balances at any point in time

   ``accounts: dict``

      Dict like {“*account_number*”: *AccountBalance*, …}

   ``last_block_number: Optional[int] = None``

      Block number at which snapshot was taken

   ``last_block_identifier: Optional[str] = None``

      Block identifier at which snapshot was taken

   ``last_block_timestamp: Optional[datetime.datetime] = None``

      Naive datetime in UTC

   ``next_block_identifier: Optional[str] = None``

      Next block identifier

**class thenewboston_node.business_logic.models.Block(node_identifier,
message, message_hash=None, message_signature=None)**

   Blocks represent a description of change to the network. These
   originate from signed requests and may include:

      *  a transfer of coins between accounts

      *  the registration of a username

      *  a new node being added to the network

      *  etc…

   ``node_identifier: str``

      Public key of a node signed the block

   ``message:
   thenewboston_node.business_logic.models.block_message.BlockMessage``

      Block payload

   ``message_hash: Optional[str] = None``

      Hash value of message field

   ``message_signature: Optional[str] = None``

      The signature of the node indicating the validity of the block

**class
thenewboston_node.business_logic.models.BlockMessage(transfer_request,
timestamp, block_number, block_identifier, updated_balances)**

   Contains requested changes in the network like transfer of coins,
   etc…

   ``transfer_request: thenewboston_node.bus ...
   request.TransferRequest``

      Requested changes

   ``timestamp: datetime.datetime``

      Block timestamp in UTC

   ``block_number: int``

      Sequential block number

   ``block_identifier: str``

      Unique block identifier

   ``updated_balances: dict``

      New account balance values like {“*account_number*”:
      *BlockAccountBalance*, …}

**class thenewboston_node.business_logic.models.Node(identifier: str,
fee_amount: int, type_: str)**

   ``identifier: str``

      Node’s public key

   ``fee_amount: int``

      Validation fee taking by the node

   ``type_: str``

      Node type

**class
thenewboston_node.business_logic.models.RegularNode(identifier: str,
fee_amount: int, type_: str = 'REGULAR_NODE')**

   Bases: ``thenewboston_node.business_logic.models.node.Node``

**class
thenewboston_node.business_logic.models.PrimaryValidator(identifier:
str, fee_amount: int, type_: str = 'PRIMARY_VALIDATOR')**

   Bases: ``thenewboston_node.business_logic.models.node.Node``

**class thenewboston_node.business_logic.models.Transaction(recipient,
amount, fee=None, memo=None)**

   Coin transfer between accounts

   ``recipient: str``

      Recipient’s account number

   ``amount: int``

      Coins being sent to the recipient

   ``fee: Optional[bool] = None``

      True if transaction is fee

   ``memo: Optional[str] = None``

      Optional memo

**class
thenewboston_node.business_logic.models.TransferRequest(sender,
message, message_signature=None)**

   Coin transfer request signed by the sender

   ``sender: str``

      Sender’s account number

   ``message: thenewboston_node.bus ... .TransferRequestMessage``

      Transfer request payload

   ``message_signature: Optional[str] = None``

      Sender’s signature of the message

**class
thenewboston_node.business_logic.models.TransferRequestMessage(balance_lock,
txs)**

   Coin transfer request message

   ``balance_lock: str``

      Current sender’s balance lock

   ``txs: list``

      List of *Transaction* objects
