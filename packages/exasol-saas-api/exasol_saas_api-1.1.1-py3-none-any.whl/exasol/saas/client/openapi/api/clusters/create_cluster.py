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
from ...models.cluster import Cluster
from ...models.create_cluster import CreateCluster
from ...types import (
    UNSET,
    Response,
)


def _get_kwargs(
    account_id: str,
    database_id: str,
    *,
    body: CreateCluster,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/accounts/{account_id}/databases/{database_id}/clusters",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Cluster]:
    if response.status_code == 200:
        response_200 = Cluster.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Cluster]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    database_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateCluster,
) -> Response[Cluster]:
    """
    Args:
        account_id (str):
        database_id (str):
        body (CreateCluster):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Cluster]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        database_id=database_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    database_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateCluster,
) -> Optional[Cluster]:
    """
    Args:
        account_id (str):
        database_id (str):
        body (CreateCluster):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Cluster
    """

    return sync_detailed(
        account_id=account_id,
        database_id=database_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    database_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateCluster,
) -> Response[Cluster]:
    """
    Args:
        account_id (str):
        database_id (str):
        body (CreateCluster):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Cluster]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        database_id=database_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    database_id: str,
    *,
    client: AuthenticatedClient,
    body: CreateCluster,
) -> Optional[Cluster]:
    """
    Args:
        account_id (str):
        database_id (str):
        body (CreateCluster):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Cluster
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            database_id=database_id,
            client=client,
            body=body,
        )
    ).parsed
