from pandas import DataFrame, json_normalize

from impresso.api_client.api.media_sources import find_media_sources
from impresso.api_client.models.find_media_sources_order_by import (
    FindMediaSourcesOrderBy,
    FindMediaSourcesOrderByLiteral,
)
from impresso.api_client.models.find_media_sources_type import (
    FindMediaSourcesType,
    FindMediaSourcesTypeLiteral,
)
from impresso.api_client.types import UNSET
from impresso.api_models import BaseFind, MediaSource
from impresso.data_container import DataContainer
from impresso.resources.base import Resource
from impresso.util.error import raise_for_error
from impresso.util.py import get_enum_from_literal


class FindMediaSourcesSchema(BaseFind):
    """Schema for the find media sources response."""

    data: list[MediaSource]


class FindMediaSourcesContainer(DataContainer):
    """Response of a search call."""

    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()["data"]
        if len(data):
            return json_normalize(self._data.to_dict()["data"]).set_index("uid")
        return DataFrame()


class MediaSourcesResource(Resource):
    """Search media sources in the Impresso database."""

    name = "media_sources"

    def find(
        self,
        term: str | None = None,
        type: FindMediaSourcesTypeLiteral | None = None,
        order_by: FindMediaSourcesOrderByLiteral | None = None,
        with_properties: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> FindMediaSourcesContainer:
        """
        Search media sources in Impresso.

        Args:
            term: Search term.
            type: Type of media sources to search for.
            order_by: Field to order results by.
            with_properties: Include properties in the results.
            limit: Number of results to return.
            offset: Number of results to skip.

        Returns:
            FindMediaSourcesContainer: Data container with a page of results of the search.
        """
        result = find_media_sources.sync(
            client=self._api_client,
            term=term if term is not None else UNSET,
            order_by=(
                get_enum_from_literal(order_by, FindMediaSourcesOrderBy)
                if order_by is not None
                else UNSET
            ),
            type=(
                get_enum_from_literal(type, FindMediaSourcesType)
                if type is not None
                else UNSET
            ),
            include_properties=with_properties,
            limit=limit if limit is not None else UNSET,
            offset=offset if offset is not None else UNSET,
        )
        raise_for_error(result)
        return FindMediaSourcesContainer(
            result,
            FindMediaSourcesSchema,
            web_app_search_result_url=_build_web_app_media_sources_url(
                base_url=self._get_web_app_base_url(),
                term=term,
                order_by=order_by,
            ),
        )


def _build_web_app_media_sources_url(
    base_url: str,
    term: str | None = None,
    order_by: FindMediaSourcesOrderByLiteral | None = None,
) -> str:
    query_params = {
        "orderBy": order_by,
        "q": term,
    }
    query_string = "&".join(
        f"{key}={value}" for key, value in query_params.items() if value is not None
    )
    url = f"{base_url}/newspapers"
    return f"{url}?{query_string}" if query_string else url
