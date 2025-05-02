from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="AuthenticationResponseUser")


@_attrs_define
class AuthenticationResponseUser:
    """User details

    Attributes:
        id (int):
        username (str):
        firstname (str):
        lastname (str):
        is_staff (bool):
        is_active (bool):
        is_superuser (bool):
        uid (str):
    """

    id: int
    username: str
    firstname: str
    lastname: str
    is_staff: bool
    is_active: bool
    is_superuser: bool
    uid: str

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        username = self.username

        firstname = self.firstname

        lastname = self.lastname

        is_staff = self.is_staff

        is_active = self.is_active

        is_superuser = self.is_superuser

        uid = self.uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "username": username,
                "firstname": firstname,
                "lastname": lastname,
                "isStaff": is_staff,
                "isActive": is_active,
                "isSuperuser": is_superuser,
                "uid": uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        username = d.pop("username")

        firstname = d.pop("firstname")

        lastname = d.pop("lastname")

        is_staff = d.pop("isStaff")

        is_active = d.pop("isActive")

        is_superuser = d.pop("isSuperuser")

        uid = d.pop("uid")

        authentication_response_user = cls(
            id=id,
            username=username,
            firstname=firstname,
            lastname=lastname,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser,
            uid=uid,
        )

        return authentication_response_user
