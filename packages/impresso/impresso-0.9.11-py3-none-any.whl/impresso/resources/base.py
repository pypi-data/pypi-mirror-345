from impresso.api_client.client import AuthenticatedClient


class Resource:
    """Base for all API backed resources."""

    name: str

    def __init__(self, api_client: AuthenticatedClient):
        self._api_client = api_client

    def _get_web_app_base_url(self) -> str:
        return "https://impresso-project.ch/app"


DEFAULT_PAGE_SIZE = 100
