from typing import Literal

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JOBFIT_", env_file=".env", extra="ignore")

    mode: Literal["demo", "live", "byok"] = "demo"
    llm_provider: Literal["fixtures", "nvidia", "ollama", "openrouter"] = "fixtures"
    llm_timeout_s: float = 90.0

    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = ""
    nvidia_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("JOBFIT_NVIDIA_API_KEY", "NVIDIA_API_KEY"),
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""

    database_url: str = "postgresql+psycopg://jobfit:jobfit@localhost:5432/jobfit"

    log_level: str = "WARNING"
