from pandas import DataFrame, json_normalize

from impresso.api_client.api.search_facets import get_tr_passages_facet
from impresso.api_client.api.text_reuse_passages import find_text_reuse_passages
from impresso.api_client.models.find_text_reuse_passages_order_by import (
    FindTextReusePassagesOrderBy,
    FindTextReusePassagesOrderByLiteral,
)
from impresso.api_client.models.get_tr_passages_facet_id import (
    GetTrPassagesFacetId,
    GetTrPassagesFacetIdLiteral,
)
from impresso.api_client.models.get_tr_passages_facet_order_by import (
    GetTrPassagesFacetOrderBy,
)
from impresso.api_client.types import UNSET, Unset
from impresso.api_models import (
    BaseFind,
    SearchFacetBucket,
    TextReusePassage,
)
from impresso.data_container import DataContainer
from impresso.resources.base import Resource
from impresso.resources.search import FacetDataContainer
from impresso.resources.text_reuse.clusters import Range, _build_filters
from impresso.structures import AND, OR, DateRange
from impresso.util.error import raise_for_error
from impresso.util.filters import and_or_filter, filters_as_protobuf
from impresso.util.py import get_enum_from_literal


class FindTextReusePassageResponseSchema(BaseFind):
    """Schema for the text reuse passage response."""

    data: list[TextReusePassage]


class FindTextReusePassagesContainer(DataContainer):
    """Response of a find text reuse passages call."""

    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()["data"]
        if len(data):
            return json_normalize(self._data.to_dict()["data"]).set_index("uid")
        return DataFrame()


