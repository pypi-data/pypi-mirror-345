"""
Package openapi contains the API generated from the JSON definition.
"""

from dataclasses import dataclass
from datetime import (
    datetime,
    timedelta,
)
from typing import Final

from exasol.saas.client.openapi.models.status import Status

SAAS_HOST = "https://cloud.exasol.com"

PROMISING_STATES = [
    Status.CREATING,
    Status.RUNNING,
    Status.STARTING,
    Status.TOCREATE,
    Status.TOSTART,
]


class Limits:
    """
    Constants for Exasol SaaS databases.
    """

    MAX_DATABASE_NAME_LENGTH: Final[int] = 20
    MAX_CLUSTER_NAME_LENGTH: Final[int] = 40
    AUTOSTOP_MIN_IDLE_TIME: Final[timedelta] = timedelta(minutes=15)
    AUTOSTOP_MAX_IDLE_TIME: Final[timedelta] = timedelta(minutes=10000)
    AUTOSTOP_DEFAULT_IDLE_TIME: Final[timedelta] = timedelta(minutes=120)
    # If deleting a database too early, then logging and accounting could be invalid.
    MIN_DATABASE_LIFETIME: Final[timedelta] = timedelta(seconds=30)
