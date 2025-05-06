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

from ..models.user_status import UserStatus
from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.user_database import UserDatabase
    from ..models.user_role import UserRole


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        email (str):
        id (str):
        created_at (datetime.datetime):
        created_by (str):
        status (UserStatus):
        roles (list['UserRole']):
        is_deletable (bool):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        databases (Union[Unset, list['UserDatabase']]):
        db_username (Union[Unset, str]):
    """

    email: str
    id: str
    created_at: datetime.datetime
    created_by: str
    status: UserStatus
    roles: list["UserRole"]
    is_deletable: bool
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    databases: Union[Unset, list["UserDatabase"]] = UNSET
    db_username: Union[Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_database import UserDatabase
        from ..models.user_role import UserRole

        email = self.email

        id = self.id

        created_at = self.created_at.isoformat()

        created_by = self.created_by

        status = self.status.value

        roles = []
        for roles_item_data in self.roles:
            roles_item = roles_item_data.to_dict()
            roles.append(roles_item)

        is_deletable = self.is_deletable

        first_name = self.first_name

        last_name = self.last_name

        databases: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.databases, Unset):
            databases = []
            for databases_item_data in self.databases:
                databases_item = databases_item_data.to_dict()
                databases.append(databases_item)

        db_username = self.db_username

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "email": email,
                "id": id,
                "createdAt": created_at,
                "createdBy": created_by,
                "status": status,
                "roles": roles,
                "isDeletable": is_deletable,
            }
        )
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if databases is not UNSET:
            field_dict["databases"] = databases
        if db_username is not UNSET:
            field_dict["dbUsername"] = db_username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_database import UserDatabase
        from ..models.user_role import UserRole

        d = dict(src_dict)
        email = d.pop("email")

        id = d.pop("id")

        created_at = isoparse(d.pop("createdAt"))

        created_by = d.pop("createdBy")

        status = UserStatus(d.pop("status"))

        roles = []
        _roles = d.pop("roles")
        for roles_item_data in _roles:
            roles_item = UserRole.from_dict(roles_item_data)

            roles.append(roles_item)

        is_deletable = d.pop("isDeletable")

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        databases = []
        _databases = d.pop("databases", UNSET)
        for databases_item_data in _databases or []:
            databases_item = UserDatabase.from_dict(databases_item_data)

            databases.append(databases_item)

        db_username = d.pop("dbUsername", UNSET)

        user = cls(
            email=email,
            id=id,
            created_at=created_at,
            created_by=created_by,
            status=status,
            roles=roles,
            is_deletable=is_deletable,
            first_name=first_name,
            last_name=last_name,
            databases=databases,
            db_username=db_username,
        )

        return user