class TextReusePassagesResource(Resource):
    """Text reuse passages resource."""

    name = "textReusePassages"

    def find(
        self,
        term: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: FindTextReusePassagesOrderByLiteral | None = None,
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
    ) -> FindTextReusePassagesContainer:
        """
        Find text reuse passages based on various criteria.

        Args:
            term: Search for passages containing specific text.
            limit: Maximum number of passages to return.
            offset: Number of passages to skip from the beginning.
            order_by: Specify the sorting order for the results.
            cluster_id: Filter passages belonging to specific text reuse clusters.
            cluster_size: Filter passages based on the size of the cluster they belong to.
            title: Filter passages by the title of the articles they appear in.
            lexical_overlap: Filter passages based on the lexical overlap score within their cluster.
            day_delta: Filter passages based on the time span (in days) of their cluster.
            date_range: Filter passages based on their publication date.
            newspaper_id: Filter passages from specific newspapers.
            collection_id: Filter passages from specific collections.
            front_page: Filter passages appearing on the front page.
            topic_id: Filter passages associated with specific topics.
            language: Filter passages by their language.
            country: Filter passages by the country of publication.
            mention: Filter passages containing specific mentions (named entities).
            entity_id: Filter passages associated with specific entity IDs.

        Returns:
            FindTextReusePassagesContainer: A container holding the search results.

        Examples:
            Find passages containing the term 'revolution' from French newspapers:
            >>> results = textReusePassages.find(term='revolution', country='FR') # doctest: +SKIP
            >>> print(results.df) # doctest: +SKIP

            Find passages from clusters with a size greater than 50:
            >>> results = textReusePassages.find(cluster_size=(51, None)) # doctest: +SKIP
            >>> print(results.df) # doctest: +SKIP
        """
        # reusing build filters from clusters - they are the same
        filters = _build_filters(
            cluster_id=cluster_id,
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
        if term is not None:
            filters.extend(and_or_filter(term, "string"))
        filters_pb = filters_as_protobuf(filters or [])

        result = find_text_reuse_passages.sync(
            client=self._api_client,
            limit=limit if limit is not None else UNSET,
            offset=offset if offset is not None else UNSET,
            order_by=(
                get_enum_from_literal(order_by, FindTextReusePassagesOrderBy)
                if order_by is not None
                else UNSET
            ),
            filters=filters_pb if filters_pb else UNSET,
        )
        raise_for_error(result)
        return FindTextReusePassagesContainer(
            result,
            FindTextReusePassageResponseSchema,
            web_app_search_result_url=_build_web_app_find_passages_url(
                base_url=self._get_web_app_base_url(),
                filters=filters_pb,
                limit=limit,
                offset=offset,
                order_by=order_by,
            ),
        )

    def facet(
        self,
        facet: GetTrPassagesFacetIdLiteral,
        term: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: FindTextReusePassagesOrderByLiteral | None = None,
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
    ) -> FacetDataContainer:
        """
        Get facet information for text reuse passages based on specified filters.

        Facets provide aggregated counts for different properties of the passages,
        such as the distribution of newspapers or languages.

        Args:
            facet: The specific facet to retrieve (e.g., 'newspaper', 'language').
            term: Filter passages by text content before calculating facets.
            limit: Maximum number of facet values to return.
            offset: Number of facet values to skip.
            order_by: How to order the facet values (e.g., 'value', 'count').
            cluster_id: Filter passages by cluster ID before calculating facets.
            cluster_size: Filter passages by cluster size before calculating facets.
            title: Filter passages by article title before calculating facets.
            lexical_overlap: Filter passages by lexical overlap before calculating facets.
            day_delta: Filter passages by cluster day delta before calculating facets.
            date_range: Filter passages by publication date before calculating facets.
            newspaper_id: Filter passages by newspaper before calculating facets.
            collection_id: Filter passages by collection before calculating facets.
            front_page: Filter passages by front page status before calculating facets.
            topic_id: Filter passages by topic ID before calculating facets.
            language: Filter passages by language before calculating facets.
            country: Filter passages by country before calculating facets.
            mention: Filter passages by mention before calculating facets.
            entity_id: Filter passages by entity ID before calculating facets.

        Returns:
            FacetDataContainer: A container holding the facet results.

        Examples:
            Get the top 10 newspapers associated with passages containing 'war':
            >>> facet_results = textReusePassages.facet(facet='newspaper', term='war', limit=10) # doctest: +SKIP
            >>> print(facet_results.df) # doctest: +SKIP

            Get the language distribution for passages published between 1914 and 1918:
            >>> from impresso.structures import DateRange
            >>> date_filter = DateRange(start="1914-01-01", end="1918-12-31")
            >>> facet_results = textReusePassages.facet(facet='language', date_range=date_filter) # doctest: +SKIP
            >>> print(facet_results.df) # doctest: +SKIP
        """
        facet_id = get_enum_from_literal(facet, GetTrPassagesFacetId)
        if isinstance(facet_id, Unset):
            raise ValueError(f"{facet} is not a valid value")

        filters = _build_filters(
            cluster_id=cluster_id,
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

        if term is not None:
            filters.extend(and_or_filter(term, "string"))

        filters_pb = filters_as_protobuf(filters or [])

        result = get_tr_passages_facet.sync(
            client=self._api_client,
            id=facet_id,
            filters=filters_pb if filters_pb else UNSET,
            offset=offset if offset is not None else UNSET,
            limit=limit if limit is not None else UNSET,
            order_by=(
                get_enum_from_literal(order_by, GetTrPassagesFacetOrderBy)
                if order_by is not None
                else get_enum_from_literal("value", GetTrPassagesFacetOrderBy)
            ),
        )
        raise_for_error(result)
        return FacetDataContainer(
            result,
            SearchFacetBucket,
            web_app_search_result_url=_build_web_app_find_passages_url(
                base_url=self._get_web_app_base_url(),
                filters=filters_pb,
                limit=limit,
                offset=offset,
                order_by=order_by,
            ),
        )


def _build_web_app_find_passages_url(
    base_url: str,
    filters=str | None,
    limit=int | None,
    offset=int | None,
    order_by=FindTextReusePassagesOrderBy | None,
) -> str:
    page = offset // limit if limit is not None and offset is not None else 0
    query_params = {
        "sort": order_by,
        "sq": filters,
        "p": page + 1,
    }
    query_string = "&".join(
        f"{key}={value}" for key, value in query_params.items() if value is not None
    )
    url = f"{base_url}/text-reuse/passages"
    return f"{url}?{query_string}" if query_string else url
