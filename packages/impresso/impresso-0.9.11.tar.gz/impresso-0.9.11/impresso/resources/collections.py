from pandas import DataFrame, json_normalize
from impresso.api_client.api.collections import (
    find_collections,
    get_collection,
    patch_collections_collection_id_items,
)
from impresso.api_client.models.find_collections_order_by import (
    FindCollectionsOrderBy,
    FindCollectionsOrderByLiteral,
)
from impresso.api_client.models.update_collectable_items_request import (
    UpdateCollectableItemsRequest,
)
from impresso.api_client.types import UNSET
from impresso.api_models import BaseFind, Collection
from impresso.data_container import DataContainer
from impresso.resources.base import Resource
from impresso.resources.search import SearchDataContainer, SearchResource
from impresso.util.error import raise_for_error
from impresso.util.py import get_enum_from_literal


class FindCollectionsSchema(BaseFind):
    """Schema for the find collections response."""

    data: list[Collection]


class FindCollectionsContainer(DataContainer):
    """Response of a find call."""

    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()["data"]
        if len(data):
            return json_normalize(self._data.to_dict()["data"]).set_index("uid")
        return DataFrame()


class GetCollectionContainer(DataContainer):
    """Response of a get call."""

    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()
        if len(data):
            return json_normalize([self._data.to_dict()]).set_index("uid")
        return DataFrame()

    @property
    def size(self) -> int:
        """Current page size."""
        data = self._data.to_dict()
        if len(data):
            return 1
        return 0

    @property
    def total(self) -> int:
        """Total number of results."""
        return self.size


class CollectionsResource(Resource):
    """
    Work with collections.

    Examples:
        Find collections containing the term "war":
        >>> results = collections.find(term="war") # doctest: +SKIP
        >>> print(results.df) # doctest: +SKIP

        Get a specific collection by its ID:
        >>> collection_id = "some-collection-id" # Replace with a real ID
        >>> collection = collections.get(collection_id) # doctest: +SKIP
        >>> print(collection.df) # doctest: +SKIP

        List items in a collection:
        >>> items = collections.items(collection_id) # doctest: +SKIP
        >>> print(items.df) # doctest: +SKIP

        Add items to a collection:
        >>> item_ids_to_add = ["item-id-1", "item-id-2"] # Replace with real item IDs
        >>> collections.add_items(collection_id, item_ids_to_add) # doctest: +SKIP

        Remove items from a collection:
        >>> item_ids_to_remove = ["item-id-1"] # Replace with real item IDs
        >>> collections.remove_items(collection_id, item_ids_to_remove) # doctest: +SKIP
    """

    name = "collections"

    def find(
        self,
        term: str | None = None,
        order_by: FindCollectionsOrderByLiteral | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> FindCollectionsContainer:
        """
        Search collections in Impresso.

        Args:
            term: Search term.
            order_by: Order by aspect.
            limit: Number of results to return.
            offset: Number of results to skip.

        Returns:
            FindCollectionsContainer: Data container with a page of results of the search.
        """

        result = find_collections.sync(
            client=self._api_client,
            term=term if term is not None else UNSET,
            order_by=(
                get_enum_from_literal(order_by, FindCollectionsOrderBy)  # type: ignore
                if order_by is not None
                else FindCollectionsOrderBy.VALUE_0
            ),
            limit=limit if limit is not None else UNSET,
            offset=offset if offset is not None else UNSET,
        )
        raise_for_error(result)
        return FindCollectionsContainer(
            result,
            FindCollectionsSchema,
            web_app_search_result_url=_build_web_app_find_collections_url(
                base_url=self._get_web_app_base_url(),
                term=term,
                order_by=order_by,
            ),
        )

    def get(self, id: str) -> GetCollectionContainer:
        """Get collection by ID."""

        result = get_collection.sync(
            client=self._api_client,
            id=id,
        )
        raise_for_error(result)
        return GetCollectionContainer(
            result,
            FindCollectionsSchema,
            web_app_search_result_url=_build_web_app_get_collection_url(
                base_url=self._get_web_app_base_url(),
                collection_id=id,
            ),
        )

    def items(
        self,
        collection_id: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> SearchDataContainer:
        """
        Return all content items from a collection.

        Args:
            collection_id: ID of the collection.
            limit: Number of results to return.
            offset: Number of results to skip.

        Returns:
            SearchDataContainer: Data container with a page of results of the search.
        """

        search_resource = SearchResource(self._api_client)
        return search_resource.find(
            collection_id=collection_id, limit=limit, offset=offset
        )

    def add_items(self, collection_id: str, item_ids: list[str]) -> None:
        """
        Add items to a collection by their IDs.

        **NOTE**: Items are not added immediately.
        This operation may take up to a few minutes
        to complete and reflect in the collection.

        Args:
            collection_id: ID of the collection.
            item_ids: IDs of the content items to add.
        """
        result = patch_collections_collection_id_items.sync(
            client=self._api_client,
            collection_id=collection_id,
            body=UpdateCollectableItemsRequest(
                add=item_ids,
                remove=UNSET,
            ),
        )
        raise_for_error(result)

    def remove_items(self, collection_id: str, item_ids: list[str]) -> None:
        """
        Add items to a collection by their IDs.

        **NOTE**: Items are not removed immediately.
        This operation may take up to a few minutes
        to complete and reflect in the collection.

        Args:
            collection_id: ID of the collection.
            item_ids: IDs of the content items to add.
        """
        result = patch_collections_collection_id_items.sync(
            client=self._api_client,
            collection_id=collection_id,
            body=UpdateCollectableItemsRequest(
                remove=item_ids,
                add=UNSET,
            ),
        )
        raise_for_error(result)


def _build_web_app_find_collections_url(
    base_url: str,
    term: str | None = None,
    order_by: FindCollectionsOrderByLiteral | None = None,
) -> str:
    query_params = {
        "orderBy": order_by,
        "q": term,
    }
    query_string = "&".join(
        f"{key}={value}" for key, value in query_params.items() if value is not None
    )
    url = f"{base_url}/collections?{query_string}"
    return f"{url}?{query_string}" if query_string else url


def _build_web_app_get_collection_url(
    base_url: str,
    collection_id: str,
) -> str:
    return f"{base_url}/collections/{collection_id}"
