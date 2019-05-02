from collections import OrderedDict
from functools import wraps
from flask import _request_ctx_stack, current_app, jsonify, request
from werkzeug.local import LocalProxy
from cognitojwt import CognitoJWTException, decode as cognito_jwt_decode
import logging

log = logging.getLogger(__name__)

CONFIG_DEFAULTS = {
    "COGNITO_CHECK_TOKEN_EXPIRATION": True,
    "COGNITO_JWT_HEADER_NAME": "Authorization",
    "COGNITO_JWT_HEADER_PREFIX": "Bearer",
}

# user from pool
current_cognito_jwt = LocalProxy(
    lambda: getattr(_request_ctx_stack.top, "cogauth_cognito_jwt", None)
)

# unused - could be a way to add mapping of cognito user to application user
current_user = LocalProxy(
    lambda: getattr(_request_ctx_stack.top, "cogauth_current_user", None)
)

# access initialized cognito extension
_cog = LocalProxy(lambda: current_app.extensions["cognito_auth"])


class CognitoAuthError(Exception):
    def __init__(self, error, description, status_code=401, headers=None):
        self.error = error
        self.description = description
        self.status_code = status_code
        self.headers = headers

    def __repr__(self):
        return f"CognitoAuthError: {self.error}"

    def __str__(self):
        return f"{self.error} - {self.description}"


class CognitoAuth(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app, identity_handler=None):
        for k, v in CONFIG_DEFAULTS.items():
            app.config.setdefault(k, v)

        # required configuration
        self.region = self._get_required_config(app, "COGNITO_REGION")
        self.userpool_id = self._get_required_config(app, "COGNITO_USERPOOL_ID")
        self.jwt_header_name = self._get_required_config(app, "COGNITO_JWT_HEADER_NAME")
        self.jwt_header_prefix = self._get_required_config(
            app, "COGNITO_JWT_HEADER_PREFIX"
        )

        self.identity_callback = identity_handler

        # optional configuration
        self.check_expiration = app.config.get("COGNITO_CHECK_TOKEN_EXPIRATION", True)
        self.app_client_id = app.config.get("COGNITO_APP_CLIENT_ID")

        # save for localproxy
        app.extensions["cognito_auth"] = self

        # handle CognitoJWTExceptions
        # TODO: make customizable
        app.errorhandler(CognitoAuthError)(self._cognito_auth_error_handler)

    def _get_required_config(self, app, config_name):
        val = app.config.get(config_name)
        if not val:
            raise Exception(
                f"{config_name} not found in app configuration but it is required."
            )
        return val

    def identity_handler(self, callback):
        if self.identity_callback is not None:
            raise Exception(
                f"Trying to override existing identity_handler on CognitoAuth. You should only set this once."
            )
        self.identity_callback = callback
        return callback

    def get_token(self):
        """Get token from request."""
        auth_header_name = _cog.jwt_header_name
        auth_header_prefix = _cog.jwt_header_prefix

        # get token value from header
        auth_header_value = request.headers.get(auth_header_name)

        if not auth_header_value:
            # no auth header found
            return None

        parts = auth_header_value.split()

        if parts[0].lower() != auth_header_prefix.lower():
            raise CognitoAuthError(
                "Invalid Cognito JWT header",
                f'Unsupported authorization type. Header prefix "{parts[0].lower()}" does not match "{auth_header_prefix.lower()}"',
            )
        elif len(parts) == 1:
            raise CognitoAuthError("Invalid Cognito JWT header", "Token missing")
        elif len(parts) > 2:
            raise CognitoAuthError(
                "Invalid Cognito JWT header", "Token contains spaces"
            )

        return parts[1]

    def get_user(self, jwt_payload):
        """Get application user identity from Cognito JWT payload."""
        if not self.identity_callback:
            return None
        return self.identity_callback(jwt_payload)

    def _cognito_auth_error_handler(self, error):
        log.exception(error)
        return (
            jsonify(
                OrderedDict(
                    [("error", error.error), ("description", error.description)]
                )
            ),
            error.status_code,
            error.headers,
        )

    def decode_token(self, token):
        """Decode token."""
        return cognito_jwt_decode(
            token=token,
            region=self.region,
            app_client_id=self.app_client_id,
            userpool_id=self.userpool_id,
            testmode=not self.check_expiration,
        )


def load_jwt_tokens():
    token = _cog.get_token()

    if token:
        try:
            # check if token is signed by userpool
            payload = _cog.decode_token(token=token)
        except CognitoJWTException as e:
            log.exception(e)
            raise CognitoAuthError(
                "Invalid Cognito Authentication Token", str(e)
            ) from e
        current_user = _cog.get_user(payload)
    else:
        current_user = None
        payload = None
    _request_ctx_stack.top.cogauth_cognito_jwt = payload
    _request_ctx_stack.top.cogauth_current_user = current_user


def cognito_auth_required(fn):
    """View decorator that requires a valid Cognito JWT token to be present in the request."""

    @wraps(fn)
    def decorator(*args, **kwargs):
        _cognito_auth_required()
        return fn(*args, **kwargs)

    return decorator


def _cognito_auth_required():
    """Does the actual work of verifying the Cognito JWT data in the current request.
    This is done automatically for you by `cognito_jwt_required()` but you could call it manually.
    Doing so would be useful in the context of optional JWT access in your APIs.
    """
    token = _cog.get_token()

    if token is None:
        auth_header_name = _cog.jwt_header_name
        auth_header_prefix = _cog.jwt_header_prefix
        raise CognitoAuthError(
            "Authorization Required",
            f'Request does not contain a well-formed access token in the "{auth_header_name}" header beginning with "{auth_header_prefix}"',
        )

    try:
        # check if token is signed by userpool
        payload = _cog.decode_token(token=token)
    except CognitoJWTException as e:
        log.exception(e)
        raise CognitoAuthError("Invalid Cognito Authentication Token", str(e)) from e

    _request_ctx_stack.top.cogauth_cognito_jwt = payload
    _request_ctx_stack.top.cogauth_current_user = _cog.get_user(payload)
