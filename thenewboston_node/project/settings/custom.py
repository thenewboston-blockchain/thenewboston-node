# File for Node-specific logic settings
SENTRY_DSN = None
IS_LOCAL_SETTINGS_FILE_APPLIED = False
TEST_WITH_ENV_VARS = False
SIGNING_KEY = NotImplemented

NETWORK = {
    'class': 'thenewboston_node.business_logic.network.tcp_network.TCPNetwork',
    'kwargs': {},
}

MEMO_MAX_LENGTH = 64
