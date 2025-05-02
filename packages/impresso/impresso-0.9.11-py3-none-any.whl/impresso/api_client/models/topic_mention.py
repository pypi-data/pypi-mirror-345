from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="TopicMention")


@_attrs_define
class TopicMention:
    """Topic presence in a content item.

    Attributes:
        uid (str): Unique identifier of the topic.
        relevance (Union[Unset, float]): Relevance of the topic in the content item.
    """

    uid: str
    relevance: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        relevance = self.relevance

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if relevance is not UNSET:
            field_dict["relevance"] = relevance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        uid = d.pop("uid")

        relevance = d.pop("relevance", UNSET)

        topic_mention = cls(
            uid=uid,
            relevance=relevance,
        )

        return topic_mention
