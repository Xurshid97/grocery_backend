<!-- in production be careful with CORS settings and secure cookie flags,
     and ensure that the `DEBUG` setting is set to `False`.
        This is a development configuration.
        For production, you should set `ALLOWED_HOSTS` to your domain or IP address,
        enable HTTPS, and configure CORS appropriately.
        Also, consider using environment variables for sensitive settings.
        Make sure to test thoroughly before deploying.
        The `samesite` attribute for cookies should be set according to your security requirements.
        For example, `samesite="None"` is often used for cross-site requests,
        but it requires `secure=True` and HTTPS.
        The `corsheaders` middleware is included to handle CORS requests.
        The `django_extensions` and `sslserver` apps are included for development convenience.
        The `CommonMiddleware` is included to handle common HTTP headers.
        The `django.middleware.common.CommonMiddleware` is included twice, which is redundant.
        You should remove one of them to avoid confusion.
        The `refresh_token` cookie is set with `httponly=True` to prevent JavaScript access,
        and `secure=False` is set for development purposes, but should be `True
        in production.
        The `samesite` attribute for the `refresh_token` cookie is set to `None`
        to allow cross-site requests, but this should be set according to your security requirements.
        The `max_age` for the `refresh_token` cookie is set to 7 days.
        The `ALLOWED_HOSTS` setting is set to allow requests from `localhost` and `127.0.0.1`.
        -->
# settings.py
