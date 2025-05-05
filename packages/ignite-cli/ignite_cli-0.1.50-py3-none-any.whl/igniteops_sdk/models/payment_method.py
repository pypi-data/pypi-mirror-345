from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PaymentMethod")


@_attrs_define
class PaymentMethod:
    """
    Attributes:
        card_holder (Union[Unset, str]):
        expiry_date (Union[Unset, str]):
        id (Union[Unset, str]):
        last_four_digits (Union[Unset, str]):
        type_ (Union[Unset, str]):
    """

    card_holder: Union[Unset, str] = UNSET
    expiry_date: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    last_four_digits: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        card_holder = self.card_holder

        expiry_date = self.expiry_date

        id = self.id

        last_four_digits = self.last_four_digits

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if card_holder is not UNSET:
            field_dict["card_holder"] = card_holder
        if expiry_date is not UNSET:
            field_dict["expiry_date"] = expiry_date
        if id is not UNSET:
            field_dict["id"] = id
        if last_four_digits is not UNSET:
            field_dict["last_four_digits"] = last_four_digits
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        card_holder = d.pop("card_holder", UNSET)

        expiry_date = d.pop("expiry_date", UNSET)

        id = d.pop("id", UNSET)

        last_four_digits = d.pop("last_four_digits", UNSET)

        type_ = d.pop("type", UNSET)

        payment_method = cls(
            card_holder=card_holder,
            expiry_date=expiry_date,
            id=id,
            last_four_digits=last_four_digits,
            type_=type_,
        )

        payment_method.additional_properties = d
        return payment_method

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
