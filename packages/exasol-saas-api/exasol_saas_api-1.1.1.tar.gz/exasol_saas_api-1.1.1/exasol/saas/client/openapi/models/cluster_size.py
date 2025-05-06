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

T = TypeVar("T", bound="ClusterSize")


@_attrs_define
class ClusterSize:
    """
    Attributes:
        size (str):
        price (float):
        vcpu (float):
        ram (float):
        is_default (bool):
        name (str):
    """

    size: str
    price: float
    vcpu: float
    ram: float
    is_default: bool
    name: str

    def to_dict(self) -> dict[str, Any]:
        size = self.size

        price = self.price

        vcpu = self.vcpu

        ram = self.ram

        is_default = self.is_default

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "size": size,
                "price": price,
                "vcpu": vcpu,
                "ram": ram,
                "isDefault": is_default,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        size = d.pop("size")

        price = d.pop("price")

        vcpu = d.pop("vcpu")

        ram = d.pop("ram")

        is_default = d.pop("isDefault")

        name = d.pop("name")

        cluster_size = cls(
            size=size,
            price=price,
            vcpu=vcpu,
            ram=ram,
            is_default=is_default,
            name=name,
        )

        return cluster_size
