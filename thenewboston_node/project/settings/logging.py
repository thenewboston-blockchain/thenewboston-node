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
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['sentry'],
        },
        'pre_sentry_handler': {
            'level': 'DEBUG',
            'class': 'thenewboston_node.core.logging.FilteringNullHandler',
            'filters': ['sentry'],
        }
    },
    'loggers': {
        logger_name: {
            'level': 'WARNING',
            'propagate': True,
        } for logger_name in (
            'django', 'django.request', 'django.db.backends', 'django.template', 'thenewboston_node', 'urllib3',
            'asyncio'
        )
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'pre_sentry_handler'],
    }
}
