import base64
import datetime
from typing import Callable, List, TypeVar

from impresso.api_models import Q, Filter, QItem
from impresso.protobuf import query_pb2 as pb
from impresso.structures import AND, OR, TermSet


def filters_as_protobuf(filters: List[Filter]) -> str | None:
    """
    Convert a list of filters to a protobuf string.
    """
    if filters is None or len(filters) == 0:
        return None

    pb_filters = [_to_pb_filter(f) for f in filters]
    q = pb.SearchQuery(filters=pb_filters)
    return base64.b64encode(q.SerializeToString()).decode("utf-8")


def _to_pb_filter(filter: Filter) -> pb.Filter:
    """
    Convert a Filter to a protobuf Filter.
    """
    filter_dict = filter.model_dump(
        exclude_defaults=True, exclude_none=True, exclude_unset=True
    )

    pb_filter = pb.Filter()

    context = filter_dict.get("context")
    if context is not None:
        pb_filter.context = _to_pb_filter_context(context)

    op = filter_dict.get("op")
    if op is not None:
        pb_filter.op = _to_pb_filter_operator(op)

    filter_type = filter_dict.get("type")
    if filter_type is not None:
        pb_filter.type = _to_pb_filter_type(filter_type)

    precision = filter_dict.get("precision")
    if precision is not None:
        pb_filter.precision = _to_pb_filter_precision(precision)

    q = filter_dict.get("q")
    if q is not None:
        pb_filter.q.extend([q] if isinstance(q, str) else q)

    daterange = filter_dict.get("daterange")
    if daterange is not None:
        daterange_from, daterange_to = daterange.split(" TO ")
        if daterange_from is not None and daterange_to is not None:
            _from = int(datetime.datetime.fromisoformat(daterange_from).timestamp())
            _to = int(datetime.datetime.fromisoformat(daterange_to).timestamp())

            pb_filter.daterange = _to_pb_filter_daterange(_from, _to)

    return pb_filter


def _to_pb_filter_context(context: str) -> pb.FilterContext:
    v = getattr(pb.FilterContext, "CONTEXT_" + context.upper())
    if v is None:
        raise ValueError(f"Invalid filter context: {context}")
    return v


def _to_pb_filter_operator(op: str) -> pb.FilterOperator:
    v = getattr(pb.FilterOperator, "OPERATOR_" + op.upper())
    if v is None:
        raise ValueError(f"Invalid filter operator: {op}")
    return v


def _to_pb_filter_type(type: str) -> pb.FilterType:
    v = getattr(pb.FilterType, "TYPE_" + type.upper())
    if v is None:
        raise ValueError(f"Invalid filter type: {type}")
    return v


def _to_pb_filter_precision(p: str) -> pb.FilterPrecision:
    v = getattr(pb.FilterPrecision, "PRECISION_" + p.upper())
    if v is None:
        raise ValueError(f"Invalid filter precision: {p}")
    return v


def _to_pb_filter_daterange(from_: int, to: int) -> pb.DateRange:
    return pb.DateRange(to=to, **{"from": from_})


T = TypeVar("T")


def and_or_filter(
    item: T | AND[T] | OR[T],
    type: str,
    converter: Callable[[T], str] = lambda x: str(x),
) -> list[Filter]:
    if isinstance(item, TermSet):
        filter = Filter(
            type=type,
            q=list([QItem(converter(i)) for i in item]),
            op=item.op,
            context="exclude" if item.inverted else "include",
            precision=item.precision,
            daterange=None,
        )
        chain_filters = [
            Filter(
                type=type,
                q=list([QItem(converter(i)) for i in chain_item]),
                op=chain_item.op,
                context="exclude" if chain_item.inverted else "include",
                daterange=None,
            )
            for chain_item in item.chain
        ]
        return [filter] + chain_filters
    else:
        return [
            Filter(type=type, q=Q(converter(item)), daterange=None, precision="exact")
        ]
