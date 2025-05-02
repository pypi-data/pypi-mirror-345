from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="Newspaper")


@_attrs_define
class Newspaper:
    """A newspaper

    Attributes:
        uid (str): The unique identifier of the newspaper.
        title (Union[Unset, str]): The title of the newspaper.
        start_year (Union[Unset, float]): The year of the first available article in the newspaper.
        end_year (Union[Unset, float]): The year of the last available article in the newspaper.
        language_codes (Union[Unset, List[str]]): ISO 639-1 codes of languages used in the newspaper.
        total_articles (Union[Unset, float]): Total number of articles in the newspaper.
        total_issues (Union[Unset, float]): Total number of issues in the newspaper.
        total_pages (Union[Unset, float]): Total number of pages in the newspaper.
    """

    uid: str
    title: Union[Unset, str] = UNSET
    start_year: Union[Unset, float] = UNSET
    end_year: Union[Unset, float] = UNSET
    language_codes: Union[Unset, List[str]] = UNSET
    total_articles: Union[Unset, float] = UNSET
    total_issues: Union[Unset, float] = UNSET
    total_pages: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        title = self.title

        start_year = self.start_year

        end_year = self.end_year

        language_codes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.language_codes, Unset):
            language_codes = self.language_codes

        total_articles = self.total_articles

        total_issues = self.total_issues

        total_pages = self.total_pages

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if start_year is not UNSET:
            field_dict["startYear"] = start_year
        if end_year is not UNSET:
            field_dict["endYear"] = end_year
        if language_codes is not UNSET:
            field_dict["languageCodes"] = language_codes
        if total_articles is not UNSET:
            field_dict["totalArticles"] = total_articles
        if total_issues is not UNSET:
            field_dict["totalIssues"] = total_issues
        if total_pages is not UNSET:
            field_dict["totalPages"] = total_pages

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        uid = d.pop("uid")

        title = d.pop("title", UNSET)

        start_year = d.pop("startYear", UNSET)

        end_year = d.pop("endYear", UNSET)

        language_codes = cast(List[str], d.pop("languageCodes", UNSET))

        total_articles = d.pop("totalArticles", UNSET)

        total_issues = d.pop("totalIssues", UNSET)

        total_pages = d.pop("totalPages", UNSET)

        newspaper = cls(
            uid=uid,
            title=title,
            start_year=start_year,
            end_year=end_year,
            language_codes=language_codes,
            total_articles=total_articles,
            total_issues=total_issues,
            total_pages=total_pages,
        )

        return newspaper
