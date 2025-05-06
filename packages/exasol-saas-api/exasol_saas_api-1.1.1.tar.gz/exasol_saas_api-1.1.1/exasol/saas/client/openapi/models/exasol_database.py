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

from ..models.status import Status
from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.exasol_database_clusters import ExasolDatabaseClusters
    from ..models.exasol_database_integrations_item import (
        ExasolDatabaseIntegrationsItem,
    )
    from ..models.exasol_database_settings import ExasolDatabaseSettings


T = TypeVar("T", bound="ExasolDatabase")


@_attrs_define
class ExasolDatabase:
    """
    Attributes:
        status (Status):
        id (str):
        name (str):
        clusters (ExasolDatabaseClusters):
        provider (str):
        region (str):
        created_at (datetime.datetime):
        created_by (str):
        settings (ExasolDatabaseSettings):
        integrations (Union[Unset, list['ExasolDatabaseIntegrationsItem']]):
        deleted_by (Union[Unset, str]):
        deleted_at (Union[Unset, datetime.datetime]):
    """

    status: Status
    id: str
    name: str
    clusters: "ExasolDatabaseClusters"
    provider: str
    region: str
    created_at: datetime.datetime
    created_by: str
    settings: "ExasolDatabaseSettings"
    integrations: Union[Unset, list["ExasolDatabaseIntegrationsItem"]] = UNSET
    deleted_by: Union[Unset, str] = UNSET
    deleted_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.exasol_database_clusters import ExasolDatabaseClusters
        from ..models.exasol_database_integrations_item import (
            ExasolDatabaseIntegrationsItem,
        )
        from ..models.exasol_database_settings import ExasolDatabaseSettings

        status = self.status.value

        id = self.id

        name = self.name

        clusters = self.clusters.to_dict()

        provider = self.provider

        region = self.region

        created_at = self.created_at.isoformat()

        created_by = self.created_by

        settings = self.settings.to_dict()

        integrations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.integrations, Unset):
            integrations = []
            for integrations_item_data in self.integrations:
                integrations_item = integrations_item_data.to_dict()
                integrations.append(integrations_item)

        deleted_by = self.deleted_by

        deleted_at: Union[Unset, str] = UNSET
        if not isinstance(self.deleted_at, Unset):
            deleted_at = self.deleted_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "id": id,
                "name": name,
                "clusters": clusters,
                "provider": provider,
                "region": region,
                "createdAt": created_at,
                "createdBy": created_by,
                "settings": settings,
            }
        )
        if integrations is not UNSET:
            field_dict["integrations"] = integrations
        if deleted_by is not UNSET:
            field_dict["deletedBy"] = deleted_by
        if deleted_at is not UNSET:
            field_dict["deletedAt"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.exasol_database_clusters import ExasolDatabaseClusters
        from ..models.exasol_database_integrations_item import (
            ExasolDatabaseIntegrationsItem,
        )
        from ..models.exasol_database_settings import ExasolDatabaseSettings

        d = dict(src_dict)
        status = Status(d.pop("status"))

        id = d.pop("id")

        name = d.pop("name")

        clusters = ExasolDatabaseClusters.from_dict(d.pop("clusters"))

        provider = d.pop("provider")

        region = d.pop("region")

        created_at = isoparse(d.pop("createdAt"))

        created_by = d.pop("createdBy")

        settings = ExasolDatabaseSettings.from_dict(d.pop("settings"))

        integrations = []
        _integrations = d.pop("integrations", UNSET)
        for integrations_item_data in _integrations or []:
            integrations_item = ExasolDatabaseIntegrationsItem.from_dict(
                integrations_item_data
            )

            integrations.append(integrations_item)

        deleted_by = d.pop("deletedBy", UNSET)

        _deleted_at = d.pop("deletedAt", UNSET)
        deleted_at: Union[Unset, datetime.datetime]
        if isinstance(_deleted_at, Unset):
            deleted_at = UNSET
        else:
            deleted_at = isoparse(_deleted_at)

        exasol_database = cls(
            status=status,
            id=id,
            name=name,
            clusters=clusters,
            provider=provider,
            region=region,
            created_at=created_at,
            created_by=created_by,
            settings=settings,
            integrations=integrations,
            deleted_by=deleted_by,
            deleted_at=deleted_at,
        )

        exasol_database.additional_properties = d
        return exasol_database

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
