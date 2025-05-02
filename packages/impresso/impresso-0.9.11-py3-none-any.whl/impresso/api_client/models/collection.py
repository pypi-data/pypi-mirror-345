import datetime
from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.collection_access_level import CollectionAccessLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="Collection")


@_attrs_define
class Collection:
    """Collection details.

    Attributes:
        uid (str): Unique identifier of the collection.
        title (Union[Unset, str]): Title of the collection.
        description (Union[Unset, str]): Description of the collection.
        access_level (Union[Unset, CollectionAccessLevel]): Access level of the collection.
        created_at (Union[Unset, datetime.datetime]): Creation date of the collection.
        updated_at (Union[Unset, datetime.datetime]): Last update date of the collection.
        total_items (Union[Unset, int]): Total number of items in the collection.
    """

    uid: str
    title: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    access_level: Union[Unset, CollectionAccessLevel] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    total_items: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        title = self.title

        description = self.description

        access_level: Union[Unset, str] = UNSET
        if not isinstance(self.access_level, Unset):
            access_level = self.access_level.value

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        total_items = self.total_items

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if access_level is not UNSET:
            field_dict["accessLevel"] = access_level
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if total_items is not UNSET:
            field_dict["totalItems"] = total_items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        uid = d.pop("uid")

        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        _access_level = d.pop("accessLevel", UNSET)
        access_level: Union[Unset, CollectionAccessLevel]
        if isinstance(_access_level, Unset):
            access_level = UNSET
        else:
            access_level = CollectionAccessLevel(_access_level)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        total_items = d.pop("totalItems", UNSET)

        collection = cls(
            uid=uid,
            title=title,
            description=description,
            access_level=access_level,
            created_at=created_at,
            updated_at=updated_at,
            total_items=total_items,
        )

        return collection
