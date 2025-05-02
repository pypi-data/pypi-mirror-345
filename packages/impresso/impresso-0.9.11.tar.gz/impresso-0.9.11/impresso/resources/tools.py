from pandas import DataFrame, json_normalize
from impresso.api_client.api.tools import perform_ner
from impresso.api_client.models.impresso_named_entity_recognition_request import (
    ImpressoNamedEntityRecognitionRequest,
)
from impresso.api_client.models.impresso_named_entity_recognition_request_method import (
    ImpressoNamedEntityRecognitionRequestMethod,
)
from impresso.api_models import ImpressoNerResponse
from impresso.data_container import DataContainer
from impresso.resources.base import Resource
from impresso.util.error import raise_for_error


class ImpressoNerSchema(ImpressoNerResponse):
    """Schema for the find entities response."""

    pass


class NerContainer(DataContainer):
    """Name entity recognition result container."""

    @property
    def df(self) -> DataFrame:
        """Return the data as a pandas dataframe."""
        data = self._data.to_dict()["entities"]
        if len(data):
            return json_normalize(self._data.to_dict()["entities"]).set_index("id")
        return DataFrame()

    @property
    def total(self) -> int:
        """Total number of results."""
        return len(self.raw.get("entities", []))

    @property
    def limit(self) -> int:
        """Page size."""
        return len(self.raw.get("entities", []))

    @property
    def offset(self) -> int:
        """Page offset."""
        return 0

    @property
    def size(self) -> int:
        """Current page size."""
        return len(self.raw.get("entities", []))


class ToolsResource(Resource):
    """Various helper tools"""

    name = "tools"

    def ner(self, text: str) -> NerContainer:
        """Named Entity Recognition

        This method is faster than `ner_nel` but does not provide any linking to external resources.

        Args:
            text (str): Text to process

        Returns:
            NerContainer: List of named entities
        """
        result = perform_ner.sync(
            client=self._api_client,
            body=ImpressoNamedEntityRecognitionRequest(
                text=text, method=ImpressoNamedEntityRecognitionRequestMethod.NER
            ),
        )
        raise_for_error(result)

        return NerContainer(
            result,
            ImpressoNerSchema,
            web_app_search_result_url=None,
        )

    def ner_nel(self, text: str) -> NerContainer:
        """Named Entity Recognition and Named Entity Linking

        This method is slower than `ner` but provides linking to external resources.

        Args:
            text (str): Text to process

        Returns:
            NerContainer: List of named entities
        """
        result = perform_ner.sync(
            client=self._api_client,
            body=ImpressoNamedEntityRecognitionRequest(
                text=text, method=ImpressoNamedEntityRecognitionRequestMethod.NER_NEL
            ),
        )
        raise_for_error(result)

        return NerContainer(
            result,
            ImpressoNerSchema,
            web_app_search_result_url=None,
        )

    def nel(self, text: str) -> NerContainer:
        """Named Entity Linking

        This method requires named entities to be enclosed in tags: [START]entity[END].

        Args:
            text (str): Text to process

        Returns:
            NerContainer: List of named entities
        """
        result = perform_ner.sync(
            client=self._api_client,
            body=ImpressoNamedEntityRecognitionRequest(
                text=text, method=ImpressoNamedEntityRecognitionRequestMethod.NEL
            ),
        )
        raise_for_error(result)

        return NerContainer(
            result,
            ImpressoNerSchema,
            web_app_search_result_url=None,
        )
