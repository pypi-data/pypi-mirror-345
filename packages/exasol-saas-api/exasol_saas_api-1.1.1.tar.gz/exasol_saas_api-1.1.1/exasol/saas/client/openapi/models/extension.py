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
    from ..models.extension_version import ExtensionVersion


T = TypeVar("T", bound="Extension")


@_attrs_define
class Extension:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        category_id (str):
        installable_versions (list['ExtensionVersion']):
    """

    id: str
    name: str
    description: str
    category_id: str
    installable_versions: list["ExtensionVersion"]

    def to_dict(self) -> dict[str, Any]:
        from ..models.extension_version import ExtensionVersion

        id = self.id

        name = self.name

        description = self.description

        category_id = self.category_id

        installable_versions = []
        for installable_versions_item_data in self.installable_versions:
            installable_versions_item = installable_versions_item_data.to_dict()
            installable_versions.append(installable_versions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "categoryId": category_id,
                "installableVersions": installable_versions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.extension_version import ExtensionVersion

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        category_id = d.pop("categoryId")

        installable_versions = []
        _installable_versions = d.pop("installableVersions")
        for installable_versions_item_data in _installable_versions:
            installable_versions_item = ExtensionVersion.from_dict(
                installable_versions_item_data
            )

            installable_versions.append(installable_versions_item)

        extension = cls(
            id=id,
            name=name,
            description=description,
            category_id=category_id,
            installable_versions=installable_versions,
        )

        return extension
