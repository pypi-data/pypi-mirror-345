from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pat_item import PATItem


T = TypeVar("T", bound="PATList")


@_attrs_define
class PATList:
    """
    Attributes:
        pats (Union[Unset, list['PATItem']]):
    """

    pats: Union[Unset, list["PATItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pats: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.pats, Unset):
            pats = []
            for pats_item_data in self.pats:
                pats_item = pats_item_data.to_dict()
                pats.append(pats_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pats is not UNSET:
            field_dict["pats"] = pats

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pat_item import PATItem

        d = dict(src_dict)
        pats = []
        _pats = d.pop("pats", UNSET)
        for pats_item_data in _pats or []:
            pats_item = PATItem.from_dict(pats_item_data)

            pats.append(pats_item)

        pat_list = cls(
            pats=pats,
        )

        pat_list.additional_properties = d
        return pat_list

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
