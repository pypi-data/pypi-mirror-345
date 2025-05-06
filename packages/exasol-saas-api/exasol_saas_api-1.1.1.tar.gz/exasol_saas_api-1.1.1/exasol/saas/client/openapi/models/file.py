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

T = TypeVar("T", bound="File")


@_attrs_define
class File:
    """
    Attributes:
        name (str):
        type_ (str):
        path (str):
        last_modified (datetime.datetime):
        size (Union[Unset, int]):
        children (Union[Unset, list['File']]):
    """

    name: str
    type_: str
    path: str
    last_modified: datetime.datetime
    size: Union[Unset, int] = UNSET
    children: Union[Unset, list["File"]] = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        path = self.path

        last_modified = self.last_modified.isoformat()

        size = self.size

        children: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.children, Unset):
            children = []
            for children_item_data in self.children:
                children_item = children_item_data.to_dict()
                children.append(children_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "path": path,
                "lastModified": last_modified,
            }
        )
        if size is not UNSET:
            field_dict["size"] = size
        if children is not UNSET:
            field_dict["children"] = children

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_ = d.pop("type")

        path = d.pop("path")

        last_modified = isoparse(d.pop("lastModified"))

        size = d.pop("size", UNSET)

        children = []
        _children = d.pop("children", UNSET)
        for children_item_data in _children or []:
            children_item = File.from_dict(children_item_data)

            children.append(children_item)

        file = cls(
            name=name,
            type_=type_,
            path=path,
            last_modified=last_modified,
            size=size,
            children=children,
        )

        return file
