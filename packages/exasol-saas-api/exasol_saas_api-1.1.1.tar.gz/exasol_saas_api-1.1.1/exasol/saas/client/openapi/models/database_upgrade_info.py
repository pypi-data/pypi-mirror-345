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

T = TypeVar("T", bound="DatabaseUpgradeInfo")


@_attrs_define
class DatabaseUpgradeInfo:
    """
    Attributes:
        current_version (str):
        update_version (str):
        update_possible (bool):
    """

    current_version: str
    update_version: str
    update_possible: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        current_version = self.current_version

        update_version = self.update_version

        update_possible = self.update_possible

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "currentVersion": current_version,
                "updateVersion": update_version,
                "updatePossible": update_possible,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_version = d.pop("currentVersion")

        update_version = d.pop("updateVersion")

        update_possible = d.pop("updatePossible")

        database_upgrade_info = cls(
            current_version=current_version,
            update_version=update_version,
            update_possible=update_possible,
        )

        database_upgrade_info.additional_properties = d
        return database_upgrade_info

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
