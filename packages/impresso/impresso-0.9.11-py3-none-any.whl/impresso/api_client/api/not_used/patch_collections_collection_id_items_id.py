from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.collectable_items_updated_response import CollectableItemsUpdatedResponse
from ...models.error import Error
from ...models.update_collectable_items_request import UpdateCollectableItemsRequest
from ...types import Response


def _get_kwargs(
    collection_id: str,
    id: int,
    *,
    body: UpdateCollectableItemsRequest,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "patch",
        "url": f"/collections/{collection_id}/items/{id}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CollectableItemsUpdatedResponse, Error]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CollectableItemsUpdatedResponse.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = Error.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = Error.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = Error.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = Error.from_dict(response.json())

        return response_422
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        response_429 = Error.from_dict(response.json())

        return response_429
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = Error.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CollectableItemsUpdatedResponse, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateCollectableItemsRequest,
) -> Response[Union[CollectableItemsUpdatedResponse, Error]]:
    """Updates the resource identified by id using data.

    Args:
        collection_id (str):
        id (int):
        body (UpdateCollectableItemsRequest): Request to update collectible items in a collection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectableItemsUpdatedResponse, Error]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateCollectableItemsRequest,
) -> Optional[Union[CollectableItemsUpdatedResponse, Error]]:
    """Updates the resource identified by id using data.

    Args:
        collection_id (str):
        id (int):
        body (UpdateCollectableItemsRequest): Request to update collectible items in a collection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectableItemsUpdatedResponse, Error]
    """

    return sync_detailed(
        collection_id=collection_id,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    collection_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateCollectableItemsRequest,
) -> Response[Union[CollectableItemsUpdatedResponse, Error]]:
    """Updates the resource identified by id using data.

    Args:
        collection_id (str):
        id (int):
        body (UpdateCollectableItemsRequest): Request to update collectible items in a collection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollectableItemsUpdatedResponse, Error]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: UpdateCollectableItemsRequest,
) -> Optional[Union[CollectableItemsUpdatedResponse, Error]]:
    """Updates the resource identified by id using data.

    Args:
        collection_id (str):
        id (int):
        body (UpdateCollectableItemsRequest): Request to update collectible items in a collection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollectableItemsUpdatedResponse, Error]
    """

    return (
        await asyncio_detailed(
            collection_id=collection_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
