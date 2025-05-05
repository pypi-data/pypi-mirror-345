from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.pat_create_response import PATCreateResponse
from ...types import Response


def _get_kwargs(
    pat_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/service/pats/{pat_id}/reissue".format(
            pat_id=pat_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, PATCreateResponse]]:
    if response.status_code == 201:
        response_201 = PATCreateResponse.from_dict(response.json())

        return response_201
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, PATCreateResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pat_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, PATCreateResponse]]:
    """Re-issue a Personal Access Token (generate a new secret)

     Generates a new secret for the specified PAT and returns it.

    Args:
        pat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PATCreateResponse]]
    """

    kwargs = _get_kwargs(
        pat_id=pat_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pat_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, PATCreateResponse]]:
    """Re-issue a Personal Access Token (generate a new secret)

     Generates a new secret for the specified PAT and returns it.

    Args:
        pat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PATCreateResponse]
    """

    return sync_detailed(
        pat_id=pat_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    pat_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, PATCreateResponse]]:
    """Re-issue a Personal Access Token (generate a new secret)

     Generates a new secret for the specified PAT and returns it.

    Args:
        pat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PATCreateResponse]]
    """

    kwargs = _get_kwargs(
        pat_id=pat_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pat_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, PATCreateResponse]]:
    """Re-issue a Personal Access Token (generate a new secret)

     Generates a new secret for the specified PAT and returns it.

    Args:
        pat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PATCreateResponse]
    """

    return (
        await asyncio_detailed(
            pat_id=pat_id,
            client=client,
        )
    ).parsed
