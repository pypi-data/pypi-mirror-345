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

from ..models.schedule_action_type_0 import ScheduleActionType0
from ..types import (
    UNSET,
    Unset,
)

if TYPE_CHECKING:
    from ..models.cluster_action_scale import ClusterActionScale
    from ..models.cluster_action_start_stop import ClusterActionStartStop


T = TypeVar("T", bound="Schedule")


@_attrs_define
class Schedule:
    """
    Attributes:
        action (ScheduleActionType0):
        cron_rule (str): cron rule in format: <minute> <hour> <day> <month> <weekday>
        id (Union[Unset, str]):
        createdby_id (Union[Unset, str]):
        createdby_first_name (Union[Unset, str]):
        createdby_last_name (Union[Unset, str]):
        cluster_name (Union[Unset, str]):
        payload (Union['ClusterActionScale', 'ClusterActionStartStop', Unset]):
    """

    action: ScheduleActionType0
    cron_rule: str
    id: Union[Unset, str] = UNSET
    createdby_id: Union[Unset, str] = UNSET
    createdby_first_name: Union[Unset, str] = UNSET
    createdby_last_name: Union[Unset, str] = UNSET
    cluster_name: Union[Unset, str] = UNSET
    payload: Union["ClusterActionScale", "ClusterActionStartStop", Unset] = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.cluster_action_scale import ClusterActionScale
        from ..models.cluster_action_start_stop import ClusterActionStartStop

        action: str
        if isinstance(self.action, ScheduleActionType0):
            action = self.action.value

        cron_rule = self.cron_rule

        id = self.id

        createdby_id = self.createdby_id

        createdby_first_name = self.createdby_first_name

        createdby_last_name = self.createdby_last_name

        cluster_name = self.cluster_name

        payload: Union[Unset, dict[str, Any]]
        if isinstance(self.payload, Unset):
            payload = UNSET
        elif isinstance(self.payload, ClusterActionScale):
            payload = self.payload.to_dict()
        else:
            payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "action": action,
                "cronRule": cron_rule,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if createdby_id is not UNSET:
            field_dict["createdbyID"] = createdby_id
        if createdby_first_name is not UNSET:
            field_dict["createdbyFirstName"] = createdby_first_name
        if createdby_last_name is not UNSET:
            field_dict["createdbyLastName"] = createdby_last_name
        if cluster_name is not UNSET:
            field_dict["clusterName"] = cluster_name
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster_action_scale import ClusterActionScale
        from ..models.cluster_action_start_stop import ClusterActionStartStop

        d = dict(src_dict)

        def _parse_action(data: object) -> ScheduleActionType0:
            if not isinstance(data, str):
                raise TypeError()
            action_type_0 = ScheduleActionType0(data)

            return action_type_0

        action = _parse_action(d.pop("action"))

        cron_rule = d.pop("cronRule")

        id = d.pop("id", UNSET)

        createdby_id = d.pop("createdbyID", UNSET)

        createdby_first_name = d.pop("createdbyFirstName", UNSET)

        createdby_last_name = d.pop("createdbyLastName", UNSET)

        cluster_name = d.pop("clusterName", UNSET)

        def _parse_payload(
            data: object,
        ) -> Union["ClusterActionScale", "ClusterActionStartStop", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                payload_type_0 = ClusterActionScale.from_dict(data)

                return payload_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            payload_type_1 = ClusterActionStartStop.from_dict(data)

            return payload_type_1

        payload = _parse_payload(d.pop("payload", UNSET))

        schedule = cls(
            action=action,
            cron_rule=cron_rule,
            id=id,
            createdby_id=createdby_id,
            createdby_first_name=createdby_first_name,
            createdby_last_name=createdby_last_name,
            cluster_name=cluster_name,
            payload=payload,
        )

        return schedule
