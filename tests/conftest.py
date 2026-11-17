import pytest

from jobfit.adapters.taxonomy_file import load_default_taxonomy
from jobfit.domain.taxonomy import Taxonomy

VACANCY = """Требования:
Обязательно: Postman, MySQL, Docker.
Будет плюсом: Playwright, Kubernetes.
Условия: гибкий график, ДМС, ноутбук на Linux.
"""

PROFILE = """4.5 года тестирования web и backend.
API-тестирование через Postman, проверка данных в MySQL.
"""


@pytest.fixture(scope="session")
def taxonomy() -> Taxonomy:
    return load_default_taxonomy()


@pytest.fixture
def vacancy_text() -> str:
    return VACANCY


@pytest.fixture
def profile_text() -> str:
    return PROFILE
