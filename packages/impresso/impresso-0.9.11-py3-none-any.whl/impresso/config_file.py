import os

from pydantic import BaseModel, Field, ValidationError
import yaml

from impresso.util.token import get_jwt_status

DEFAULT_API_URL = "https://impresso-project.ch/public-api/v1"


class ImpressoApiToken(BaseModel):
    url: str
    token: str


class ImpressoPyConfigContent(BaseModel):
    """Content of the configuration file."""

    tokens: list[ImpressoApiToken] = []
    default_api_url: str = Field(
        serialization_alias="defaultApiUrl",
        default=DEFAULT_API_URL,
    )


class ImpressoPyConfig:
    """File backed configuration of the library."""

    def __init__(self, config_file="~/.impresso_py.yml") -> None:
        self._config_file = config_file
        self._config = ImpressoPyConfigContent()

        filepath = os.path.expanduser(self._config_file)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    config = yaml.safe_load(f)
                    self._config = ImpressoPyConfigContent.model_validate(config)
                except yaml.YAMLError as exc:
                    print("Error loading config file:", exc)
                except ValidationError as exc:
                    print("Error validating config file:", exc)

    @property
    def default_api_url(self) -> str:
        return self._config.default_api_url

    def get_token(self, url: str | None) -> str | None:
        """
        Return the token for the given API URL.
        Use the default API URL if no URL is provided.
        """
        the_url = url or self._config.default_api_url
        token = next((t.token for t in self._config.tokens if t.url == the_url), None)

        if token is None:
            return None
        token_status, _ = get_jwt_status(token)
        if token_status == "valid":
            return token

        return None

    def set_token(self, token: str, url: str | None) -> None:
        """
        Return the token for the given API URL.
        Use the default API URL if no URL is provided.
        """
        the_url = url or self._config.default_api_url
        token_container = next(
            (t for t in self._config.tokens if t.url == the_url), None
        )

        if token_container is None:
            self._config.tokens.append(ImpressoApiToken(url=the_url, token=token))
        else:
            token_container.token = token

        self._write_config()

    def _write_config(self) -> None:
        """Write the configuration to the file."""
        filepath = os.path.expanduser(self._config_file)
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(self._config.model_dump(exclude_none=True), f)
