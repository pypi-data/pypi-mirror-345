from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.authentication_response_authentication import AuthenticationResponseAuthentication
    from ..models.authentication_response_user import AuthenticationResponseUser


T = TypeVar("T", bound="AuthenticationResponse")


@_attrs_define
class AuthenticationResponse:
    """Authentication Response

    Attributes:
        access_token (str):
        authentication (AuthenticationResponseAuthentication):
        user (AuthenticationResponseUser): User details
    """

    access_token: str
    authentication: "AuthenticationResponseAuthentication"
    user: "AuthenticationResponseUser"

    def to_dict(self) -> Dict[str, Any]:
        access_token = self.access_token

        authentication = self.authentication.to_dict()

        user = self.user.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accessToken": access_token,
                "authentication": authentication,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.authentication_response_authentication import AuthenticationResponseAuthentication
        from ..models.authentication_response_user import AuthenticationResponseUser

        d = src_dict.copy()
        access_token = d.pop("accessToken")

        authentication = AuthenticationResponseAuthentication.from_dict(d.pop("authentication"))

        user = AuthenticationResponseUser.from_dict(d.pop("user"))

        authentication_response = cls(
            access_token=access_token,
            authentication=authentication,
            user=user,
        )

        return authentication_response
