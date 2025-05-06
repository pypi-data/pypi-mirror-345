from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Optional,
    TextIO,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="ExasolDatabaseClusters")


@_attrs_define
class ExasolDatabaseClusters:
    """
    Attributes:
        total (int):
        running (int):
    """

    total: int
    running: int

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        running = self.running

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "total": total,
                "running": running,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total = d.pop("total")

        running = d.pop("running")

        exasol_database_clusters = cls(
            total=total,
            running=running,
        )

        return exasol_database_clusters
