from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.text_reuse_passage_offset import TextReusePassageOffset


T = TypeVar("T", bound="TextReusePassage")


@_attrs_define
class TextReusePassage:
    """Represents a passage of text that was identified as a part of a text reuse cluster

    Attributes:
        uid (str): Unique ID of the text reuse passage.
        content (Union[Unset, str]): Textual content of the passage.
        content_item_id (Union[Unset, str]): ID of the content item that the text reuse passage belongs to.
        offset (Union[Unset, TextReusePassageOffset]): Start and end offsets of the passage in the content item.
    """

    uid: str
    content: Union[Unset, str] = UNSET
    content_item_id: Union[Unset, str] = UNSET
    offset: Union[Unset, "TextReusePassageOffset"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        content = self.content

        content_item_id = self.content_item_id

        offset: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.offset, Unset):
            offset = self.offset.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if content is not UNSET:
            field_dict["content"] = content
        if content_item_id is not UNSET:
            field_dict["contentItemId"] = content_item_id
        if offset is not UNSET:
            field_dict["offset"] = offset

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.text_reuse_passage_offset import TextReusePassageOffset

        d = src_dict.copy()
        uid = d.pop("uid")

        content = d.pop("content", UNSET)

        content_item_id = d.pop("contentItemId", UNSET)

        _offset = d.pop("offset", UNSET)
        offset: Union[Unset, TextReusePassageOffset]
        if isinstance(_offset, Unset):
            offset = UNSET
        else:
            offset = TextReusePassageOffset.from_dict(_offset)

        text_reuse_passage = cls(
            uid=uid,
            content=content,
            content_item_id=content_item_id,
            offset=offset,
        )

        return text_reuse_passage
