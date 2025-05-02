import matplotlib.pyplot as plt
import io
import base64

from pandas import DataFrame, json_normalize

from impresso.api_client.api.search import search
from impresso.api_client.api.search_facets import get_search_facet
from impresso.api_client.models.get_search_facet_id import (
    GetSearchFacetId,
    GetSearchFacetIdLiteral,
)
from impresso.api_client.models.get_search_facet_order_by import (
    GetSearchFacetOrderBy,
    GetSearchFacetOrderByLiteral,
)
from impresso.api_client.models.search_order_by import (
    SearchOrderBy,
    SearchOrderByLiteral,
)
from impresso.api_client.types import UNSET, Unset
from impresso.api_models import ContentItem, BaseFind, Filter, Q, SearchFacetBucket
from impresso.data_container import DataContainer
from impresso.resources.base import DEFAULT_PAGE_SIZE, Resource
from impresso.structures import AND, OR, DateRange
from impresso.util.error import raise_for_error
from impresso.util.filters import and_or_filter, filters_as_protobuf
from impresso.util.py import get_enum_from_literal


class SearchResponseSchema(BaseFind):
    """Schema for the content items response."""

    data: list[ContentItem]


class FacetResponseSchema(BaseFind):
    """Schema for a facet response."""

    data: list[SearchFacetBucket]


class SearchDataContainer(DataContainer):
    """Response of a search call."""

    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()["data"]
        if len(data):
            return json_normalize(self._data.to_dict()["data"]).set_index("uid")
        return DataFrame()


class FacetDataContainer(DataContainer):
    """Response of a get facet call."""

    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()["data"]
        if len(data):
            return json_normalize(self._data.to_dict()["data"]).set_index("value")
        return DataFrame()

    def _get_preview_image_(self) -> str | None:
        if self.size == 0:
            return None
        return render_dataframe_chart_base64(
            self.df.index[:].values, self.df["count"].values
        )


