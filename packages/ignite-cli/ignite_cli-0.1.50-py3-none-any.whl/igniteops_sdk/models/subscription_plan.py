from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SubscriptionPlan")


@_attrs_define
class SubscriptionPlan:
    """
    Attributes:
        billing_frequency (Union[Unset, str]):
        description (Union[Unset, str]):
        features (Union[Unset, list[str]]):
        id (Union[Unset, str]):
        name (Union[Unset, str]):
        price (Union[Unset, float]):
        trial_period_days (Union[Unset, int]):
    """

    billing_frequency: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    features: Union[Unset, list[str]] = UNSET
    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    price: Union[Unset, float] = UNSET
    trial_period_days: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        billing_frequency = self.billing_frequency

        description = self.description

        features: Union[Unset, list[str]] = UNSET
        if not isinstance(self.features, Unset):
            features = self.features

        id = self.id

        name = self.name

        price = self.price

        trial_period_days = self.trial_period_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if billing_frequency is not UNSET:
            field_dict["billing_frequency"] = billing_frequency
        if description is not UNSET:
            field_dict["description"] = description
        if features is not UNSET:
            field_dict["features"] = features
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if price is not UNSET:
            field_dict["price"] = price
        if trial_period_days is not UNSET:
            field_dict["trial_period_days"] = trial_period_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        billing_frequency = d.pop("billing_frequency", UNSET)

        description = d.pop("description", UNSET)

        features = cast(list[str], d.pop("features", UNSET))

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        price = d.pop("price", UNSET)

        trial_period_days = d.pop("trial_period_days", UNSET)

        subscription_plan = cls(
            billing_frequency=billing_frequency,
            description=description,
            features=features,
            id=id,
            name=name,
            price=price,
            trial_period_days=trial_period_days,
        )

        subscription_plan.additional_properties = d
        return subscription_plan

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
