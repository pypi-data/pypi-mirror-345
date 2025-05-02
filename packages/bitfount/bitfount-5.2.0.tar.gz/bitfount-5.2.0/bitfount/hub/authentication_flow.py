"""Authentication flow and session management."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import threading
from typing import TYPE_CHECKING, Optional

import requests

from bitfount import config
from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _SANDBOX_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from bitfount.exceptions import BitfountError
from bitfount.hub.authentication_handlers import (
    _DEVELOPMENT_AUTH_DOMAIN,
    _DEVELOPMENT_CLIENT_ID,
    _PRODUCTION_AUTH_DOMAIN,
    _PRODUCTION_CLIENT_ID,
    _SANDBOX_AUTH_DOMAIN,
    _SANDBOX_CLIENT_ID,
    _STAGING_AUTH_DOMAIN,
    _STAGING_CLIENT_ID,
    AuthenticationHandler,
    DeviceCodeFlowHandler,
)
from bitfount.hub.types import (
    _DEV_AM_URL,
    _DEV_HUB_URL,
    _SANDBOX_AM_URL,
    _SANDBOX_HUB_URL,
    _STAGING_AM_URL,
    _STAGING_HUB_URL,
    PRODUCTION_AM_URL,
    PRODUCTION_HUB_URL,
    SMARTOnFHIRAccessToken,
)
from bitfount.utils import delegates
from bitfount.utils.web_utils import _auto_retry_request

if TYPE_CHECKING:
    from requests import Response

    from bitfount.hub.api import SMARTOnFHIR

logger = logging.getLogger(__name__)

# This forces `requests` to make IPv4 connections
# TODO: [BIT-1443] Remove this once Hub/AM support IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore[attr-defined] # Reason: see above # noqa: E501

_HUB_URLS: list[str] = [
    PRODUCTION_HUB_URL,
    _STAGING_HUB_URL,
    _SANDBOX_HUB_URL,
    _DEV_HUB_URL,
]
_AM_URLS: list[str] = [PRODUCTION_AM_URL, _STAGING_AM_URL, _SANDBOX_AM_URL, _DEV_AM_URL]


@dataclass
class _AuthEnv:
    """Captures the combined authorisation information."""

    name: str
    auth_domain: str
    client_id: str


def _get_auth_environment() -> _AuthEnv:
    """Determines the auth settings based on environment variables.

    Returns:
        A tuple containing the auth domain and client ID for the given environment.
    """
    environment = _get_environment()
    if environment == _STAGING_ENVIRONMENT:
        return _AuthEnv("staging", _STAGING_AUTH_DOMAIN, _STAGING_CLIENT_ID)
    if environment == _DEVELOPMENT_ENVIRONMENT:
        return _AuthEnv("development", _DEVELOPMENT_AUTH_DOMAIN, _DEVELOPMENT_CLIENT_ID)
    if environment == _SANDBOX_ENVIRONMENT:
        return _AuthEnv("sandbox", _SANDBOX_AUTH_DOMAIN, _SANDBOX_CLIENT_ID)
    return _AuthEnv("production", _PRODUCTION_AUTH_DOMAIN, _PRODUCTION_CLIENT_ID)


class AuthEnvironmentError(BitfountError):
    """Exception related to the authorization and authentication environment."""

    pass


@delegates()
class BitfountSession(requests.Session):
    """Manages session-based interactions with Bitfount.

    Extends `requests.Session`, appending an access token to the
    authorization of any requests made if an access token is present

    When the token expires it will request a new token prior to
    sending the web request.

    Usage:
        `session = BitfountSession(...)`
        # When you want the user to interact to start the session:
        `session.authenticate()`
        # The session can then be used as a normal requests.Session


    Properties:
        username: Username of the authenticated user

    """

    def __init__(
        self,
        authentication_handler: Optional[AuthenticationHandler] = None,
    ):
        super().__init__()

        self._reauthentication_lock = threading.Lock()

        self.authentication_handler = (
            authentication_handler
            if authentication_handler
            else DeviceCodeFlowHandler()
        )

    @property
    def username(self) -> str:
        """Returns the username of the authenticated user."""
        return self.authentication_handler.username

    @property
    def message_service_metadata(self) -> list[tuple[str, str]]:
        """Returns metadata for authenticating with message service."""
        with self._reauthentication_lock:
            if not self.authenticated:
                self.authenticate()

            return self.authentication_handler.message_service_request_metadata

    @property
    def hub_request_headers(self) -> dict:
        """Returns metadata for authenticating with message service."""
        with self._reauthentication_lock:
            if not self.authenticated:
                self.authenticate()
            return self.authentication_handler.hub_request_headers

    @property
    def am_request_headers(self) -> dict:
        """Returns metadata for authenticating with message service."""
        with self._reauthentication_lock:
            if not self.authenticated:
                self.authenticate()

            return self.authentication_handler.am_request_headers

    @property
    def authenticated(self) -> bool:
        """Returns true if we have an unexpired access token or API Keys."""
        return self.authentication_handler.authenticated

    @staticmethod
    def _is_url_in_urls(url: str, urls: list[str]) -> bool:
        """Returns true if the given `url` is in the list of `urls`.

        This includes if `url` points to a particular resource/page/endpoint etc. for
        a url present in `urls`.
        """
        for _url in urls:
            if url.startswith(_url):
                return True

        return False

    @classmethod
    def _is_hub_url(cls, url: str) -> bool:
        """Returns whether the provided url is a Bitfount Hub URL."""
        return cls._is_url_in_urls(url, _HUB_URLS)

    @classmethod
    def _is_am_url(cls, url: str) -> bool:
        """Returns whether the provided url is a Bitfount AM URL."""
        return cls._is_url_in_urls(url, _AM_URLS)

    def authenticate(self) -> None:
        """Authenticates user to allow protected requests.

        Prompts the user to login/authenticate and stores the tokens to use them
        in future requests.

        Raises:
            AssertionError: If user storage path corresponds to a different username
                from the BitfountSession.
            ConnectionError: If a token cannot be retrieved.
        """
        logger.debug("Calling authenticate on authentication handler")
        self.authentication_handler.authenticate()

    # We only wrap this method in _auto_retry_request as any calls to the others
    # (post, get, etc) will make use of this. Wrapping them all would result in
    # a double retry loop, but we can't _not_ wrap request as it is often used
    # directly.
    @_auto_retry_request
    def request(  # type: ignore[no-untyped-def,override]
        self, method, url, params=None, data=None, headers=None, **kwargs
    ) -> Response:
        """Performs an HTTP request.

        Overrides requests.session.request, appending our access token
        to the request headers or API keys if present.
        """
        # Create headers if they don't exist already
        if not headers:
            headers = {}

        is_am_url = self._is_am_url(url)
        is_hub_url = self._is_hub_url(url)

        if is_am_url or is_hub_url:
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_authentication_headers:
                logger.debug(f"Adding authentication to request headers for {url}")

            if is_hub_url:
                headers.update(self.hub_request_headers)
            elif is_am_url:
                headers.update(self.am_request_headers)

        return super().request(
            method, url, params=params, data=data, headers=headers, **kwargs
        )


class BearerAuthSession(requests.Session):
    """Session implementation that uses bearer authentication and auto-retry."""

    def __init__(
        self,
        bearer_token: str,
    ):
        super().__init__()
        self.token = bearer_token

    # We only wrap this method in _auto_retry_request as any calls to the others
    # (post, get, etc) will make use of this. Wrapping them all would result in
    # a double retry loop, but we can't _not_ wrap request as it is often used
    # directly.
    @_auto_retry_request
    def request(  # type: ignore[no-untyped-def,override]
        self, method, url, params=None, data=None, headers=None, **kwargs
    ) -> Response:
        """Performs an HTTP request.

        Overrides requests.session.request, appending our access token
        to the request headers or API keys if present.
        """
        # Create headers if they don't exist already
        if not headers:
            headers = {}

        headers["authorization"] = f"Bearer {self.token}"

        return super().request(
            method, url, params=params, data=data, headers=headers, **kwargs
        )


class NextGenAuthSession(requests.Session):
    """Session that uses bearer authentication and auto-retry for NextGen APIs.

    Differs from BearerAuthSession in that it contains functionality to auto-retrieve
    a new NextGen token from SMARTOnFHIR if the other is found to be expired.
    """

    def __init__(
        self,
        smart_on_fhir: SMARTOnFHIR,
    ):
        super().__init__()
        self.smart_on_fhir = smart_on_fhir
        self._token: Optional[SMARTOnFHIRAccessToken] = None

    @property
    def token(self) -> str:
        """Returns the current NextGen token or gets one if necessary."""
        if self._token is None:
            self._token = self.smart_on_fhir.get_access_token()
        return self._token.token

    # We only wrap this method in _auto_retry_request as any calls to the others
    # (post, get, etc) will make use of this. Wrapping them all would result in
    # a double retry loop, but we can't _not_ wrap request as it is often used
    # directly.
    @_auto_retry_request
    def request(  # type: ignore[no-untyped-def,override]
        self, method, url, params=None, data=None, headers=None, **kwargs
    ) -> Response:
        """Performs an HTTP request.

        Overrides requests.session.request, appending our access token
        to the request headers or API keys if present.
        """
        # Create headers if they don't exist already
        if not headers:
            headers = {}

        headers["authorization"] = f"Bearer {self.token}"

        # Try the request once
        resp = super().request(
            method, url, params=params, data=data, headers=headers, **kwargs
        )
        # If we get a 401 (which could indicate token expired), we'll get a new token
        # and retry; otherwise, just return the response
        if resp.status_code != 401:
            return resp
        else:
            # Do some sanity checking; auth failures seem to have body
            # "invalid access token" so we should check this
            if (resp_body := resp.text) == "invalid access token":
                logger.warning(
                    "NextGen response was 401: invalid access token,"
                    " refreshing from SMART on FHIR..."
                )
            else:
                if len(resp_body) <= 40:
                    body_log_str = resp_body
                else:
                    body_log_str = f"{resp_body[:40]}... (truncated)"
                logger.warning(
                    f"NextGen response was 401, but body didn't indicate expired token."
                    f" Attempting to refresh token from SMART on FHIR anyway..."
                    f" Body was: {body_log_str}"
                )

            self._token = None  # Clear the old token to force a new one to be fetched
            headers["authorization"] = f"Bearer {self.token}"
            return super().request(
                method, url, params=params, data=data, headers=headers, **kwargs
            )