class SearchResource(Resource):
    """Search content items in the impresso database."""

    name = "search"

    def find(
        self,
        term: str | AND[str] | OR[str] | None = None,
        order_by: SearchOrderByLiteral | None = None,
        limit: int | None = None,
        offset: int | None = None,
        with_text_contents: bool | None = False,
        title: str | AND[str] | OR[str] | None = None,
        front_page: bool | None = None,
        entity_id: str | AND[str] | OR[str] | None = None,
        newspaper_id: str | AND[str] | OR[str] | None = None,
        date_range: DateRange | None = None,
        language: str | AND[str] | OR[str] | None = None,
        mention: str | AND[str] | OR[str] | None = None,
        topic_id: str | AND[str] | OR[str] | None = None,
        collection_id: str | AND[str] | OR[str] | None = None,
        country: str | AND[str] | OR[str] | None = None,
        partner_id: str | AND[str] | OR[str] | None = None,
        text_reuse_cluster_id: str | AND[str] | OR[str] | None = None,
    ) -> SearchDataContainer:
        """
        Search for content items in Impresso.

        Args:
            term: Search term.
            order_by: Order by aspect.
            limit: Number of results to return.
            offset: Number of results to skip.

            with_text_contents: Return only content items with text contents.
            title: Return only content items that have this term or all/any of the terms in the title.
            front_page: Return only content items that were on the front page.
            entity_id: Return only content items that mention this entity or all/any of the entities.
            date_range: Return only content items that were published in this date range.
            language: Return only content items that are in this language or all/any of the languages.
                      Use 2-letter ISO language codes (e.g., 'en', 'de', 'fr').
            mention: Return only content items that mention an entity with this term or all/any
                     of entities with the terms.
            topic_id: Return only content items that are about this topic or all/any of the topics.
            collection_id: Return only content items that are in this collection or all/any of the collections.
            country: Return only content items that are from this country or all/any of the countries.
                     Use 2-letter ISO country codes (e.g., 'ch', 'de', 'lu').
            partner_id: Return only content items that are from this partner or all/any of the partners.
            text_reuse_cluster_id: Return only content items that are in this text reuse cluster
                                   or all/any of the clusters.

        Returns:
            SearchDataContainer: Data container with a page of results of the search.
        """

        filters = self._build_filters(
            string=term,
            with_text_contents=with_text_contents,
            title=title,
            front_page=front_page,
            entity_id=entity_id,
            newspaper_id=newspaper_id,
            date_range=date_range,
            language=language,
            mention=mention,
            topic_id=topic_id,
            collection_id=collection_id,
            country=country,
            partner_id=partner_id,
            text_reuse_cluster_id=text_reuse_cluster_id,
        )

        filters_pb = filters_as_protobuf(filters or [])

        result = search.sync(
            client=self._api_client,
            term=UNSET,
            order_by=(
                get_enum_from_literal(order_by, SearchOrderBy)
                if order_by is not None
                else UNSET
            ),
            filters=filters_pb if filters_pb else UNSET,
            limit=limit if limit is not None else DEFAULT_PAGE_SIZE,
            offset=offset if offset is not None else UNSET,
        )
        raise_for_error(result)
        return SearchDataContainer(
            result,
            SearchResponseSchema,
            _build_web_app_search_url(
                f"{self._get_web_app_base_url()}/search",
                order_by=order_by,
                filters=filters_pb,
                limit=limit,
                offset=offset,
            ),
        )

    def facet(
        self,
        facet: GetSearchFacetIdLiteral,
        term: str | AND[str] | OR[str] | None = None,
        order_by: GetSearchFacetOrderByLiteral | None = "value",
        limit: int | None = None,
        offset: int | None = None,
        with_text_contents: bool | None = False,
        title: str | AND[str] | OR[str] | None = None,
        front_page: bool | None = None,
        entity_id: str | AND[str] | OR[str] | None = None,
        newspaper_id: str | AND[str] | OR[str] | None = None,
        date_range: DateRange | None = None,
        language: str | AND[str] | OR[str] | None = None,
        mention: str | AND[str] | OR[str] | None = None,
        topic_id: str | AND[str] | OR[str] | None = None,
        collection_id: str | AND[str] | OR[str] | None = None,
        country: str | AND[str] | OR[str] | None = None,
        partner_id: str | AND[str] | OR[str] | None = None,
        text_reuse_cluster_id: str | AND[str] | OR[str] | None = None,
    ) -> FacetDataContainer:
        """
        Get facets for a search query.

        Facets provide aggregated information about a specific dimension of search results,
        such as counts of newspaper titles, languages, or topics.

        Args:
            facet: Type of facet to retrieve (e.g., 'newspaper', 'language', 'topic').
            term: Search term to filter facets.
            order_by: How to order facet results ('value' or 'count').
            limit: Maximum number of facet buckets to return.
            offset: Number of facet buckets to skip.

            with_text_contents: Filter for content items with text contents.
            title: Filter by content items having this term or terms in the title.
            front_page: Filter for content items that were on the front page.
            entity_id: Filter by content items mentioning this entity or entities.
            newspaper_id: Filter by newspaper.
            date_range: Filter by publication date range.
            language: Filter by content language. Use 2-letter ISO language codes (e.g., 'en', 'de', 'fr').
            mention: Filter by content items mentioning entities with these terms.
            topic_id: Filter by content items about this topic or topics.
            collection_id: Filter by collection.
            country: Filter by country of publication. Use 2-letter ISO country codes (e.g., 'ch', 'de', 'lu').
            partner_id: Filter by partner institution.
            text_reuse_cluster_id: Filter by text reuse cluster.

        Returns:
            FacetDataContainer: Data container with facet results, including counts for each bucket.
            The container provides visualization capabilities through the ._get_preview_image_() method.

        Examples:
            >>> search = SearchResource(client)
            >>> # Get newspaper facets for articles mentioning "war"
            >>> newspaper_facets = search.facet(facet="newspaper", term="war")
            >>> # Get language facets for front page articles
            >>> language_facets = search.facet(facet="language", front_page=True)
        """

        facet_id = get_enum_from_literal(facet, GetSearchFacetId)
        if isinstance(facet_id, Unset):
            raise ValueError(f"{facet} is not a valid value")

        filters = self._build_filters(
            string=term,
            with_text_contents=with_text_contents,
            title=title,
            front_page=front_page,
            entity_id=entity_id,
            newspaper_id=newspaper_id,
            date_range=date_range,
            language=language,
            mention=mention,
            topic_id=topic_id,
            collection_id=collection_id,
            country=country,
            partner_id=partner_id,
            text_reuse_cluster_id=text_reuse_cluster_id,
        )

        filters_pb = filters_as_protobuf(filters or [])

        result = get_search_facet.sync(
            client=self._api_client,
            id=facet_id,
            filters=filters_pb if filters_pb else UNSET,
            offset=offset if offset is not None else UNSET,
            limit=limit if limit is not None else UNSET,
            order_by=(
                get_enum_from_literal(order_by, GetSearchFacetOrderBy)
                if order_by is not None
                else UNSET
            ),
        )
        raise_for_error(result)
        return FacetDataContainer(
            result,
            FacetResponseSchema,
            _build_web_app_facet_url(
                f"{self._get_web_app_base_url()}/search",
                facet=facet,
                filters=filters_pb,
                limit=limit,
                offset=offset,
            ),
        )
        # return FacetDataContainer(
        #     result,
        #     SearchFacet,
        #     limit=limit,
        #     offset=offset,
        #     web_app_search_result_url=_build_web_app_facet_url(
        #         f"{self._get_web_app_base_url()}/search",
        #         facet=facet,
        #         filters=filters_pb,
        #         limit=limit,
        #         offset=offset,
        #     ),
        # )

    def _build_filters(
        self,
        string: str | AND[str] | OR[str] | None,
        with_text_contents: bool | None = False,
        title: str | AND[str] | OR[str] | None = None,
        front_page: bool | None = None,
        entity_id: str | AND[str] | OR[str] | None = None,
        newspaper_id: str | AND[str] | OR[str] | None = None,
        date_range: DateRange | None = None,
        language: str | AND[str] | OR[str] | None = None,
        mention: str | AND[str] | OR[str] | None = None,
        topic_id: str | AND[str] | OR[str] | None = None,
        collection_id: str | AND[str] | OR[str] | None = None,
        country: str | AND[str] | OR[str] | None = None,
        partner_id: str | AND[str] | OR[str] | None = None,
        text_reuse_cluster_id: str | AND[str] | OR[str] | None = None,
    ) -> list[Filter]:
        filters: list[Filter] = []
        if string:
            filters.extend(and_or_filter(string, "string"))
        if with_text_contents:
            filters.append(Filter(type="has_text_contents", daterange=None))
        if title is not None:
            filters.extend(and_or_filter(title, "title"))
        if front_page:
            filters.append(Filter(type="is_front", daterange=None))
        if entity_id is not None:
            filters.extend(and_or_filter(entity_id, "entity"))
        if newspaper_id is not None:
            filters.extend(and_or_filter(newspaper_id, "newspaper"))
        if date_range is not None:
            filters.append(
                Filter(
                    type="daterange",
                    q=Q(DateRange._as_filter_value(date_range)),
                    context="exclude" if date_range.inverted else "include",
                    daterange=None,
                )
            )
        if language is not None:
            filters.extend(and_or_filter(language, "language"))
        if mention is not None:
            filters.extend(and_or_filter(mention, "mention"))
        if topic_id is not None:
            filters.extend(and_or_filter(topic_id, "topic"))
        if collection_id is not None:
            filters.extend(and_or_filter(collection_id, "collection"))
        if country is not None:
            filters.extend(and_or_filter(country, "country"))
        if partner_id is not None:
            filters.extend(and_or_filter(partner_id, "partner"))
        if text_reuse_cluster_id is not None:
            filters.extend(and_or_filter(text_reuse_cluster_id, "text_reuse_cluster"))

        return filters


