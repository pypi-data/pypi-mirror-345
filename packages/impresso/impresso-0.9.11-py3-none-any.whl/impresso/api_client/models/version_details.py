from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="VersionDetails")


@_attrs_define
class VersionDetails:
    """Details of the current version of the API and details of its aspects.

    Attributes:
        version (str): Version of the API.
    """

    version: str

    def to_dict(self) -> Dict[str, Any]:
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        version = d.pop("version")

        version_details = cls(
            version=version,
        )

        return version_details
