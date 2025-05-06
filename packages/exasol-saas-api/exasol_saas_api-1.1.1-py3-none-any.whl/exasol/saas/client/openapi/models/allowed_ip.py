import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Optional,
    TextIO,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="AllowedIP")


@_attrs_define
class AllowedIP:
    """
    Attributes:
        id (str):
        name (str):
        cidr_ip (str):
        created_at (datetime.datetime):
        created_by (str):
        deleted_by (Union[Unset, str]):
        deleted_at (Union[Unset, datetime.datetime]):
    """

    id: str
    name: str
    cidr_ip: str
    created_at: datetime.datetime
    created_by: str
    deleted_by: Union[Unset, str] = UNSET
    deleted_at: Union[Unset, datetime.datetime] = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        cidr_ip = self.cidr_ip

        created_at = self.created_at.isoformat()

        created_by = self.created_by

        deleted_by = self.deleted_by

        deleted_at: Union[Unset, str] = UNSET
        if not isinstance(self.deleted_at, Unset):
            deleted_at = self.deleted_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "cidrIp": cidr_ip,
                "createdAt": created_at,
                "createdBy": created_by,
            }
        )
        if deleted_by is not UNSET:
            field_dict["deletedBy"] = deleted_by
        if deleted_at is not UNSET:
            field_dict["deletedAt"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        cidr_ip = d.pop("cidrIp")

        created_at = isoparse(d.pop("createdAt"))

        created_by = d.pop("createdBy")

        deleted_by = d.pop("deletedBy", UNSET)

        _deleted_at = d.pop("deletedAt", UNSET)
        deleted_at: Union[Unset, datetime.datetime]
        if isinstance(_deleted_at, Unset):
            deleted_at = UNSET
        else:
            deleted_at = isoparse(_deleted_at)

        allowed_ip = cls(
            id=id,
            name=name,
            cidr_ip=cidr_ip,
            created_at=created_at,
            created_by=created_by,
            deleted_by=deleted_by,
            deleted_at=deleted_at,
        )

        return allowed_ip