def _build_web_app_search_url(
    base_url: str,
    order_by: SearchOrderByLiteral | None = None,
    filters: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> str:
    page = offset // limit if limit is not None and offset is not None else 0
    query_params = {
        "orderBy": order_by,
        "sq": filters,
        "p": page + 1,
    }
    query_string = "&".join(
        f"{key}={value}" for key, value in query_params.items() if value is not None
    )
    return f"{base_url}?{query_string}" if query_string else base_url


def _build_web_app_facet_url(
    base_url: str,
    facet: str,
    filters: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> str:
    page = offset // limit if limit is not None and offset is not None else 0
    query_params = {
        "index": "search",
        "facet": "type",
        "domain": facet,
        "sq": filters,
        "p": page + 1,
    }
    query_string = "&".join(
        f"{key}={value}" for key, value in query_params.items() if value is not None
    )
    return f"{base_url}?{query_string}" if query_string else base_url


def render_dataframe_chart_base64(x, y) -> str:
    plt.figure(figsize=(12, 1))

    if len(x) < 50:
        plt.bar(x, y)
    else:
        plt.plot(x, y)

    # Remove labels, and legend
    # plt.legend().remove()

    # Either
    # Remove axes,
    plt.axis("off")

    # OR
    # Remove Y axis and only show the first and last tick
    # plt.gca().get_yaxis().set_visible(False)
    # plt.xticks([x[0], x[-1]])

    # Remove the box around the graph
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    # Save the plot to a bytes buffer with a transparent background
    buffer = io.BytesIO()
    plt.savefig(
        buffer, format="png", bbox_inches="tight", pad_inches=0.1, transparent=True
    )
    buffer.seek(0)

    # Encode the bytes as base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Close the plot to free up memory
    plt.close()

    return image_base64
