from http import HTTPStatus
from typing import (
    Any,
    Optional,
    Union,
    cast,
)

import httpx

from ... import errors
from ...client import (
    AuthenticatedClient,
    Client,
)
from ...models.region import Region
from ...types import (
    UNSET,
    Response,
)


def _get_kwargs(
    platform: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/platforms/{platform}/regions",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["Region"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Region.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Region"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    platform: str,
    *,
    client: AuthenticatedClient,
) -> Response[list["Region"]]:
    """
    Args:
        platform (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Region']]
    """

    kwargs = _get_kwargs(
        platform=platform,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    platform: str,
    *,
    client: AuthenticatedClient,
) -> Optional[list["Region"]]:
    """
    Args:
        platform (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Region']
    """

    return sync_detailed(
        platform=platform,
        client=client,
    ).parsed


async def asyncio_detailed(
    platform: str,
    *,
    client: AuthenticatedClient,
) -> Response[list["Region"]]:
    """
    Args:
        platform (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Region']]
    """

    kwargs = _get_kwargs(
        platform=platform,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    platform: str,
    *,
    client: AuthenticatedClient,
) -> Optional[list["Region"]]:
    """
    Args:
        platform (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Region']
    """

    return (
        await asyncio_detailed(
            platform=platform,
            client=client,
        )
    ).parsed
