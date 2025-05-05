from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateProjectResponse200")


@_attrs_define
class UpdateProjectResponse200:
    """
    Attributes:
        fav (Union[Unset, bool]):
        project_id (Union[Unset, str]):
    """

    fav: Union[Unset, bool] = UNSET
    project_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fav = self.fav

        project_id = self.project_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fav is not UNSET:
            field_dict["fav"] = fav
        if project_id is not UNSET:
            field_dict["project_id"] = project_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fav = d.pop("fav", UNSET)

        project_id = d.pop("project_id", UNSET)

        update_project_response_200 = cls(
            fav=fav,
            project_id=project_id,
        )

        update_project_response_200.additional_properties = d
        return update_project_response_200

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
