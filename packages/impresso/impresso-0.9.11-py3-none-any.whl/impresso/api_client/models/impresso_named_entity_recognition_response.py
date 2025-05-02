import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.impresso_named_entity_recognition_entity import ImpressoNamedEntityRecognitionEntity


T = TypeVar("T", bound="ImpressoNamedEntityRecognitionResponse")


@_attrs_define
class ImpressoNamedEntityRecognitionResponse:
    """Response of the Impresso NER endpoint

    Attributes:
        model_id (str): ID of the model used for the named entity recognition
        text (str): Text processed for named entity recognition
        timestamp (datetime.datetime): Timestamp of when named entity recognition was performed
        entities (List['ImpressoNamedEntityRecognitionEntity']):
    """

    model_id: str
    text: str
    timestamp: datetime.datetime
    entities: List["ImpressoNamedEntityRecognitionEntity"]

    def to_dict(self) -> Dict[str, Any]:
        model_id = self.model_id

        text = self.text

        timestamp = self.timestamp.isoformat()

        entities = []
        for entities_item_data in self.entities:
            entities_item = entities_item_data.to_dict()
            entities.append(entities_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "modelId": model_id,
                "text": text,
                "timestamp": timestamp,
                "entities": entities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.impresso_named_entity_recognition_entity import ImpressoNamedEntityRecognitionEntity

        d = src_dict.copy()
        model_id = d.pop("modelId")

        text = d.pop("text")

        timestamp = isoparse(d.pop("timestamp"))

        entities = []
        _entities = d.pop("entities")
        for entities_item_data in _entities:
            entities_item = ImpressoNamedEntityRecognitionEntity.from_dict(entities_item_data)

            entities.append(entities_item)

        impresso_named_entity_recognition_response = cls(
            model_id=model_id,
            text=text,
            timestamp=timestamp,
            entities=entities,
        )

        return impresso_named_entity_recognition_response
