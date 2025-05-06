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
from ...models.user import User
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    account_id: str,
    *,
    filter_: Union[Unset, str] = UNSET,
    next_: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["filter"] = filter_

    params["next"] = next_

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/accounts/{account_id}/users",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["User"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = User.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["User"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    filter_: Union[Unset, str] = UNSET,
    next_: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[list["User"]]:
    """
    Args:
        account_id (str):
        filter_ (Union[Unset, str]):
        next_ (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['User']]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        filter_=filter_,
        next_=next_,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    *,
    client: AuthenticatedClient,
    filter_: Union[Unset, str] = UNSET,
    next_: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[list["User"]]:
    """
    Args:
        account_id (str):
        filter_ (Union[Unset, str]):
        next_ (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['User']
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        filter_=filter_,
        next_=next_,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    filter_: Union[Unset, str] = UNSET,
    next_: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[list["User"]]:
    """
    Args:
        account_id (str):
        filter_ (Union[Unset, str]):
        next_ (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['User']]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        filter_=filter_,
        next_=next_,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    *,
    client: AuthenticatedClient,
    filter_: Union[Unset, str] = UNSET,
    next_: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[list["User"]]:
    """
    Args:
        account_id (str):
        filter_ (Union[Unset, str]):
        next_ (Union[Unset, int]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['User']
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            filter_=filter_,
            next_=next_,
            limit=limit,
        )
    ).parsed
