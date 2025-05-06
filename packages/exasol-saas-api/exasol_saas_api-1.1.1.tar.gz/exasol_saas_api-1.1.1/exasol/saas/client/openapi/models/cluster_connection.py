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
    from ..models.connection_i_ps import ConnectionIPs


T = TypeVar("T", bound="ClusterConnection")


@_attrs_define
class ClusterConnection:
    """
    Attributes:
        dns (str):
        port (int):
        jdbc (str):
        ips (ConnectionIPs):
        db_username (str):
    """

    dns: str
    port: int
    jdbc: str
    ips: "ConnectionIPs"
    db_username: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.connection_i_ps import ConnectionIPs

        dns = self.dns

        port = self.port

        jdbc = self.jdbc

        ips = self.ips.to_dict()

        db_username = self.db_username

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "dns": dns,
                "port": port,
                "jdbc": jdbc,
                "ips": ips,
                "dbUsername": db_username,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_i_ps import ConnectionIPs

        d = dict(src_dict)
        dns = d.pop("dns")

        port = d.pop("port")

        jdbc = d.pop("jdbc")

        ips = ConnectionIPs.from_dict(d.pop("ips"))

        db_username = d.pop("dbUsername")

        cluster_connection = cls(
            dns=dns,
            port=port,
            jdbc=jdbc,
            ips=ips,
            db_username=db_username,
        )

        return cluster_connection
