from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authentication_create_request_strategy import AuthenticationCreateRequestStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthenticationCreateRequest")


@_attrs_define
class AuthenticationCreateRequest:
    """Request body for the authentication endpoint

    Attributes:
        strategy (AuthenticationCreateRequestStrategy):
        email (Union[Unset, str]):
        password (Union[Unset, str]):
        access_token (Union[Unset, str]):
    """

    strategy: AuthenticationCreateRequestStrategy
    email: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    access_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        strategy = self.strategy.value

        email = self.email

        password = self.password

        access_token = self.access_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "strategy": strategy,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email
        if password is not UNSET:
            field_dict["password"] = password
        if access_token is not UNSET:
            field_dict["accessToken"] = access_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        strategy = AuthenticationCreateRequestStrategy(d.pop("strategy"))

        email = d.pop("email", UNSET)

        password = d.pop("password", UNSET)

        access_token = d.pop("accessToken", UNSET)

        authentication_create_request = cls(
            strategy=strategy,
            email=email,
            password=password,
            access_token=access_token,
        )

        authentication_create_request.additional_properties = d
        return authentication_create_request

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
