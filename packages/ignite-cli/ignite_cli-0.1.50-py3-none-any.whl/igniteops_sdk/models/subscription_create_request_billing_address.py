from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SubscriptionCreateRequestBillingAddress")


@_attrs_define
class SubscriptionCreateRequestBillingAddress:
    """
    Attributes:
        city (Union[Unset, str]):
        country (Union[Unset, str]):
        number (Union[Unset, str]):
        state (Union[Unset, str]):
        street (Union[Unset, str]):
        zipcode (Union[Unset, str]):
    """

    city: Union[Unset, str] = UNSET
    country: Union[Unset, str] = UNSET
    number: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    street: Union[Unset, str] = UNSET
    zipcode: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        city = self.city

        country = self.country

        number = self.number

        state = self.state

        street = self.street

        zipcode = self.zipcode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if city is not UNSET:
            field_dict["city"] = city
        if country is not UNSET:
            field_dict["country"] = country
        if number is not UNSET:
            field_dict["number"] = number
        if state is not UNSET:
            field_dict["state"] = state
        if street is not UNSET:
            field_dict["street"] = street
        if zipcode is not UNSET:
            field_dict["zipcode"] = zipcode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        city = d.pop("city", UNSET)

        country = d.pop("country", UNSET)

        number = d.pop("number", UNSET)

        state = d.pop("state", UNSET)

        street = d.pop("street", UNSET)

        zipcode = d.pop("zipcode", UNSET)

        subscription_create_request_billing_address = cls(
            city=city,
            country=country,
            number=number,
            state=state,
            street=street,
            zipcode=zipcode,
        )

        subscription_create_request_billing_address.additional_properties = d
        return subscription_create_request_billing_address

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
