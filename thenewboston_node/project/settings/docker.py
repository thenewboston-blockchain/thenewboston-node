from thenewboston_node.core.utils.docker import is_in_docker

if is_in_docker():
    # We need it to serve static files with DEBUG=False
    assert MIDDLEWARE[:1] == [  # noqa: F821
        'django.middleware.security.SecurityMiddleware'
    ]
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # noqa: F821
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
