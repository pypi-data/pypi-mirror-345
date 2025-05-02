import datetime
from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.wikidata_person_type import WikidataPersonType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.wikidata_location import WikidataLocation
    from ..models.wikidata_person_descriptions import WikidataPersonDescriptions
    from ..models.wikidata_person_labels import WikidataPersonLabels


T = TypeVar("T", bound="WikidataPerson")


@_attrs_define
class WikidataPerson:
    """Wikidata person schema. Based on https://schema.org/Person

    Attributes:
        id (str): The Q Wikidata ID of the person (https://www.wikidata.org/wiki/Wikidata:Identifiers)
        type (WikidataPersonType): The type of the entity
        labels (Union[Unset, WikidataPersonLabels]): Labels of the person in different languages
        descriptions (Union[Unset, WikidataPersonDescriptions]): Descriptions of the person in different languages
        birth_date (Union[Unset, datetime.datetime]): The birth date of the person
        death_date (Union[Unset, datetime.datetime]): The death date of the person
        birth_place (Union[Unset, WikidataLocation]): Wikidata location schema. Based on https://schema.org/Place
        death_place (Union[Unset, WikidataLocation]): Wikidata location schema. Based on https://schema.org/Place
    """

    id: str
    type: WikidataPersonType
    labels: Union[Unset, "WikidataPersonLabels"] = UNSET
    descriptions: Union[Unset, "WikidataPersonDescriptions"] = UNSET
    birth_date: Union[Unset, datetime.datetime] = UNSET
    death_date: Union[Unset, datetime.datetime] = UNSET
    birth_place: Union[Unset, "WikidataLocation"] = UNSET
    death_place: Union[Unset, "WikidataLocation"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        type = self.type.value

        labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()

        descriptions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.descriptions, Unset):
            descriptions = self.descriptions.to_dict()

        birth_date: Union[Unset, str] = UNSET
        if not isinstance(self.birth_date, Unset):
            birth_date = self.birth_date.isoformat()

        death_date: Union[Unset, str] = UNSET
        if not isinstance(self.death_date, Unset):
            death_date = self.death_date.isoformat()

        birth_place: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.birth_place, Unset):
            birth_place = self.birth_place.to_dict()

        death_place: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.death_place, Unset):
            death_place = self.death_place.to_dict()

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
        if birth_date is not UNSET:
            field_dict["birthDate"] = birth_date
        if death_date is not UNSET:
            field_dict["deathDate"] = death_date
        if birth_place is not UNSET:
            field_dict["birthPlace"] = birth_place
        if death_place is not UNSET:
            field_dict["deathPlace"] = death_place

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.wikidata_location import WikidataLocation
        from ..models.wikidata_person_descriptions import WikidataPersonDescriptions
        from ..models.wikidata_person_labels import WikidataPersonLabels

        d = src_dict.copy()
        id = d.pop("id")

        type = WikidataPersonType(d.pop("type"))

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, WikidataPersonLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = WikidataPersonLabels.from_dict(_labels)

        _descriptions = d.pop("descriptions", UNSET)
        descriptions: Union[Unset, WikidataPersonDescriptions]
        if isinstance(_descriptions, Unset):
            descriptions = UNSET
        else:
            descriptions = WikidataPersonDescriptions.from_dict(_descriptions)

        _birth_date = d.pop("birthDate", UNSET)
        birth_date: Union[Unset, datetime.datetime]
        if isinstance(_birth_date, Unset):
            birth_date = UNSET
        else:
            birth_date = isoparse(_birth_date)

        _death_date = d.pop("deathDate", UNSET)
        death_date: Union[Unset, datetime.datetime]
        if isinstance(_death_date, Unset):
            death_date = UNSET
        else:
            death_date = isoparse(_death_date)

        _birth_place = d.pop("birthPlace", UNSET)
        birth_place: Union[Unset, WikidataLocation]
        if isinstance(_birth_place, Unset):
            birth_place = UNSET
        else:
            birth_place = WikidataLocation.from_dict(_birth_place)

        _death_place = d.pop("deathPlace", UNSET)
        death_place: Union[Unset, WikidataLocation]
        if isinstance(_death_place, Unset):
            death_place = UNSET
        else:
            death_place = WikidataLocation.from_dict(_death_place)

        wikidata_person = cls(
            id=id,
            type=type,
            labels=labels,
            descriptions=descriptions,
            birth_date=birth_date,
            death_date=death_date,
            birth_place=birth_place,
            death_place=death_place,
        )

        return wikidata_person
