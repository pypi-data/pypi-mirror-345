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

T = TypeVar("T", bound="ExtensionVersion")


@_attrs_define
class ExtensionVersion:
    """
    Attributes:
        version (str):
        latest (bool):
        deprecated (bool):
        installed (bool):
    """

    version: str
    latest: bool
    deprecated: bool
    installed: bool

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        latest = self.latest

        deprecated = self.deprecated

        installed = self.installed

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "version": version,
                "latest": latest,
                "deprecated": deprecated,
                "installed": installed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version = d.pop("version")

        latest = d.pop("latest")

        deprecated = d.pop("deprecated")

        installed = d.pop("installed")

        extension_version = cls(
            version=version,
            latest=latest,
            deprecated=deprecated,
            installed=installed,
        )

        return extension_version
