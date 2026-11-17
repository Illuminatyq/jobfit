import pytest
from pydantic import ValidationError

from jobfit.settings import Settings


@pytest.mark.unit
def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.mode == "demo"
    assert settings.llm_provider == "fixtures"
    assert settings.nvidia_base_url == "https://integrate.api.nvidia.com/v1"


@pytest.mark.unit
def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOBFIT_NVIDIA_MODEL", "owner/model-slug")
    monkeypatch.setenv("JOBFIT_LLM_TIMEOUT_S", "12.5")
    settings = Settings(_env_file=None)
    assert settings.nvidia_model == "owner/model-slug"
    assert settings.llm_timeout_s == 12.5


@pytest.mark.unit
def test_invalid_mode_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOBFIT_MODE", "nonsense")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.unit
def test_api_key_never_leaks_into_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "nvapi-" + "x" * 40
    monkeypatch.setenv("NVIDIA_API_KEY", secret)
    settings = Settings(_env_file=None)
    assert settings.nvidia_api_key.get_secret_value() == secret
    assert secret not in repr(settings)
    assert secret not in str(settings)
    assert secret not in settings.model_dump_json()
