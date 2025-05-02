from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authentication_response_authentication_payload import AuthenticationResponseAuthenticationPayload


T = TypeVar("T", bound="AuthenticationResponseAuthentication")


@_attrs_define
class AuthenticationResponseAuthentication:
    """
    Attributes:
        strategy (Union[Unset, str]):
        payload (Union[Unset, AuthenticationResponseAuthenticationPayload]):
    """

    strategy: Union[Unset, str] = UNSET
    payload: Union[Unset, "AuthenticationResponseAuthenticationPayload"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        strategy = self.strategy

        payload: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.payload, Unset):
            payload = self.payload.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if strategy is not UNSET:
            field_dict["strategy"] = strategy
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.authentication_response_authentication_payload import AuthenticationResponseAuthenticationPayload

        d = src_dict.copy()
        strategy = d.pop("strategy", UNSET)

        _payload = d.pop("payload", UNSET)
        payload: Union[Unset, AuthenticationResponseAuthenticationPayload]
        if isinstance(_payload, Unset):
            payload = UNSET
        else:
            payload = AuthenticationResponseAuthenticationPayload.from_dict(_payload)

        authentication_response_authentication = cls(
            strategy=strategy,
            payload=payload,
        )

        authentication_response_authentication.additional_properties = d
        return authentication_response_authentication

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
