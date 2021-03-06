import os

if not SENTRY_DSN:  # noqa: F821
    SENTRY_DSN = os.getenv('SENTRY_DSN')

if SENTRY_DSN:
    import logging

    import sentry_sdk
    # TODO(dmu) HIGH: Enable Celery integration once Celery is added
    # from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    logging_integration = LoggingIntegration(
        level=logging.DEBUG,  # Breadcrumbs level
        event_level=SENTRY_EVENT_LEVEL,  # noqa: F821
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        debug=True,
        send_default_pii=True,
        # TODO(dmu) HIGH: Provide `release=...`,
        request_bodies='medium',
        integrations=(logging_integration, DjangoIntegration()),
    )
