from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.text_reuse_cluster_time_coverage import TextReuseClusterTimeCoverage


T = TypeVar("T", bound="TextReuseCluster")


@_attrs_define
class TextReuseCluster:
    """Text reuse cluster details.

    Attributes:
        uid (str): Unique ID of the text reuse cluster.
        lexical_overlap (Union[Unset, float]): Overlap in percents between the passages in the cluster.
        cluster_size (Union[Unset, int]): Number of passages in the cluster.
        text_sample (Union[Unset, str]): Sample of a text from one of the passages in the cluster.
        time_coverage (Union[Unset, TextReuseClusterTimeCoverage]): Time coverage of the cluster.
    """

    uid: str
    lexical_overlap: Union[Unset, float] = UNSET
    cluster_size: Union[Unset, int] = UNSET
    text_sample: Union[Unset, str] = UNSET
    time_coverage: Union[Unset, "TextReuseClusterTimeCoverage"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid

        lexical_overlap = self.lexical_overlap

        cluster_size = self.cluster_size

        text_sample = self.text_sample

        time_coverage: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.time_coverage, Unset):
            time_coverage = self.time_coverage.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "uid": uid,
            }
        )
        if lexical_overlap is not UNSET:
            field_dict["lexicalOverlap"] = lexical_overlap
        if cluster_size is not UNSET:
            field_dict["clusterSize"] = cluster_size
        if text_sample is not UNSET:
            field_dict["textSample"] = text_sample
        if time_coverage is not UNSET:
            field_dict["timeCoverage"] = time_coverage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.text_reuse_cluster_time_coverage import TextReuseClusterTimeCoverage

        d = src_dict.copy()
        uid = d.pop("uid")

        lexical_overlap = d.pop("lexicalOverlap", UNSET)

        cluster_size = d.pop("clusterSize", UNSET)

        text_sample = d.pop("textSample", UNSET)

        _time_coverage = d.pop("timeCoverage", UNSET)
        time_coverage: Union[Unset, TextReuseClusterTimeCoverage]
        if isinstance(_time_coverage, Unset):
            time_coverage = UNSET
        else:
            time_coverage = TextReuseClusterTimeCoverage.from_dict(_time_coverage)

        text_reuse_cluster = cls(
            uid=uid,
            lexical_overlap=lexical_overlap,
            cluster_size=cluster_size,
            text_sample=text_sample,
            time_coverage=time_coverage,
        )

        return text_reuse_cluster
