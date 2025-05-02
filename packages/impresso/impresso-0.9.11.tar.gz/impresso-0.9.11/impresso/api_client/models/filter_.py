from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..models.filter_context import FilterContext
from ..models.filter_op import FilterOp
from ..models.filter_precision import FilterPrecision
from ..types import UNSET, Unset

T = TypeVar("T", bound="Filter")


@_attrs_define
class Filter:
    """A single filter criteria

    Attributes:
        type (str): Possible values are in 'search.validators:eachFilterValidator.type.choices'
        context (Union[Unset, FilterContext]):  Default: FilterContext.INCLUDE.
        op (Union[Unset, FilterOp]):  Default: FilterOp.OR.
        precision (Union[Unset, FilterPrecision]):  Default: FilterPrecision.EXACT.
        q (Union[List[str], Unset, str]):
        daterange (Union[Unset, str]):
        uids (Union[Unset, str]):
        uid (Union[Unset, str]):
    """

    type: str
    context: Union[Unset, FilterContext] = FilterContext.INCLUDE
    op: Union[Unset, FilterOp] = FilterOp.OR
    precision: Union[Unset, FilterPrecision] = FilterPrecision.EXACT
    q: Union[List[str], Unset, str] = UNSET
    daterange: Union[Unset, str] = UNSET
    uids: Union[Unset, str] = UNSET
    uid: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        type = self.type

        context: Union[Unset, str] = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.value

        op: Union[Unset, str] = UNSET
        if not isinstance(self.op, Unset):
            op = self.op.value

        precision: Union[Unset, str] = UNSET
        if not isinstance(self.precision, Unset):
            precision = self.precision.value

        q: Union[List[str], Unset, str]
        if isinstance(self.q, Unset):
            q = UNSET
        elif isinstance(self.q, list):
            q = self.q

        else:
            q = self.q

        daterange = self.daterange

        uids = self.uids

        uid = self.uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
            }
        )
        if context is not UNSET:
            field_dict["context"] = context
        if op is not UNSET:
            field_dict["op"] = op
        if precision is not UNSET:
            field_dict["precision"] = precision
        if q is not UNSET:
            field_dict["q"] = q
        if daterange is not UNSET:
            field_dict["daterange"] = daterange
        if uids is not UNSET:
            field_dict["uids"] = uids
        if uid is not UNSET:
            field_dict["uid"] = uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type")

        _context = d.pop("context", UNSET)
        context: Union[Unset, FilterContext]
        if isinstance(_context, Unset):
            context = UNSET
        else:
            context = FilterContext(_context)

        _op = d.pop("op", UNSET)
        op: Union[Unset, FilterOp]
        if isinstance(_op, Unset):
            op = UNSET
        else:
            op = FilterOp(_op)

        _precision = d.pop("precision", UNSET)
        precision: Union[Unset, FilterPrecision]
        if isinstance(_precision, Unset):
            precision = UNSET
        else:
            precision = FilterPrecision(_precision)

        def _parse_q(data: object) -> Union[List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                q_type_1 = cast(List[str], data)

                return q_type_1
            except:  # noqa: E722
                pass
            return cast(Union[List[str], Unset, str], data)

        q = _parse_q(d.pop("q", UNSET))

        daterange = d.pop("daterange", UNSET)

        uids = d.pop("uids", UNSET)

        uid = d.pop("uid", UNSET)

        filter_ = cls(
            type=type,
            context=context,
            op=op,
            precision=precision,
            q=q,
            daterange=daterange,
            uids=uids,
            uid=uid,
        )

        return filter_
