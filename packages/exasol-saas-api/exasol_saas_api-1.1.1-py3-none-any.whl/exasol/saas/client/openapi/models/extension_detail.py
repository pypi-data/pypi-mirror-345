from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Optional,
    TextIO,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.extension_parameter_definitions import ExtensionParameterDefinitions


T = TypeVar("T", bound="ExtensionDetail")


@_attrs_define
class ExtensionDetail:
    """
    Attributes:
        id (str):
        version (str):
        parameter_definitions (list['ExtensionParameterDefinitions']):
    """

    id: str
    version: str
    parameter_definitions: list["ExtensionParameterDefinitions"]

    def to_dict(self) -> dict[str, Any]:
        from ..models.extension_parameter_definitions import (
            ExtensionParameterDefinitions,
        )

        id = self.id

        version = self.version

        parameter_definitions = []
        for parameter_definitions_item_data in self.parameter_definitions:
            parameter_definitions_item = parameter_definitions_item_data.to_dict()
            parameter_definitions.append(parameter_definitions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "version": version,
                "parameterDefinitions": parameter_definitions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.extension_parameter_definitions import (
            ExtensionParameterDefinitions,
        )

        d = dict(src_dict)
        id = d.pop("id")

        version = d.pop("version")

        parameter_definitions = []
        _parameter_definitions = d.pop("parameterDefinitions")
        for parameter_definitions_item_data in _parameter_definitions:
            parameter_definitions_item = ExtensionParameterDefinitions.from_dict(
                parameter_definitions_item_data
            )

            parameter_definitions.append(parameter_definitions_item)

        extension_detail = cls(
            id=id,
            version=version,
            parameter_definitions=parameter_definitions,
        )

        return extension_detail
