from pandas import DataFrame, json_normalize

from impresso.api_client.api.search_facets import get_tr_clusters_facet
from impresso.api_client.api.text_reuse_clusters import find_text_reuse_clusters
from impresso.api_client.models.find_text_reuse_clusters_order_by import (
    FindTextReuseClustersOrderBy,
    FindTextReuseClustersOrderByLiteral,
)
from impresso.api_client.models.get_tr_clusters_facet_id import (
    GetTrClustersFacetId,
    GetTrClustersFacetIdLiteral,
)
from impresso.api_client.models.get_tr_clusters_facet_order_by import (
    GetTrClustersFacetOrderBy,
    GetTrClustersFacetOrderByLiteral,
)
from impresso.api_client.types import UNSET, Unset
from impresso.api_models import (
    BaseFind,
    Filter,
    Q,
    SearchFacetBucket,
    TextReuseCluster,
)
from impresso.data_container import DataContainer
from impresso.resources.base import Resource
from impresso.resources.search import FacetDataContainer
from impresso.structures import AND, OR, DateRange
from impresso.util.error import raise_for_error
from impresso.util.filters import and_or_filter, filters_as_protobuf
from impresso.util.py import get_enum_from_literal


class FindTextReuseClusterResponseSchema(BaseFind):
    """Schema for the text reuse clusters response."""

    data: list[TextReuseCluster]


class FindTextReuseClustersContainer(DataContainer):
    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()["data"]
        if len(data):
            return json_normalize(data).set_index("uid")
        return DataFrame()


Range = tuple[int, int]


