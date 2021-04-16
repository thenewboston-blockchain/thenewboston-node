# File for Node-specific logic settings
SENTRY_DSN = None
IS_LOCAL_SETTINGS_FILE_APPLIED = False
TEST_WITH_ENV_VARS = False
SIGNING_KEY = NotImplemented
BLOCKCHAIN = {
    'class': 'thenewboston_node.business_logic.blockchain.file_blockchain.FileBlockchain',
    'kwargs': {},
}

NETWORK = {
    'class': 'thenewboston_node.business_logic.network.tcp_network.TCPNetwork',
    'kwargs': {},
}

AUTO_CREATE_ACCOUNT_ROOT_FILE_EVERY_BLOCKS = 100
