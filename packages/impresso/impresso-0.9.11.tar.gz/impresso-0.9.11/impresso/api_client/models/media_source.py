import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.media_source_type import MediaSourceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.media_source_properties_item import MediaSourcePropertiesItem
    from ..models.media_source_totals import MediaSourceTotals


T = TypeVar("T", bound="MediaSource")


@_attrs_define
class MediaSource:
    """A media source is what a content item belongs to. This can be a newspaper, a TV or a radio station, etc.

    Attributes:
        uid (str): The unique identifier of the media source.
        type (MediaSourceType): The type of the media source.
        name (str): A display name of the media source.
        language_codes (List[str]): ISO 639-2 language codes this media source has content in.
        totals (MediaSourceTotals):
        published_period_years (Union[Unset, List[int]]): The range of years this media source has been published for.
            Impresso may not have data for all this period. Is not defined if there is no information.
        available_dates_range (Union[Unset, List[datetime.datetime]]): The range of dates this media source has content
            items for. This represents the earliest and the latest dates of the contet items.  Is not defined if there are
            no content items for this source.
        properties (Union[Unset, List['MediaSourcePropertiesItem']]):
    """

    uid: str
    type: MediaSourceType
    name: str
    language_codes: List[str]
    totals: "MediaSourceTotals"
    published_period_years: Union[Unset, List[int]] = UNSET
    available_dates_range: Union[Unset, List[datetime.datetime]] = UNSET
    properties: Union[Unset, List["MediaSourcePropertiesItem"]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        type = self.type.value

        name = self.name

        language_codes = self.language_codes

        totals = self.totals.to_dict()

        published_period_years: Union[Unset, List[int]] = UNSET
        if not isinstance(self.published_period_years, Unset):
            published_period_years = self.published_period_years

        available_dates_range: Union[Unset, List[str]] = UNSET
        if not isinstance(self.available_dates_range, Unset):
            available_dates_range = []
            for available_dates_range_item_data in self.available_dates_range:
                available_dates_range_item = available_dates_range_item_data.isoformat()
                available_dates_range.append(available_dates_range_item)

        properties: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data.to_dict()
                properties.append(properties_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
                "type": type,
                "name": name,
                "languageCodes": language_codes,
                "totals": totals,
            }
        )
        if published_period_years is not UNSET:
            field_dict["publishedPeriodYears"] = published_period_years
        if available_dates_range is not UNSET:
            field_dict["availableDatesRange"] = available_dates_range
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.media_source_properties_item import MediaSourcePropertiesItem
        from ..models.media_source_totals import MediaSourceTotals

        d = src_dict.copy()
        uid = d.pop("uid")

        type = MediaSourceType(d.pop("type"))

        name = d.pop("name")

        language_codes = cast(List[str], d.pop("languageCodes"))

        totals = MediaSourceTotals.from_dict(d.pop("totals"))

        published_period_years = cast(List[int], d.pop("publishedPeriodYears", UNSET))

        available_dates_range = []
        _available_dates_range = d.pop("availableDatesRange", UNSET)
        for available_dates_range_item_data in _available_dates_range or []:
            available_dates_range_item = isoparse(available_dates_range_item_data)

            available_dates_range.append(available_dates_range_item)

        properties = []
        _properties = d.pop("properties", UNSET)
        for properties_item_data in _properties or []:
            properties_item = MediaSourcePropertiesItem.from_dict(properties_item_data)

            properties.append(properties_item)

        media_source = cls(
            uid=uid,
            type=type,
            name=name,
            language_codes=language_codes,
            totals=totals,
            published_period_years=published_period_years,
            available_dates_range=available_dates_range,
            properties=properties,
        )

        return media_source
