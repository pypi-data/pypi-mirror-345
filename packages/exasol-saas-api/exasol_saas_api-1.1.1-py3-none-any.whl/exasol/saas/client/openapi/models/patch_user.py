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

from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.patch_user_databases import PatchUserDatabases


T = TypeVar("T", bound="PatchUser")


@_attrs_define
class PatchUser:
    """
    Attributes:
        role_id (Union[Unset, str]):
        databases (Union[Unset, PatchUserDatabases]):
        db_username (Union[Unset, str]):
    """

    role_id: Union[Unset, str] = UNSET
    databases: Union[Unset, "PatchUserDatabases"] = UNSET
    db_username: Union[Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.patch_user_databases import PatchUserDatabases

        role_id = self.role_id

        databases: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.databases, Unset):
            databases = self.databases.to_dict()

        db_username = self.db_username

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if role_id is not UNSET:
            field_dict["roleID"] = role_id
        if databases is not UNSET:
            field_dict["databases"] = databases
        if db_username is not UNSET:
            field_dict["dbUsername"] = db_username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_user_databases import PatchUserDatabases

        d = dict(src_dict)
        role_id = d.pop("roleID", UNSET)

        _databases = d.pop("databases", UNSET)
        databases: Union[Unset, PatchUserDatabases]
        if isinstance(_databases, Unset):
            databases = UNSET
        else:
            databases = PatchUserDatabases.from_dict(_databases)

        db_username = d.pop("dbUsername", UNSET)

        patch_user = cls(
            role_id=role_id,
            databases=databases,
            db_username=db_username,
        )

        return patch_user
