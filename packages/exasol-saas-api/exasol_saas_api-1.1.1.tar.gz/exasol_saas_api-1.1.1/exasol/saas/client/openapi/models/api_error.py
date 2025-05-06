from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Optional,
    TextIO,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="ApiError")


@_attrs_define
class ApiError:
    """
    Attributes:
        status (float):
        message (str):
        request_id (str):
        path (str):
        method (str):
        log_id (str):
        handler (str):
        timestamp (str):
        causes (Union[Unset, Any]):
    """

    status: float
    message: str
    request_id: str
    path: str
    method: str
    log_id: str
    handler: str
    timestamp: str
    causes: Union[Unset, Any] = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        message = self.message

        request_id = self.request_id

        path = self.path

        method = self.method

        log_id = self.log_id

        handler = self.handler

        timestamp = self.timestamp

        causes = self.causes

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
                "message": message,
                "requestId": request_id,
                "path": path,
                "method": method,
                "logId": log_id,
                "handler": handler,
                "timestamp": timestamp,
            }
        )
        if causes is not UNSET:
            field_dict["causes"] = causes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        message = d.pop("message")

        request_id = d.pop("requestId")

        path = d.pop("path")

        method = d.pop("method")

        log_id = d.pop("logId")

        handler = d.pop("handler")

        timestamp = d.pop("timestamp")

        causes = d.pop("causes", UNSET)

        api_error = cls(
            status=status,
            message=message,
            request_id=request_id,
            path=path,
            method=method,
            log_id=log_id,
            handler=handler,
            timestamp=timestamp,
            causes=causes,
        )

        return api_error