class TextReuseClustersResource(Resource):
    """
    Interact with the text reuse clusters endpoint of the Impresso API.

    This resource allows searching for text reuse clusters based on various criteria
    and retrieving facet information about these clusters.

    Examples:
        Find clusters with size between 10 and 20:
        >>> results = textReuseClusters.find(cluster_size=(10, 20)) # doctest: +SKIP
        >>> print(results.df) # doctest: +SKIP

        Get the distribution of newspapers involved in clusters:
        >>> facet_results = textReuseClusters.facet(facet='newspaper', order_by='count') # doctest: +SKIP
        >>> print(facet_results.df) # doctest: +SKIP
    """

    name = "textReuseClusters"

    def find(
        self,
        term: str | None = None,
        title: str | AND[str] | OR[str] | None = None,
        order_by: FindTextReuseClustersOrderByLiteral | None = None,
        cluster_size: Range | AND[Range] | OR[Range] | None = None,
        lexical_overlap: Range | AND[Range] | OR[Range] | None = None,
        day_delta: Range | AND[Range] | OR[Range] | None = None,
        date_range: DateRange | None = None,
        newspaper_id: str | OR[str] | None = None,
        collection_id: str | OR[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        front_page: bool | None = None,
        topic_id: str | AND[str] | OR[str] | None = None,
        language: str | OR[str] | None = None,
        country: str | OR[str] | None = None,
        mention: str | AND[str] | OR[str] | None = None,
        entity_id: str | AND[str] | OR[str] | None = None,
    ) -> FindTextReuseClustersContainer:
        """
        Find text reuse clusters based on various criteria.

        Args:
            term: Search for clusters containing specific text.
            title: Filter clusters by the title of the articles within them.
            order_by: Specify the sorting order for the results.
            cluster_size: Filter clusters by the number of items they contain.
            lexical_overlap: Filter clusters by the lexical overlap score.
            day_delta: Filter clusters by the time span (in days) between the first and last item.
            date_range: Filter clusters based on the date range of their items.
            newspaper_id: Filter clusters containing items from specific newspapers.
            collection_id: Filter clusters containing items from specific collections.
            limit: Maximum number of clusters to return.
            offset: Number of clusters to skip from the beginning.
            front_page: Filter clusters containing items published on the front page.
            topic_id: Filter clusters associated with specific topics.
            language: Filter clusters by the language of their items.
            country: Filter clusters by the country of publication of their items.
            mention: Filter clusters containing specific mentions (named entities).
            entity_id: Filter clusters associated with specific entity IDs.

        Returns:
            FindTextReuseClustersContainer: A container holding the search results.

        Examples:
            Find clusters with size between 10 and 20:
            >>> results = textReuseClusters.find(cluster_size=(10, 20)) # doctest: +SKIP
            >>> print(results.df) # doctest: +SKIP

            Find clusters related to 'politics' in Swiss newspapers:
            >>> results = textReuseClusters.find(term='politics', country='CH') # doctest: +SKIP
            >>> print(results.df) # doctest: +SKIP
        """

        filters = _build_filters(
            text=term,
            cluster_size=cluster_size,
            title=title,
            lexical_overlap=lexical_overlap,
            day_delta=day_delta,
            date_range=date_range,
            newspaper_id=newspaper_id,
            collection_id=collection_id,
            front_page=front_page,
            topic_id=topic_id,
            language=language,
            country=country,
            mention=mention,
            entity_id=entity_id,
        )
        filters_pb = filters_as_protobuf(filters or [])

        result = find_text_reuse_clusters.sync(
            client=self._api_client,
            limit=limit if limit is not None else UNSET,
            offset=offset if offset is not None else UNSET,
            order_by=(
                get_enum_from_literal(order_by, FindTextReuseClustersOrderBy)
                if order_by is not None
                else UNSET
            ),
            filters=filters_pb if filters_pb else UNSET,
        )
        raise_for_error(result)
        return FindTextReuseClustersContainer(
            result,
            FindTextReuseClusterResponseSchema,
            web_app_search_result_url=_build_web_app_find_clusters_url(
                base_url=self._get_web_app_base_url(),
                filters=filters_pb,
                limit=limit,
                offset=offset,
                order_by=order_by,
            ),
        )

    def facet(
        self,
        facet: GetTrClustersFacetIdLiteral,
        order_by: GetTrClustersFacetOrderByLiteral | None = "value",
        limit: int | None = None,
        offset: int | None = None,
        cluster_size: Range | AND[Range] | OR[Range] | None = None,
        date_range: DateRange | None = None,
        newspaper_id: str | OR[str] | None = None,
        lexical_overlap: Range | AND[Range] | OR[Range] | None = None,
        day_delta: Range | AND[Range] | OR[Range] | None = None,
    ) -> FacetDataContainer:
        """
        Get facet information for text reuse clusters based on specified filters.

        Facets provide aggregated counts for different properties of the clusters,
        such as the distribution of cluster sizes or newspapers involved.

        Args:
            facet: The specific facet to retrieve (e.g., 'newspaper', 'cluster_size').
            order_by: How to order the facet values (e.g., 'value', 'count').
            limit: Maximum number of facet values to return.
            offset: Number of facet values to skip.
            cluster_size: Filter clusters by size before calculating facets.
            date_range: Filter clusters by date range before calculating facets.
            newspaper_id: Filter clusters by newspaper before calculating facets.
            lexical_overlap: Filter clusters by lexical overlap before calculating facets.
            day_delta: Filter clusters by day delta before calculating facets.

        Returns:
            FacetDataContainer: A container holding the facet results.

        Examples:
            Get the top 10 newspapers involved in clusters:
            >>> facet_results = textReuseClusters.facet(facet='newspaper', limit=10, order_by='count') # doctest: +SKIP
            >>> print(facet_results.df) # doctest: +SKIP

            Get the distribution of cluster sizes for clusters within a specific date range:
            >>> from impresso.structures import DateRange
            >>> date_filter = DateRange(start="1900-01-01", end="1910-12-31")
            >>> facet_results = textReuseClusters.facet(facet='cluster_size', date_range=date_filter) # doctest: +SKIP
            >>> print(facet_results.df) # doctest: +SKIP
        """
        facet_id = get_enum_from_literal(facet, GetTrClustersFacetId)
        if isinstance(facet_id, Unset):
            raise ValueError(f"{facet} is not a valid value")

        filters = _build_cluster_facet_filters(
            cluster_size=cluster_size,
            lexical_overlap=lexical_overlap,
            day_delta=day_delta,
            date_range=date_range,
            newspaper_id=newspaper_id,
        )

        filters_pb = filters_as_protobuf(filters or [])

        result = get_tr_clusters_facet.sync(
            client=self._api_client,
            id=facet_id,
            filters=filters_pb if filters_pb else UNSET,
            offset=offset if offset is not None else UNSET,
            limit=limit if limit is not None else UNSET,
            order_by=(
                get_enum_from_literal(order_by, GetTrClustersFacetOrderBy)
                if order_by is not None
                else UNSET
            ),
        )
        raise_for_error(result)
        return FacetDataContainer(
            result,
            SearchFacetBucket,
            web_app_search_result_url=_build_web_app_find_clusters_url(
                base_url=self._get_web_app_base_url(),
                filters=filters_pb,
                limit=limit,
                offset=offset,
                order_by=order_by,
            ),
        )


def _build_cluster_facet_filters(
    cluster_size: Range | AND[Range] | OR[Range] | None = None,
    date_range: DateRange | None = None,
    newspaper_id: str | OR[str] | None = None,
    lexical_overlap: Range | AND[Range] | OR[Range] | None = None,
    day_delta: Range | AND[Range] | OR[Range] | None = None,
) -> list[Filter]:
    """Build text reuse clusters facet filters."""

    filters: list[Filter] = []
    if cluster_size is not None:
        filters.extend(
            and_or_filter(
                cluster_size,
                "text_reuse_cluster_size",
                lambda r: f"{r[0]} TO {r[1]}",
            )
        )
    if date_range is not None:
        filters.append(
            Filter(
                type="daterange",
                q=Q(DateRange._as_filter_value(date_range)),
                context="exclude" if date_range.inverted else "include",
                daterange=None,
            )
        )
    if newspaper_id is not None:
        filters.extend(and_or_filter(newspaper_id, "newspaper"))
    if lexical_overlap is not None:
        filters.extend(
            and_or_filter(
                lexical_overlap,
                "text_reuse_cluster_lexical_overlap",
                lambda r: f"{r[0]} TO {r[1]}",
            )
        )
    if day_delta is not None:
        filters.extend(
            and_or_filter(
                day_delta,
                "text_reuse_cluster_day_delta",
                lambda r: f"{r[0]} TO {r[1]}",
            )
        )
    return filters


def _build_filters(
    text: str | None = None,
    cluster_id: str | AND[str] | OR[str] | None = None,
    cluster_size: Range | AND[Range] | OR[Range] | None = None,
    title: str | AND[str] | OR[str] | None = None,
    lexical_overlap: Range | AND[Range] | OR[Range] | None = None,
    day_delta: Range | AND[Range] | OR[Range] | None = None,
    date_range: DateRange | None = None,
    newspaper_id: str | OR[str] | None = None,
    collection_id: str | OR[str] | None = None,
    front_page: bool | None = None,
    topic_id: str | AND[str] | OR[str] | None = None,
    language: str | OR[str] | None = None,
    country: str | OR[str] | None = None,
    mention: str | AND[str] | OR[str] | None = None,
    entity_id: str | AND[str] | OR[str] | None = None,
) -> list[Filter]:
    """Build text reuse clusters filters."""

    filters: list[Filter] = []
    if text is not None:
        filters.extend(and_or_filter(text, "string"))
    if cluster_id is not None:
        filters.extend(and_or_filter(cluster_id, "text_reuse_cluster"))
    if cluster_size is not None:
        filters.extend(
            and_or_filter(
                cluster_size,
                "text_reuse_cluster_size",
                lambda r: f"{r[0]} TO {r[1]}",
            )
        )
    if title is not None:
        filters.extend(and_or_filter(title, "title"))
    if lexical_overlap is not None:
        filters.extend(
            and_or_filter(
                lexical_overlap,
                "text_reuse_cluster_lexical_overlap",
                lambda r: f"{r[0]} TO {r[1]}",
            )
        )
    if day_delta is not None:
        filters.extend(
            and_or_filter(
                day_delta,
                "text_reuse_cluster_day_delta",
                lambda r: f"{r[0]} TO {r[1]}",
            )
        )
    if date_range is not None:
        filters.append(
            Filter(
                type="daterange",
                q=Q(DateRange._as_filter_value(date_range)),
                context="exclude" if date_range.inverted else "include",
                daterange=None,
            )
        )
    if newspaper_id is not None:
        filters.extend(and_or_filter(newspaper_id, "newspaper"))
    if collection_id is not None:
        filters.extend(and_or_filter(collection_id, "collection"))
    if front_page:
        filters.append(Filter(type="is_front", daterange=None))
    if topic_id is not None:
        filters.extend(and_or_filter(topic_id, "topic"))
    if language is not None:
        filters.extend(and_or_filter(language, "language"))
    if country is not None:
        filters.extend(and_or_filter(country, "country"))
    if mention is not None:
        filters.extend(and_or_filter(mention, "mention"))
    if entity_id is not None:
        filters.extend(and_or_filter(entity_id, "entity"))

    return filters


def _build_web_app_find_clusters_url(
    base_url: str,
    filters=str | None,
    limit=int | None,
    offset=int | None,
    order_by=GetTrClustersFacetOrderByLiteral | None,
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
    url = f"{base_url}/text-reuse/clusters"
    return f"{url}?{query_string}" if query_string else url
