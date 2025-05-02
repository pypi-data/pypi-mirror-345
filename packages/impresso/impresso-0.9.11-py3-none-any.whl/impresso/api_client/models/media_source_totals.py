from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="MediaSourceTotals")


@_attrs_define
class MediaSourceTotals:
    """
    Attributes:
        articles (Union[Unset, int]): The number of articles in the media source.
        issues (Union[Unset, int]): The number of issues in the media source.
        pages (Union[Unset, int]): The number of pages in the media source.
    """

    articles: Union[Unset, int] = UNSET
    issues: Union[Unset, int] = UNSET
    pages: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        articles = self.articles

        issues = self.issues

        pages = self.pages

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if articles is not UNSET:
            field_dict["articles"] = articles
        if issues is not UNSET:
            field_dict["issues"] = issues
        if pages is not UNSET:
            field_dict["pages"] = pages

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        articles = d.pop("articles", UNSET)

        issues = d.pop("issues", UNSET)

        pages = d.pop("pages", UNSET)

        media_source_totals = cls(
            articles=articles,
            issues=issues,
            pages=pages,
        )

        return media_source_totals
