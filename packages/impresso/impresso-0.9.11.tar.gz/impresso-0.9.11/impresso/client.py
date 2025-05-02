"""Impresso Python client library."""

import getpass
import importlib.metadata
import logging
import os
from urllib.parse import urlparse

import httpx

from impresso.api_client import AuthenticatedClient
from impresso.client_base import ImpressoApiResourcesBase
from impresso.config_file import DEFAULT_API_URL, ImpressoPyConfig
from impresso.util.token import get_jwt_status

logger = logging.getLogger(__name__)

version = importlib.metadata.version("impresso")


def _is_localhost_netloc(netloc: str) -> bool:
    return netloc.startswith("localhost") or netloc.startswith("127.0.0.1")


DEFAULT_LOCALHOST_TOKEN_NETLOC = "impresso-project.ch"


def _log_non_2xx(response: httpx.Response) -> None:
    if response.status_code >= 400:
        response.read()
        logging.error(
            f"Received error response ({response.status_code}): {response.text}"
        )


class ImpressoClient(ImpressoApiResourcesBase):
    """
    Client class for the impresso Python libary. This is the context for all
    interactions with the impresso API.
    """

    def __init__(self, api_url: str, api_bearer_token: str):
        self._api_url = api_url
        self._api_bearer_token = api_bearer_token
        super().__init__(
            AuthenticatedClient(
                base_url=self._api_url,
                token=self._api_bearer_token,
                headers={
                    "Accept": "application/json",
                    "User-Agent": f"impresso-py/${version}",
                },
                raise_on_unexpected_status=True,
                httpx_args={
                    "event_hooks": {
                        "response": [_log_non_2xx],
                    }
                },
            )
        )

    @property
    def api_url(self) -> str:
        """
        Return the Impresso Public API URL currently in use.
        """
        return self._api_url


_PROMPT = """
Click on the following link to access the login page: {URL}
 - 🔤 Enter your email/password on this page.
 - 🔑 Once logged in, a secret token will be generated for you.
 - 📋 Copy this token and paste it into the input field below. Then press "Enter". 👇🏼.
"""


def connect(
    public_api_url: str | None = None,
    persisted_token: bool = True,
) -> ImpressoClient:
    """
    Connect to the Impresso API and return a client object.

    ```python
    from impresso import connect

    impresso = connect()
    ```

    Args:
        public_api_url (str): The URL of the Impresso API to connect to. By default using the default URL set
                              in the config file (~/.impresso_py.yml) or the Impresso default URL ({DEFAULT_API_URL}).
        persisted_token (bool): Whether to read and write token to the user directory
                                (~/.impresso_py.yml).
                                This is useful to avoid having to re-enter the token each time the
                                Jupiter notebook is restarted.
    """

    config = ImpressoPyConfig()

    api_url = public_api_url or os.getenv("IMPRESSO_API_URL") or config.default_api_url

    parsed_url = urlparse(api_url)
    token_base_url_netloc = parsed_url.netloc
    if _is_localhost_netloc(token_base_url_netloc):
        token_base_url_netloc = DEFAULT_LOCALHOST_TOKEN_NETLOC

    token_base_url = f"https://{token_base_url_netloc}"
    token_url = f"{token_base_url}/datalab/token"

    token = None
    if persisted_token:
        token = config.get_token(url=api_url)

    if not token:
        # Show a prompt to the user with the explanations on how to get the token.
        print(_PROMPT.format(URL=token_url))
        token = getpass.getpass("🔑 Enter your token: ")
        token_status, _ = get_jwt_status(token)

        if token_status != "valid":
            message = f"The provided token is {token_status}. Have you entered it correctly? 🤔"
            print(message)
            raise ValueError(message)

        if persisted_token:
            config.set_token(token, api_url)

    print("🎉 You are now connected to the Impresso API!  🎉")
    if api_url != DEFAULT_API_URL:
        print(f"🔗 Using API: {api_url}")

    return ImpressoClient(api_url=api_url, api_bearer_token=token)
