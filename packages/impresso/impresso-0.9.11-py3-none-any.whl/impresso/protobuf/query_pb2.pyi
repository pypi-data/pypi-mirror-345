from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilterContext(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTEXT_UNSPECIFIED: _ClassVar[FilterContext]
    CONTEXT_INCLUDE: _ClassVar[FilterContext]
    CONTEXT_EXCLUDE: _ClassVar[FilterContext]

class FilterOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATOR_UNSPECIFIED: _ClassVar[FilterOperator]
    OPERATOR_AND: _ClassVar[FilterOperator]
    OPERATOR_OR: _ClassVar[FilterOperator]

class FilterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TYPE_UNSPECIFIED: _ClassVar[FilterType]
    TYPE_UID: _ClassVar[FilterType]
    TYPE_HAS_TEXT_CONTENTS: _ClassVar[FilterType]
    TYPE_TITLE: _ClassVar[FilterType]
    TYPE_IS_FRONT: _ClassVar[FilterType]
    TYPE_PAGE: _ClassVar[FilterType]
    TYPE_ISSUE: _ClassVar[FilterType]
    TYPE_STRING: _ClassVar[FilterType]
    TYPE_ENTITY: _ClassVar[FilterType]
    TYPE_NEWSPAPER: _ClassVar[FilterType]
    TYPE_DATERANGE: _ClassVar[FilterType]
    TYPE_YEAR: _ClassVar[FilterType]
    TYPE_LANGUAGE: _ClassVar[FilterType]
    TYPE_TYPE: _ClassVar[FilterType]
    TYPE_REGEX: _ClassVar[FilterType]
    TYPE_MENTION: _ClassVar[FilterType]
    TYPE_PERSON: _ClassVar[FilterType]
    TYPE_LOCATION: _ClassVar[FilterType]
    TYPE_TOPIC: _ClassVar[FilterType]
    TYPE_COLLECTION: _ClassVar[FilterType]
    TYPE_OCR_QUALITY: _ClassVar[FilterType]
    TYPE_CONTENT_LENGTH: _ClassVar[FilterType]
    TYPE_COUNTRY: _ClassVar[FilterType]
    TYPE_ACCESS_RIGHT: _ClassVar[FilterType]
    TYPE_PARTNER: _ClassVar[FilterType]
    TYPE_MONTH: _ClassVar[FilterType]
    TYPE_TEXT_REUSE_CLUSTER_SIZE: _ClassVar[FilterType]
    TYPE_TEXT_REUSE_CLUSTER_LEXICAL_OVERLAP: _ClassVar[FilterType]
    TYPE_TEXT_REUSE_CLUSTER_DAY_DELTA: _ClassVar[FilterType]
    TYPE_TEXT_REUSE_CLUSTER: _ClassVar[FilterType]
    TYPE_MENTION_FUNCTION: _ClassVar[FilterType]
    TYPE_NAG: _ClassVar[FilterType]
    TYPE_WIKIDATA_ID: _ClassVar[FilterType]

class FilterPrecision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRECISION_UNSPECIFIED: _ClassVar[FilterPrecision]
    PRECISION_EXACT: _ClassVar[FilterPrecision]
    PRECISION_PARTIAL: _ClassVar[FilterPrecision]
    PRECISION_FUZZY: _ClassVar[FilterPrecision]
    PRECISION_SOFT: _ClassVar[FilterPrecision]

class GroupValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GROUPVALUE_UNSPECIFIED: _ClassVar[GroupValue]
    GROUPVALUE_ARTICLES: _ClassVar[GroupValue]
CONTEXT_UNSPECIFIED: FilterContext
CONTEXT_INCLUDE: FilterContext
CONTEXT_EXCLUDE: FilterContext
OPERATOR_UNSPECIFIED: FilterOperator
OPERATOR_AND: FilterOperator
OPERATOR_OR: FilterOperator
TYPE_UNSPECIFIED: FilterType
TYPE_UID: FilterType
TYPE_HAS_TEXT_CONTENTS: FilterType
TYPE_TITLE: FilterType
TYPE_IS_FRONT: FilterType
TYPE_PAGE: FilterType
TYPE_ISSUE: FilterType
TYPE_STRING: FilterType
TYPE_ENTITY: FilterType
TYPE_NEWSPAPER: FilterType
TYPE_DATERANGE: FilterType
TYPE_YEAR: FilterType
TYPE_LANGUAGE: FilterType
TYPE_TYPE: FilterType
TYPE_REGEX: FilterType
TYPE_MENTION: FilterType
TYPE_PERSON: FilterType
TYPE_LOCATION: FilterType
TYPE_TOPIC: FilterType
TYPE_COLLECTION: FilterType
TYPE_OCR_QUALITY: FilterType
TYPE_CONTENT_LENGTH: FilterType
TYPE_COUNTRY: FilterType
TYPE_ACCESS_RIGHT: FilterType
TYPE_PARTNER: FilterType
TYPE_MONTH: FilterType
TYPE_TEXT_REUSE_CLUSTER_SIZE: FilterType
TYPE_TEXT_REUSE_CLUSTER_LEXICAL_OVERLAP: FilterType
TYPE_TEXT_REUSE_CLUSTER_DAY_DELTA: FilterType
TYPE_TEXT_REUSE_CLUSTER: FilterType
TYPE_MENTION_FUNCTION: FilterType
TYPE_NAG: FilterType
TYPE_WIKIDATA_ID: FilterType
PRECISION_UNSPECIFIED: FilterPrecision
PRECISION_EXACT: FilterPrecision
PRECISION_PARTIAL: FilterPrecision
PRECISION_FUZZY: FilterPrecision
PRECISION_SOFT: FilterPrecision
GROUPVALUE_UNSPECIFIED: GroupValue
GROUPVALUE_ARTICLES: GroupValue

class DateRange(_message.Message):
    __slots__ = ("to",)
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    to: int
    def __init__(self, to: _Optional[int] = ..., **kwargs) -> None: ...

class Filter(_message.Message):
    __slots__ = ("context", "op", "type", "precision", "q", "daterange", "uids")
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    OP_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    DATERANGE_FIELD_NUMBER: _ClassVar[int]
    UIDS_FIELD_NUMBER: _ClassVar[int]
    context: FilterContext
    op: FilterOperator
    type: FilterType
    precision: FilterPrecision
    q: _containers.RepeatedScalarFieldContainer[str]
    daterange: DateRange
    uids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, context: _Optional[_Union[FilterContext, str]] = ..., op: _Optional[_Union[FilterOperator, str]] = ..., type: _Optional[_Union[FilterType, str]] = ..., precision: _Optional[_Union[FilterPrecision, str]] = ..., q: _Optional[_Iterable[str]] = ..., daterange: _Optional[_Union[DateRange, _Mapping]] = ..., uids: _Optional[_Iterable[str]] = ...) -> None: ...

