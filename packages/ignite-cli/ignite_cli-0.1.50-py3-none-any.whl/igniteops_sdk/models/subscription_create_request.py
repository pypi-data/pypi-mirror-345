from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.subscription_create_request_billing_address import (
        SubscriptionCreateRequestBillingAddress,
    )


T = TypeVar("T", bound="SubscriptionCreateRequest")


@_attrs_define
class SubscriptionCreateRequest:
    """
    Attributes:
        billing_address (SubscriptionCreateRequestBillingAddress):
        card_token_id (str):
        cardholder_name (str):
        payer_email (str):
        plan_id (str):
    """

    billing_address: "SubscriptionCreateRequestBillingAddress"
    card_token_id: str
    cardholder_name: str
    payer_email: str
    plan_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        billing_address = self.billing_address.to_dict()

        card_token_id = self.card_token_id

        cardholder_name = self.cardholder_name

        payer_email = self.payer_email

        plan_id = self.plan_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "billing_address": billing_address,
                "cardTokenId": card_token_id,
                "cardholderName": cardholder_name,
                "payer_email": payer_email,
                "planId": plan_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.subscription_create_request_billing_address import (
            SubscriptionCreateRequestBillingAddress,
        )

        d = dict(src_dict)
        billing_address = SubscriptionCreateRequestBillingAddress.from_dict(
            d.pop("billing_address")
        )

        card_token_id = d.pop("cardTokenId")

        cardholder_name = d.pop("cardholderName")

        payer_email = d.pop("payer_email")

        plan_id = d.pop("planId")

        subscription_create_request = cls(
            billing_address=billing_address,
            card_token_id=card_token_id,
            cardholder_name=cardholder_name,
            payer_email=payer_email,
            plan_id=plan_id,
        )

        subscription_create_request.additional_properties = d
        return subscription_create_request

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
