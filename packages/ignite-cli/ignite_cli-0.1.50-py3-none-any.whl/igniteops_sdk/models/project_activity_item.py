import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.project_activity_item_detail import ProjectActivityItemDetail


T = TypeVar("T", bound="ProjectActivityItem")


@_attrs_define
class ProjectActivityItem:
    """
    Attributes:
        detail (Union[Unset, ProjectActivityItemDetail]):
        event_type (Union[Unset, str]):
        timestamp (Union[Unset, datetime.datetime]):
    """

    detail: Union[Unset, "ProjectActivityItemDetail"] = UNSET
    event_type: Union[Unset, str] = UNSET
    timestamp: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        detail: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.detail, Unset):
            detail = self.detail.to_dict()

        event_type = self.event_type

        timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if detail is not UNSET:
            field_dict["detail"] = detail
        if event_type is not UNSET:
            field_dict["event_type"] = event_type
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.project_activity_item_detail import ProjectActivityItemDetail

        d = dict(src_dict)
        _detail = d.pop("detail", UNSET)
        detail: Union[Unset, ProjectActivityItemDetail]
        if isinstance(_detail, Unset):
            detail = UNSET
        else:
            detail = ProjectActivityItemDetail.from_dict(_detail)

        event_type = d.pop("event_type", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: Union[Unset, datetime.datetime]
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        project_activity_item = cls(
            detail=detail,
            event_type=event_type,
            timestamp=timestamp,
        )

        project_activity_item.additional_properties = d
        return project_activity_item

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
