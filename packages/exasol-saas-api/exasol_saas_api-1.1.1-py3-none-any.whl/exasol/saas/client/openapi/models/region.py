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

T = TypeVar("T", bound="Region")


@_attrs_define
class Region:
    """
    Attributes:
        id (str):
        name (str):
        price_multiplier (float):
        storage_price (float):
    """

    id: str
    name: str
    price_multiplier: float
    storage_price: float

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        price_multiplier = self.price_multiplier

        storage_price = self.storage_price

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "priceMultiplier": price_multiplier,
                "storagePrice": storage_price,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        price_multiplier = d.pop("priceMultiplier")

        storage_price = d.pop("storagePrice")

        region = cls(
            id=id,
            name=name,
            price_multiplier=price_multiplier,
            storage_price=storage_price,
        )

        return region
