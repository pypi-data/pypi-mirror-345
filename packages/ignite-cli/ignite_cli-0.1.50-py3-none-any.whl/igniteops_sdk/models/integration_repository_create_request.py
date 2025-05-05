from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.integration_repository_create_request_account_type import (
    IntegrationRepositoryCreateRequestAccountType,
)
from ..models.integration_repository_create_request_provider import (
    IntegrationRepositoryCreateRequestProvider,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="IntegrationRepositoryCreateRequest")


@_attrs_define
class IntegrationRepositoryCreateRequest:
    """
    Attributes:
        account_name (str):
        account_type (IntegrationRepositoryCreateRequestAccountType):
        name (str):
        provider (IntegrationRepositoryCreateRequestProvider):
        token (str):
        api_endpoint (Union[Unset, str]):
    """

    account_name: str
    account_type: IntegrationRepositoryCreateRequestAccountType
    name: str
    provider: IntegrationRepositoryCreateRequestProvider
    token: str
    api_endpoint: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account_name = self.account_name

        account_type = self.account_type.value

        name = self.name

        provider = self.provider.value

        token = self.token

        api_endpoint = self.api_endpoint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accountName": account_name,
                "accountType": account_type,
                "name": name,
                "provider": provider,
                "token": token,
            }
        )
        if api_endpoint is not UNSET:
            field_dict["apiEndpoint"] = api_endpoint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        account_name = d.pop("accountName")

        account_type = IntegrationRepositoryCreateRequestAccountType(
            d.pop("accountType")
        )

        name = d.pop("name")

        provider = IntegrationRepositoryCreateRequestProvider(d.pop("provider"))

        token = d.pop("token")

        api_endpoint = d.pop("apiEndpoint", UNSET)

        integration_repository_create_request = cls(
            account_name=account_name,
            account_type=account_type,
            name=name,
            provider=provider,
            token=token,
            api_endpoint=api_endpoint,
        )

        integration_repository_create_request.additional_properties = d
        return integration_repository_create_request

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
