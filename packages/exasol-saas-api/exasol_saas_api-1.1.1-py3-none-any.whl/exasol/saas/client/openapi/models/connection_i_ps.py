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

T = TypeVar("T", bound="ConnectionIPs")


@_attrs_define
class ConnectionIPs:
    """
    Attributes:
        private (list[str]):
        public (list[str]):
    """

    private: list[str]
    public: list[str]

    def to_dict(self) -> dict[str, Any]:
        private = self.private

        public = self.public

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "private": private,
                "public": public,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        private = cast(list[str], d.pop("private"))

        public = cast(list[str], d.pop("public"))

        connection_i_ps = cls(
            private=private,
            public=public,
        )

        return connection_i_ps
