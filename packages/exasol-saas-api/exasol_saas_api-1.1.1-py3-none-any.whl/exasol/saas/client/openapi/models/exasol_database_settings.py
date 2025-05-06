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

T = TypeVar("T", bound="ExasolDatabaseSettings")


@_attrs_define
class ExasolDatabaseSettings:
    """
    Attributes:
        offload_enabled (bool):
        auto_updates_enabled (bool):
        auto_updates_hard_disabled (bool):
        num_nodes (int):
        stream_type (str):
        stream_description (str):
    """

    offload_enabled: bool
    auto_updates_enabled: bool
    auto_updates_hard_disabled: bool
    num_nodes: int
    stream_type: str
    stream_description: str

    def to_dict(self) -> dict[str, Any]:
        offload_enabled = self.offload_enabled

        auto_updates_enabled = self.auto_updates_enabled

        auto_updates_hard_disabled = self.auto_updates_hard_disabled

        num_nodes = self.num_nodes

        stream_type = self.stream_type

        stream_description = self.stream_description

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "offloadEnabled": offload_enabled,
                "autoUpdatesEnabled": auto_updates_enabled,
                "autoUpdatesHardDisabled": auto_updates_hard_disabled,
                "numNodes": num_nodes,
                "streamType": stream_type,
                "streamDescription": stream_description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        offload_enabled = d.pop("offloadEnabled")

        auto_updates_enabled = d.pop("autoUpdatesEnabled")

        auto_updates_hard_disabled = d.pop("autoUpdatesHardDisabled")

        num_nodes = d.pop("numNodes")

        stream_type = d.pop("streamType")

        stream_description = d.pop("streamDescription")

        exasol_database_settings = cls(
            offload_enabled=offload_enabled,
            auto_updates_enabled=auto_updates_enabled,
            auto_updates_hard_disabled=auto_updates_hard_disabled,
            num_nodes=num_nodes,
            stream_type=stream_type,
            stream_description=stream_description,
        )

        return exasol_database_settings
