import datetime
from collections.abc import Sequence as ABCSequence
from typing import (
    Any,
    Generic,
    Iterable,
    Literal,
    Sequence,
    TypeGuard,
    TypeVar,
    Union,
    cast,
)

T = TypeVar("T")


def _is_string_like_sequence(obj: Any) -> TypeGuard[Sequence[str]]:
    return (
        isinstance(obj, ABCSequence)
        and not isinstance(obj, str)
        and all(isinstance(item, str) for item in obj)
    )


class TermSet(set[T], Generic[T]):

    def __init__(self, items: Union[Sequence[T], T], *args: T):
        if _is_string_like_sequence(items):
            _items = items
        elif isinstance(items, str):
            _items = [items] + list(args)  # type:ignore
        else:
            raise ValueError(f"{items.__class__} is not supported")

        super().__init__(cast(Iterable[T], _items))
        self.inverted = False
        self.chain: list[TermSet] = []
        self._precision = "exact"

    def __invert__(self):
        new_instance = AND(list(self))
        new_instance.inverted = not self.inverted
        new_instance.chain = self.chain
        return new_instance

    def __and__(self, other: Any) -> "TermSet[T]":
        if not isinstance(other, TermSet):
            raise ValueError(f"{other.__class__} is not supported")
        klass = other.__class__
        new_instance = klass(list(other))
        new_instance.chain = other.chain + [self]
        new_instance.chain.extend(self.chain)
        new_instance.inverted = other.inverted
        return new_instance

    @property
    def op(self) -> Literal["AND", "OR"]:
        return getattr(self, "_op")

    @property
    def precision(self) -> Literal["fuzzy", "soft", "exact", "partial"]:
        return getattr(self, "_precision", "exact")


class AND(TermSet[T], Generic[T]):
    """
    Used in filters to specify that all the terms must be present in the result.

    Example:

    ```
    AND(["apple", "banana"])
    AND("apple")
    AND("apple", "banana")
    # Negate:
    ~AND("apple", "banana")
    ```

    """

    def __init__(self, items: Union[Sequence[T], T], *args: T):
        super().__init__(items, *args)
        self._op = "AND"


class OR(TermSet[T], Generic[T]):
    """
    Used in filters to specify that any of the terms must be present in the result.


    Example:

    ```
    OR(["apple", "banana"])
    OR("apple")
    OR("apple", "banana")
    # Negate:
    ~OR("apple", "banana")
    ```

    """

    def __init__(self, items: Union[Sequence[T], T], *args: T):
        super().__init__(items, *args)
        self._op = "OR"


def _as_term_set(val: TermSet[T] | str) -> TermSet[T]:
    if isinstance(val, str):
        return AND(cast(T, val))
    return val


def Fuzzy(ts: TermSet[T] | str) -> TermSet[T]:
    s = _as_term_set(ts)
    s._precision = "fuzzy"
    return s


def Soft(ts: TermSet[T] | str) -> TermSet[T]:
    s = _as_term_set(ts)
    s._precision = "soft"
    return s


def Exact(ts: TermSet[T] | str) -> TermSet[T]:
    s = _as_term_set(ts)
    s._precision = "exact"
    return s


def Partial(ts: TermSet[T] | str) -> TermSet[T]:
    s = _as_term_set(ts)
    s._precision = "partial"
    return s


class DateRange:
    """
    Date range.

    Example:

    ```
    DateRange(datetime.date(1900, 1, 1), datetime.date(2000, 12, 31))

    # Everything until 2000
    DateRange(None, datetime.date(2000, 12, 31))

    # Everything since 1900
    DateRange(datetime.date(1900, 12, 31), None)

    ```

    """

    def __init__(
        self, start: datetime.date | str | None, end: datetime.date | str | None
    ):
        self.start = datetime.date.min if start is None else DateRange._as_date(start)
        self.end = datetime.date.max if end is None else DateRange._as_date(end)
        self.inverted = False

    def __invert__(self):
        new_instance = DateRange(self.start, self.end)
        new_instance.inverted = not self.inverted
        return new_instance

    @staticmethod
    def _as_filter_value(v: "DateRange") -> str:
        return f"{v.start.isoformat()}T00:00:00Z TO {v.end.isoformat()}T00:00:00Z"

    @staticmethod
    def _as_date(value: datetime.date | str) -> datetime.date:
        if isinstance(value, str):
            return datetime.date.fromisoformat(value)
        return value


class NumericRange:
    """
    Numeric range.

    Example:

    ```
    NumericRange(1, 10)
    ```

    """

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end
        self.inverted = False

    def __invert__(self):
        new_instance = NumericRange(self.start, self.end)
        new_instance.inverted = not self.inverted
        return new_instance

    @staticmethod
    def _as_filter_value(v: "NumericRange") -> str:
        return f"{v.start} TO {v.end}"
