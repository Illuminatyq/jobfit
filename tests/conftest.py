import pytest
import allure

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


@pytest.fixture(autouse=True)
def _allure_parent_suite(request: pytest.FixtureRequest) -> None:
    if request.node.get_closest_marker("integration"):
        allure.dynamic.parent_suite("integration")
    elif request.node.get_closest_marker("ui_landing"):
        pass  # группу ставит tests/ui_landing/conftest.py
    else:
        allure.dynamic.parent_suite("unit")
