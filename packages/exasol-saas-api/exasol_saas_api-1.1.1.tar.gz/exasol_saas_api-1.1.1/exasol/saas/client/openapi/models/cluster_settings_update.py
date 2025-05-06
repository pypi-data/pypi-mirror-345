from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Optional,
    TextIO,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="ClusterSettingsUpdate")


@_attrs_define
class ClusterSettingsUpdate:
    """
    Attributes:
        offload_enabled (Union[Unset, bool]):
        offload_timeout_min (Union[Unset, int]):
    """

    offload_enabled: Union[Unset, bool] = UNSET
    offload_timeout_min: Union[Unset, int] = UNSET

    def to_dict(self) -> dict[str, Any]:
        offload_enabled = self.offload_enabled

        offload_timeout_min = self.offload_timeout_min

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if offload_enabled is not UNSET:
            field_dict["offloadEnabled"] = offload_enabled
        if offload_timeout_min is not UNSET:
            field_dict["offloadTimeoutMin"] = offload_timeout_min

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        offload_enabled = d.pop("offloadEnabled", UNSET)

        offload_timeout_min = d.pop("offloadTimeoutMin", UNSET)

        cluster_settings_update = cls(
            offload_enabled=offload_enabled,
            offload_timeout_min=offload_timeout_min,
        )

        return cluster_settings_update
