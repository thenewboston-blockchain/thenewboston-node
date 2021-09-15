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

FASTER_UNITTESTS = True
NODE_SIGNING_KEY = '0000000000000000000000000000000000000000000000000000000000000000'
