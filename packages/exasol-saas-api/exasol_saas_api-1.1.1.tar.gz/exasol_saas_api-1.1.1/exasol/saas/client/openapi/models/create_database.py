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
    from ..models.create_database_initial_cluster import CreateDatabaseInitialCluster


T = TypeVar("T", bound="CreateDatabase")


@_attrs_define
class CreateDatabase:
    """
    Attributes:
        name (str):
        initial_cluster (CreateDatabaseInitialCluster):
        provider (str):
        region (str):
        num_nodes (Union[Unset, int]):
        stream_type (Union[Unset, str]):
    """

    name: str
    initial_cluster: "CreateDatabaseInitialCluster"
    provider: str
    region: str
    num_nodes: Union[Unset, int] = UNSET
    stream_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.create_database_initial_cluster import (
            CreateDatabaseInitialCluster,
        )

        name = self.name

        initial_cluster = self.initial_cluster.to_dict()

        provider = self.provider

        region = self.region

        num_nodes = self.num_nodes

        stream_type = self.stream_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "initialCluster": initial_cluster,
                "provider": provider,
                "region": region,
            }
        )
        if num_nodes is not UNSET:
            field_dict["numNodes"] = num_nodes
        if stream_type is not UNSET:
            field_dict["streamType"] = stream_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_database_initial_cluster import (
            CreateDatabaseInitialCluster,
        )

        d = dict(src_dict)
        name = d.pop("name")

        initial_cluster = CreateDatabaseInitialCluster.from_dict(
            d.pop("initialCluster")
        )

        provider = d.pop("provider")

        region = d.pop("region")

        num_nodes = d.pop("numNodes", UNSET)

        stream_type = d.pop("streamType", UNSET)

        create_database = cls(
            name=name,
            initial_cluster=initial_cluster,
            provider=provider,
            region=region,
            num_nodes=num_nodes,
            stream_type=stream_type,
        )

        create_database.additional_properties = d
        return create_database

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
