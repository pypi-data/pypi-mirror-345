from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="WikidataLocationCoordinates")


@_attrs_define
class WikidataLocationCoordinates:
    """
    Attributes:
        latitude (Union[Unset, float]): The latitude of the location
        longitude (Union[Unset, float]): The longitude of the location
    """

    latitude: Union[Unset, float] = UNSET
    longitude: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        latitude = self.latitude

        longitude = self.longitude

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        latitude = d.pop("latitude", UNSET)

        longitude = d.pop("longitude", UNSET)

        wikidata_location_coordinates = cls(
            latitude=latitude,
            longitude=longitude,
        )

        return wikidata_location_coordinates
