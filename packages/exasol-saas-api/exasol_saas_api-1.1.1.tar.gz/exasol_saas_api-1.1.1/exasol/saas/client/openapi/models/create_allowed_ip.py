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

T = TypeVar("T", bound="CreateAllowedIP")


@_attrs_define
class CreateAllowedIP:
    """
    Attributes:
        name (str):
        cidr_ip (str):
    """

    name: str
    cidr_ip: str

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        cidr_ip = self.cidr_ip

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "cidrIp": cidr_ip,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        cidr_ip = d.pop("cidrIp")

        create_allowed_ip = cls(
            name=name,
            cidr_ip=cidr_ip,
        )

        return create_allowed_ip
