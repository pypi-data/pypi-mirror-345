import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pat_permissions import PATPermissions


T = TypeVar("T", bound="PATCreateResponse")


@_attrs_define
class PATCreateResponse:
    """
    Attributes:
        expires_at (Union[None, Unset, datetime.datetime]):
        pat_id (Union[Unset, str]):
        permissions (Union[Unset, PATPermissions]):
        token (Union[Unset, str]):
    """

    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    pat_id: Union[Unset, str] = UNSET
    permissions: Union[Unset, "PATPermissions"] = UNSET
    token: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        pat_id = self.pat_id

        permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()

        token = self.token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at
        if pat_id is not UNSET:
            field_dict["patId"] = pat_id
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pat_permissions import PATPermissions

        d = dict(src_dict)

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expiresAt", UNSET))

        pat_id = d.pop("patId", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, PATPermissions]
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = PATPermissions.from_dict(_permissions)

        token = d.pop("token", UNSET)

        pat_create_response = cls(
            expires_at=expires_at,
            pat_id=pat_id,
            permissions=permissions,
            token=token,
        )

        pat_create_response.additional_properties = d
        return pat_create_response

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
