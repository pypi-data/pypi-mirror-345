from impresso.api_client.client import AuthenticatedClient
from impresso.resources.content_items import ContentItemsResource
from impresso.resources.collections import CollectionsResource
from impresso.resources.entities import EntitiesResource
from impresso.resources.media_sources import MediaSourcesResource
from impresso.resources.search import SearchResource
from impresso.resources.text_reuse import TextReuseDomain
from impresso.resources.tools import ToolsResource


class ImpressoApiResourcesBase:
    """Base class for the Impresso client that contains resources."""

    def __init__(self, api_client: AuthenticatedClient) -> None:
        self._api_client = api_client

    @property
    def search(self) -> SearchResource:
        return SearchResource(self._api_client)

    @property
    def content_items(self) -> ContentItemsResource:
        return ContentItemsResource(self._api_client)

    @property
    def text_reuse(self) -> TextReuseDomain:
        return TextReuseDomain(self._api_client)

    @property
    def media_sources(self) -> MediaSourcesResource:
        return MediaSourcesResource(self._api_client)

    @property
    def collections(self) -> CollectionsResource:
        return CollectionsResource(self._api_client)

    @property
    def entities(self) -> EntitiesResource:
        return EntitiesResource(self._api_client)

    @property
    def tools(self) -> ToolsResource:
        return ToolsResource(self._api_client)
