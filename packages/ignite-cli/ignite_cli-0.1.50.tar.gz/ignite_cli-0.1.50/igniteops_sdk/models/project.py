import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Project")


@_attrs_define
class Project:
    """
    Attributes:
        created_at (Union[Unset, datetime.datetime]):
        description (Union[Unset, str]):
        fav (Union[Unset, bool]):
        framework (Union[Unset, str]):
        language (Union[Unset, str]):
        name (Union[Unset, str]):
        project_id (Union[Unset, str]):
        repository_name (Union[Unset, str]):
        repository_url (Union[Unset, str]):
        status (Union[Unset, str]):
        updated_at (Union[Unset, datetime.datetime]):
    """

    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[Unset, str] = UNSET
    fav: Union[Unset, bool] = UNSET
    framework: Union[Unset, str] = UNSET
    language: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    project_id: Union[Unset, str] = UNSET
    repository_name: Union[Unset, str] = UNSET
    repository_url: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        description = self.description

        fav = self.fav

        framework = self.framework

        language = self.language

        name = self.name

        project_id = self.project_id

        repository_name = self.repository_name

        repository_url = self.repository_url

        status = self.status

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if fav is not UNSET:
            field_dict["fav"] = fav
        if framework is not UNSET:
            field_dict["framework"] = framework
        if language is not UNSET:
            field_dict["language"] = language
        if name is not UNSET:
            field_dict["name"] = name
        if project_id is not UNSET:
            field_dict["project_id"] = project_id
        if repository_name is not UNSET:
            field_dict["repository_name"] = repository_name
        if repository_url is not UNSET:
            field_dict["repository_url"] = repository_url
        if status is not UNSET:
            field_dict["status"] = status
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        description = d.pop("description", UNSET)

        fav = d.pop("fav", UNSET)

        framework = d.pop("framework", UNSET)

        language = d.pop("language", UNSET)

        name = d.pop("name", UNSET)

        project_id = d.pop("project_id", UNSET)

        repository_name = d.pop("repository_name", UNSET)

        repository_url = d.pop("repository_url", UNSET)

        status = d.pop("status", UNSET)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        project = cls(
            created_at=created_at,
            description=description,
            fav=fav,
            framework=framework,
            language=language,
            name=name,
            project_id=project_id,
            repository_name=repository_name,
            repository_url=repository_url,
            status=status,
            updated_at=updated_at,
        )

        project.additional_properties = d
        return project

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
