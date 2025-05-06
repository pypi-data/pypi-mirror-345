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

T = TypeVar("T", bound="ExtensionParameterValue")


@_attrs_define
class ExtensionParameterValue:
    """
    Attributes:
        id (str):
        value (str):
    """

    id: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        value = d.pop("value")

        extension_parameter_value = cls(
            id=id,
            value=value,
        )

        return extension_parameter_value
