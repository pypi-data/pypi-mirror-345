from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.wikidata_location_type import WikidataLocationType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.wikidata_location_coordinates import WikidataLocationCoordinates
    from ..models.wikidata_location_descriptions import WikidataLocationDescriptions
    from ..models.wikidata_location_labels import WikidataLocationLabels


T = TypeVar("T", bound="WikidataLocation")


@_attrs_define
class WikidataLocation:
    """Wikidata location schema. Based on https://schema.org/Place

    Attributes:
        id (str): The Q Wikidata ID of the location (https://www.wikidata.org/wiki/Wikidata:Identifiers)
        type (WikidataLocationType): The type of the entity
        labels (Union[Unset, WikidataLocationLabels]): Labels of the location in different languages
        descriptions (Union[Unset, WikidataLocationDescriptions]): Descriptions of the location in different languages
        coordinates (Union[Unset, WikidataLocationCoordinates]):
    """

    id: str
    type: WikidataLocationType
    labels: Union[Unset, "WikidataLocationLabels"] = UNSET
    descriptions: Union[Unset, "WikidataLocationDescriptions"] = UNSET
    coordinates: Union[Unset, "WikidataLocationCoordinates"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        type = self.type.value

        labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()

        descriptions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.descriptions, Unset):
            descriptions = self.descriptions.to_dict()

        coordinates: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.coordinates, Unset):
            coordinates = self.coordinates.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "type": type,
            }
        )
        if labels is not UNSET:
            field_dict["labels"] = labels
        if descriptions is not UNSET:
            field_dict["descriptions"] = descriptions
        if coordinates is not UNSET:
            field_dict["coordinates"] = coordinates

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.wikidata_location_coordinates import WikidataLocationCoordinates
        from ..models.wikidata_location_descriptions import WikidataLocationDescriptions
        from ..models.wikidata_location_labels import WikidataLocationLabels

        d = src_dict.copy()
        id = d.pop("id")

        type = WikidataLocationType(d.pop("type"))

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, WikidataLocationLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = WikidataLocationLabels.from_dict(_labels)

        _descriptions = d.pop("descriptions", UNSET)
        descriptions: Union[Unset, WikidataLocationDescriptions]
        if isinstance(_descriptions, Unset):
            descriptions = UNSET
        else:
            descriptions = WikidataLocationDescriptions.from_dict(_descriptions)

        _coordinates = d.pop("coordinates", UNSET)
        coordinates: Union[Unset, WikidataLocationCoordinates]
        if isinstance(_coordinates, Unset):
            coordinates = UNSET
        else:
            coordinates = WikidataLocationCoordinates.from_dict(_coordinates)

        wikidata_location = cls(
            id=id,
            type=type,
            labels=labels,
            descriptions=descriptions,
            coordinates=coordinates,
        )

        return wikidata_location
