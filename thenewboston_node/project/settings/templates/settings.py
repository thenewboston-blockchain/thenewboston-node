# mypy: ignore-errors

DEBUG = True

SECRET_KEY = '90oqi[f[ohfipuuapugrp83yq09=40=oasdngkj'

MIDDLEWARE += ('thenewboston_node.core.middleware.LoggingMiddleware',)
LOGGING['formatters']['colored'] = {
    '()': 'colorlog.ColoredFormatter',
    'format': '%(log_color)s%(asctime)s %(levelname)s %(name)s %(bold_white)s%(message)s',
}
LOGGING['loggers']['thenewboston_node']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['console']['formatter'] = 'colored'

IS_LOCAL_SETTINGS_FILE_APPLIED = True

BLOCKCHAIN['kwargs']['base_directory'] = '<replace with absolute path to local/blockchain directory>'

NODE_SIGNING_KEY = '<replace with a value produced with `make generate-signing-key`>'
