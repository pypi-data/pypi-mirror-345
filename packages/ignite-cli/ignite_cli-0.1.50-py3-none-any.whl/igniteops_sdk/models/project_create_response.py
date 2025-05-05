from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectCreateResponse")


@_attrs_define
class ProjectCreateResponse:
    """
    Attributes:
        execution_arn (Union[Unset, str]):
        message (Union[Unset, str]):
        status (Union[Unset, str]):
    """

    execution_arn: Union[Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        execution_arn = self.execution_arn

        message = self.message

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if execution_arn is not UNSET:
            field_dict["execution_arn"] = execution_arn
        if message is not UNSET:
            field_dict["message"] = message
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        execution_arn = d.pop("execution_arn", UNSET)

        message = d.pop("message", UNSET)

        status = d.pop("status", UNSET)

        project_create_response = cls(
            execution_arn=execution_arn,
            message=message,
            status=status,
        )

        project_create_response.additional_properties = d
        return project_create_response

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
