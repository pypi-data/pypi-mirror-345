from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.entity_details_type import EntityDetailsType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.wikidata_location import WikidataLocation
    from ..models.wikidata_person import WikidataPerson


T = TypeVar("T", bound="EntityDetails")


@_attrs_define
class EntityDetails:
    """An entity: location or person.

    Attributes:
        uid (str): Unique identifier of the entity
        label (Union[Unset, str]): Entity label
        type (Union[Unset, EntityDetailsType]):
        wikidata_id (Union[Unset, str]): Wikidata identifier of the entity.
        total_mentions (Union[Unset, int]): Total number of mentions of the entity.
        total_content_items (Union[Unset, int]): Total number of content items the entity is mentioned in.
        wikidata_details (Union['WikidataLocation', 'WikidataPerson', Unset]):
    """

    uid: str
    label: Union[Unset, str] = UNSET
    type: Union[Unset, EntityDetailsType] = UNSET
    wikidata_id: Union[Unset, str] = UNSET
    total_mentions: Union[Unset, int] = UNSET
    total_content_items: Union[Unset, int] = UNSET
    wikidata_details: Union["WikidataLocation", "WikidataPerson", Unset] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        from ..models.wikidata_person import WikidataPerson

        uid = self.uid

        label = self.label

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        wikidata_id = self.wikidata_id

        total_mentions = self.total_mentions

        total_content_items = self.total_content_items

        wikidata_details: Union[Dict[str, Any], Unset]
        if isinstance(self.wikidata_details, Unset):
            wikidata_details = UNSET
        elif isinstance(self.wikidata_details, WikidataPerson):
            wikidata_details = self.wikidata_details.to_dict()
        else:
            wikidata_details = self.wikidata_details.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if type is not UNSET:
            field_dict["type"] = type
        if wikidata_id is not UNSET:
            field_dict["wikidataId"] = wikidata_id
        if total_mentions is not UNSET:
            field_dict["totalMentions"] = total_mentions
        if total_content_items is not UNSET:
            field_dict["totalContentItems"] = total_content_items
        if wikidata_details is not UNSET:
            field_dict["wikidataDetails"] = wikidata_details

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.wikidata_location import WikidataLocation
        from ..models.wikidata_person import WikidataPerson

        d = src_dict.copy()
        uid = d.pop("uid")

        label = d.pop("label", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, EntityDetailsType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = EntityDetailsType(_type)

        wikidata_id = d.pop("wikidataId", UNSET)

        total_mentions = d.pop("totalMentions", UNSET)

        total_content_items = d.pop("totalContentItems", UNSET)

        def _parse_wikidata_details(data: object) -> Union["WikidataLocation", "WikidataPerson", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                wikidata_details_type_0 = WikidataPerson.from_dict(data)

                return wikidata_details_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            wikidata_details_type_1 = WikidataLocation.from_dict(data)

            return wikidata_details_type_1

        wikidata_details = _parse_wikidata_details(d.pop("wikidataDetails", UNSET))

        entity_details = cls(
            uid=uid,
            label=label,
            type=type,
            wikidata_id=wikidata_id,
            total_mentions=total_mentions,
            total_content_items=total_content_items,
            wikidata_details=wikidata_details,
        )

        return entity_details
