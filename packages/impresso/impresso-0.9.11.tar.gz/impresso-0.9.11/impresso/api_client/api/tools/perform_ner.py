from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.impresso_named_entity_recognition_request import ImpressoNamedEntityRecognitionRequest
from ...models.impresso_named_entity_recognition_response import ImpressoNamedEntityRecognitionResponse
from ...types import Response


def _get_kwargs(
    *,
    body: ImpressoNamedEntityRecognitionRequest,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/tools/ner",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, ImpressoNamedEntityRecognitionResponse]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = ImpressoNamedEntityRecognitionResponse.from_dict(response.json())

        return response_201
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = Error.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = Error.from_dict(response.json())

        return response_403
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
) -> Response[Union[Error, ImpressoNamedEntityRecognitionResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ImpressoNamedEntityRecognitionRequest,
) -> Response[Union[Error, ImpressoNamedEntityRecognitionResponse]]:
    """Perform named entity recognition (and optional named entity linking) of a text

    Args:
        body (ImpressoNamedEntityRecognitionRequest): Request body for the Impresso NER endpoint

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, ImpressoNamedEntityRecognitionResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: ImpressoNamedEntityRecognitionRequest,
) -> Optional[Union[Error, ImpressoNamedEntityRecognitionResponse]]:
    """Perform named entity recognition (and optional named entity linking) of a text

    Args:
        body (ImpressoNamedEntityRecognitionRequest): Request body for the Impresso NER endpoint

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, ImpressoNamedEntityRecognitionResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ImpressoNamedEntityRecognitionRequest,
) -> Response[Union[Error, ImpressoNamedEntityRecognitionResponse]]:
    """Perform named entity recognition (and optional named entity linking) of a text

    Args:
        body (ImpressoNamedEntityRecognitionRequest): Request body for the Impresso NER endpoint

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, ImpressoNamedEntityRecognitionResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ImpressoNamedEntityRecognitionRequest,
) -> Optional[Union[Error, ImpressoNamedEntityRecognitionResponse]]:
    """Perform named entity recognition (and optional named entity linking) of a text

    Args:
        body (ImpressoNamedEntityRecognitionRequest): Request body for the Impresso NER endpoint

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, ImpressoNamedEntityRecognitionResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
