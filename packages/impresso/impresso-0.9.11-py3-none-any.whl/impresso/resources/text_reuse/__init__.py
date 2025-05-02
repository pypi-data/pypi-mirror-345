from impresso.api_client.client import AuthenticatedClient
from impresso.resources.text_reuse.clusters import TextReuseClustersResource
from impresso.resources.text_reuse.passages import TextReusePassagesResource


class TextReuseDomain:
    """Container for text reuse resources."""

    def __init__(self, api_client: AuthenticatedClient) -> None:
        self._api_client = api_client

    @property
    def clusters(self) -> TextReuseClustersResource:
        return TextReuseClustersResource(self._api_client)

    @property
    def passages(self) -> TextReusePassagesResource:
        return TextReusePassagesResource(self._api_client)
