import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.content_item_media_type import ContentItemMediaType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_mention import EntityMention
    from ..models.topic_mention import TopicMention


T = TypeVar("T", bound="ContentItem")


@_attrs_define
class ContentItem:
    """A journal/magazine content item (article, advertisement, etc.)

    Attributes:
        uid (str): The unique identifier of the content item.
        type (Union[Unset, str]): The type of the content item, as present in the OLR provided by the data provider. All
            content items are not characterised by the same set of types.
        title (Union[Unset, str]): The title of the content item.
        transcript (Union[Unset, str]): Transcript of the content item.
        locations (Union[Unset, List['EntityMention']]): Locations mentioned in the content item.
        persons (Union[Unset, List['EntityMention']]): Persions mentioned in the content item.
        topics (Union[Unset, List['TopicMention']]): Topics mentioned in the content item.
        transcript_length (Union[Unset, float]): The length of the transcript in characters.
        total_pages (Union[Unset, float]): Total number of pages the item covers.
        language_code (Union[Unset, str]): ISO 639-1 language code of the content item.
        is_on_front_page (Union[Unset, bool]): Whether the content item is on the front page of the publication.
        publication_date (Union[Unset, datetime.datetime]): The publication date of the content item.
        country_code (Union[Unset, str]): ISO 3166-1 alpha-2 country code of the content item.
        data_provider_code (Union[Unset, str]): The code of the data provider.
        media_code (Union[Unset, str]): Code of the newspaper or the other media the content item belongs to.
        media_type (Union[Unset, ContentItemMediaType]): The type of the media the content item belongs to.
    """

    uid: str
    type: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    transcript: Union[Unset, str] = UNSET
    locations: Union[Unset, List["EntityMention"]] = UNSET
    persons: Union[Unset, List["EntityMention"]] = UNSET
    topics: Union[Unset, List["TopicMention"]] = UNSET
    transcript_length: Union[Unset, float] = UNSET
    total_pages: Union[Unset, float] = UNSET
    language_code: Union[Unset, str] = UNSET
    is_on_front_page: Union[Unset, bool] = UNSET
    publication_date: Union[Unset, datetime.datetime] = UNSET
    country_code: Union[Unset, str] = UNSET
    data_provider_code: Union[Unset, str] = UNSET
    media_code: Union[Unset, str] = UNSET
    media_type: Union[Unset, ContentItemMediaType] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        type = self.type

        title = self.title

        transcript = self.transcript

        locations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = []
            for locations_item_data in self.locations:
                locations_item = locations_item_data.to_dict()
                locations.append(locations_item)

        persons: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.persons, Unset):
            persons = []
            for persons_item_data in self.persons:
                persons_item = persons_item_data.to_dict()
                persons.append(persons_item)

        topics: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.topics, Unset):
            topics = []
            for topics_item_data in self.topics:
                topics_item = topics_item_data.to_dict()
                topics.append(topics_item)

        transcript_length = self.transcript_length

        total_pages = self.total_pages

        language_code = self.language_code

        is_on_front_page = self.is_on_front_page

        publication_date: Union[Unset, str] = UNSET
        if not isinstance(self.publication_date, Unset):
            publication_date = self.publication_date.isoformat()

        country_code = self.country_code

        data_provider_code = self.data_provider_code

        media_code = self.media_code

        media_type: Union[Unset, str] = UNSET
        if not isinstance(self.media_type, Unset):
            media_type = self.media_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type
        if title is not UNSET:
            field_dict["title"] = title
        if transcript is not UNSET:
            field_dict["transcript"] = transcript
        if locations is not UNSET:
            field_dict["locations"] = locations
        if persons is not UNSET:
            field_dict["persons"] = persons
        if topics is not UNSET:
            field_dict["topics"] = topics
        if transcript_length is not UNSET:
            field_dict["transcriptLength"] = transcript_length
        if total_pages is not UNSET:
            field_dict["totalPages"] = total_pages
        if language_code is not UNSET:
            field_dict["languageCode"] = language_code
        if is_on_front_page is not UNSET:
            field_dict["isOnFrontPage"] = is_on_front_page
        if publication_date is not UNSET:
            field_dict["publicationDate"] = publication_date
        if country_code is not UNSET:
            field_dict["countryCode"] = country_code
        if data_provider_code is not UNSET:
            field_dict["dataProviderCode"] = data_provider_code
        if media_code is not UNSET:
            field_dict["mediaCode"] = media_code
        if media_type is not UNSET:
            field_dict["mediaType"] = media_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.entity_mention import EntityMention
        from ..models.topic_mention import TopicMention

        d = src_dict.copy()
        uid = d.pop("uid")

        type = d.pop("type", UNSET)

        title = d.pop("title", UNSET)

        transcript = d.pop("transcript", UNSET)

        locations = []
        _locations = d.pop("locations", UNSET)
        for locations_item_data in _locations or []:
            locations_item = EntityMention.from_dict(locations_item_data)

            locations.append(locations_item)

        persons = []
        _persons = d.pop("persons", UNSET)
        for persons_item_data in _persons or []:
            persons_item = EntityMention.from_dict(persons_item_data)

            persons.append(persons_item)

        topics = []
        _topics = d.pop("topics", UNSET)
        for topics_item_data in _topics or []:
            topics_item = TopicMention.from_dict(topics_item_data)

            topics.append(topics_item)

        transcript_length = d.pop("transcriptLength", UNSET)

        total_pages = d.pop("totalPages", UNSET)

        language_code = d.pop("languageCode", UNSET)

        is_on_front_page = d.pop("isOnFrontPage", UNSET)

        _publication_date = d.pop("publicationDate", UNSET)
        publication_date: Union[Unset, datetime.datetime]
        if isinstance(_publication_date, Unset):
            publication_date = UNSET
        else:
            publication_date = isoparse(_publication_date)

        country_code = d.pop("countryCode", UNSET)

        data_provider_code = d.pop("dataProviderCode", UNSET)

        media_code = d.pop("mediaCode", UNSET)

        _media_type = d.pop("mediaType", UNSET)
        media_type: Union[Unset, ContentItemMediaType]
        if isinstance(_media_type, Unset):
            media_type = UNSET
        else:
            media_type = ContentItemMediaType(_media_type)

        content_item = cls(
            uid=uid,
            type=type,
            title=title,
            transcript=transcript,
            locations=locations,
            persons=persons,
            topics=topics,
            transcript_length=transcript_length,
            total_pages=total_pages,
            language_code=language_code,
            is_on_front_page=is_on_front_page,
            publication_date=publication_date,
            country_code=country_code,
            data_provider_code=data_provider_code,
            media_code=media_code,
            media_type=media_type,
        )

        return content_item