class SearchQuery(_message.Message):
    __slots__ = ("filters", "group_by")
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[Filter]
    group_by: GroupValue
    def __init__(self, filters: _Optional[_Iterable[_Union[Filter, _Mapping]]] = ..., group_by: _Optional[_Union[GroupValue, str]] = ...) -> None: ...

class CollectionRecommenderParameter(_message.Message):
    __slots__ = ("key", "string_value", "number_value", "bool_value")
    class RecommenderParameterId(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ID_UNSPECIFIED: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
        ID_COUNT_TYPE: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
        ID_MIN_OCCURRENCES: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
        ID_NUMBER_TO_KEEP: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
        ID_REMOVE_FULLY_MENTIONED: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
        ID_NORMALIZE_MAX_SCORE: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
        ID_MARGIN: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
        ID_SCALING_FACTOR: _ClassVar[CollectionRecommenderParameter.RecommenderParameterId]
    ID_UNSPECIFIED: CollectionRecommenderParameter.RecommenderParameterId
    ID_COUNT_TYPE: CollectionRecommenderParameter.RecommenderParameterId
    ID_MIN_OCCURRENCES: CollectionRecommenderParameter.RecommenderParameterId
    ID_NUMBER_TO_KEEP: CollectionRecommenderParameter.RecommenderParameterId
    ID_REMOVE_FULLY_MENTIONED: CollectionRecommenderParameter.RecommenderParameterId
    ID_NORMALIZE_MAX_SCORE: CollectionRecommenderParameter.RecommenderParameterId
    ID_MARGIN: CollectionRecommenderParameter.RecommenderParameterId
    ID_SCALING_FACTOR: CollectionRecommenderParameter.RecommenderParameterId
    KEY_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    key: CollectionRecommenderParameter.RecommenderParameterId
    string_value: str
    number_value: int
    bool_value: bool
    def __init__(self, key: _Optional[_Union[CollectionRecommenderParameter.RecommenderParameterId, str]] = ..., string_value: _Optional[str] = ..., number_value: _Optional[int] = ..., bool_value: bool = ...) -> None: ...

class CollectionRecommender(_message.Message):
    __slots__ = ("type", "weight", "parameters", "enabled")
    class RecommenderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[CollectionRecommender.RecommenderType]
        TYPE_TIME_RANGE: _ClassVar[CollectionRecommender.RecommenderType]
        TYPE_ENTITIES: _ClassVar[CollectionRecommender.RecommenderType]
        TYPE_TOPICS: _ClassVar[CollectionRecommender.RecommenderType]
        TYPE_TEXT_REUSE_CLUSTERS: _ClassVar[CollectionRecommender.RecommenderType]
    TYPE_UNSPECIFIED: CollectionRecommender.RecommenderType
    TYPE_TIME_RANGE: CollectionRecommender.RecommenderType
    TYPE_ENTITIES: CollectionRecommender.RecommenderType
    TYPE_TOPICS: CollectionRecommender.RecommenderType
    TYPE_TEXT_REUSE_CLUSTERS: CollectionRecommender.RecommenderType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    type: CollectionRecommender.RecommenderType
    weight: int
    parameters: _containers.RepeatedCompositeFieldContainer[CollectionRecommenderParameter]
    enabled: bool
    def __init__(self, type: _Optional[_Union[CollectionRecommender.RecommenderType, str]] = ..., weight: _Optional[int] = ..., parameters: _Optional[_Iterable[_Union[CollectionRecommenderParameter, _Mapping]]] = ..., enabled: bool = ...) -> None: ...

class CollectionRecommendersSettings(_message.Message):
    __slots__ = ("recommenders",)
    RECOMMENDERS_FIELD_NUMBER: _ClassVar[int]
    recommenders: _containers.RepeatedCompositeFieldContainer[CollectionRecommender]
    def __init__(self, recommenders: _Optional[_Iterable[_Union[CollectionRecommender, _Mapping]]] = ...) -> None: ...
