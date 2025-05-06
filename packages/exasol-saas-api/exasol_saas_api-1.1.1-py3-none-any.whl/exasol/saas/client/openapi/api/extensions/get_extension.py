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
from ...models.api_error import ApiError
from ...models.extension_detail import ExtensionDetail
from ...types import (
    UNSET,
    Response,
)


def _get_kwargs(
    account_id: str,
    database_id: str,
    extension_id: str,
    extension_version: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/accounts/{account_id}/databases/{database_id}/extensions/{extension_id}/{extension_version}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ApiError, ExtensionDetail]]:
    if response.status_code == 200:
        response_200 = ExtensionDetail.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = ApiError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ApiError, ExtensionDetail]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    database_id: str,
    extension_id: str,
    extension_version: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ApiError, ExtensionDetail]]:
    """
    Args:
        account_id (str):
        database_id (str):
        extension_id (str):
        extension_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiError, ExtensionDetail]]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        database_id=database_id,
        extension_id=extension_id,
        extension_version=extension_version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    database_id: str,
    extension_id: str,
    extension_version: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ApiError, ExtensionDetail]]:
    """
    Args:
        account_id (str):
        database_id (str):
        extension_id (str):
        extension_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiError, ExtensionDetail]
    """

    return sync_detailed(
        account_id=account_id,
        database_id=database_id,
        extension_id=extension_id,
        extension_version=extension_version,
        client=client,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    database_id: str,
    extension_id: str,
    extension_version: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ApiError, ExtensionDetail]]:
    """
    Args:
        account_id (str):
        database_id (str):
        extension_id (str):
        extension_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiError, ExtensionDetail]]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        database_id=database_id,
        extension_id=extension_id,
        extension_version=extension_version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    database_id: str,
    extension_id: str,
    extension_version: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ApiError, ExtensionDetail]]:
    """
    Args:
        account_id (str):
        database_id (str):
        extension_id (str):
        extension_version (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiError, ExtensionDetail]
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            database_id=database_id,
            extension_id=extension_id,
            extension_version=extension_version,
            client=client,
        )
    ).parsed
