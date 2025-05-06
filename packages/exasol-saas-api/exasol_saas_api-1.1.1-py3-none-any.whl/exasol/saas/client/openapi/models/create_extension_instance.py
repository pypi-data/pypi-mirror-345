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
    from ..models.extension_parameter_value import ExtensionParameterValue


T = TypeVar("T", bound="CreateExtensionInstance")


@_attrs_define
class CreateExtensionInstance:
    """
    Attributes:
        parameter_values (list['ExtensionParameterValue']):
    """

    parameter_values: list["ExtensionParameterValue"]

    def to_dict(self) -> dict[str, Any]:
        from ..models.extension_parameter_value import ExtensionParameterValue

        parameter_values = []
        for parameter_values_item_data in self.parameter_values:
            parameter_values_item = parameter_values_item_data.to_dict()
            parameter_values.append(parameter_values_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "parameterValues": parameter_values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.extension_parameter_value import ExtensionParameterValue

        d = dict(src_dict)
        parameter_values = []
        _parameter_values = d.pop("parameterValues")
        for parameter_values_item_data in _parameter_values:
            parameter_values_item = ExtensionParameterValue.from_dict(
                parameter_values_item_data
            )

            parameter_values.append(parameter_values_item)

        create_extension_instance = cls(
            parameter_values=parameter_values,
        )

        return create_extension_instance
