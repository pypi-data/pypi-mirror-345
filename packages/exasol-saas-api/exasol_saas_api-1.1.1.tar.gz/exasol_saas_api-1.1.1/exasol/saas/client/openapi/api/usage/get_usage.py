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
from ...models.get_usage_type import GetUsageType
from ...models.usage import Usage
from ...types import (
    UNSET,
    Response,
    Unset,
)


def _get_kwargs(
    account_id: str,
    *,
    year_month: Union[Unset, str] = UNSET,
    type_: Union[Unset, GetUsageType] = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["yearMonth"] = year_month

    json_type_: Union[Unset, str] = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/accounts/{account_id}/usage",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Usage]:
    if response.status_code == 200:
        response_200 = Usage.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Usage]:
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
    year_month: Union[Unset, str] = UNSET,
    type_: Union[Unset, GetUsageType] = UNSET,
) -> Response[Usage]:
    """
    Args:
        account_id (str):
        year_month (Union[Unset, str]):
        type_ (Union[Unset, GetUsageType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Usage]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        year_month=year_month,
        type_=type_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    *,
    client: AuthenticatedClient,
    year_month: Union[Unset, str] = UNSET,
    type_: Union[Unset, GetUsageType] = UNSET,
) -> Optional[Usage]:
    """
    Args:
        account_id (str):
        year_month (Union[Unset, str]):
        type_ (Union[Unset, GetUsageType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Usage
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        year_month=year_month,
        type_=type_,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    year_month: Union[Unset, str] = UNSET,
    type_: Union[Unset, GetUsageType] = UNSET,
) -> Response[Usage]:
    """
    Args:
        account_id (str):
        year_month (Union[Unset, str]):
        type_ (Union[Unset, GetUsageType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Usage]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        year_month=year_month,
        type_=type_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    *,
    client: AuthenticatedClient,
    year_month: Union[Unset, str] = UNSET,
    type_: Union[Unset, GetUsageType] = UNSET,
) -> Optional[Usage]:
    """
    Args:
        account_id (str):
        year_month (Union[Unset, str]):
        type_ (Union[Unset, GetUsageType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Usage
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            year_month=year_month,
            type_=type_,
        )
    ).parsed
