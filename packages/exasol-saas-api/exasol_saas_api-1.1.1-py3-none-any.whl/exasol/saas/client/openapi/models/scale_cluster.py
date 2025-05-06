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

T = TypeVar("T", bound="ScaleCluster")


@_attrs_define
class ScaleCluster:
    """
    Attributes:
        size (str):
    """

    size: str

    def to_dict(self) -> dict[str, Any]:
        size = self.size

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "size": size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        size = d.pop("size")

        scale_cluster = cls(
            size=size,
        )

        return scale_cluster
