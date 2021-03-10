# mypy: ignore-errors

DEBUG = True

SECRET_KEY = '90oqi[f[ohfipuuapugrp83yq09=40=oasdngkj'

MIDDLEWARE += ('thenewboston_node.core.middleware.LoggingMiddleware',)
LOGGING['loggers']['thenewboston_node']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'

IS_LOCAL_SETTINGS_FILE_APPLIED = True
