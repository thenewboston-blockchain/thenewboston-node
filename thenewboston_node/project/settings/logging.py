LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'filters': {
        'sentry': {
            '()': 'thenewboston_node.core.logging.SentryFilter'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': [],
        },
        'pre_sentry_handler': {
            'level': 'DEBUG',
            'class': 'thenewboston_node.core.logging.FilteringNullHandler',
            'filters': ['sentry'],
        }
    },
    'loggers': {
        logger_name: {
            'level': 'INFO',
            'propagate': True,
        } for logger_name in (
            'django', 'django.request', 'django.db.backends', 'django.template', 'thenewboston_node',
            'thenewboston_node.core.logging', 'urllib3', 'asyncio'
        )
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}
