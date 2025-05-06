"""A client library for accessing Exasol SaaS REST-API"""

from .client import (
    AuthenticatedClient,
    Client,
)

__all__ = (
    "AuthenticatedClient",
    "Client",
)
