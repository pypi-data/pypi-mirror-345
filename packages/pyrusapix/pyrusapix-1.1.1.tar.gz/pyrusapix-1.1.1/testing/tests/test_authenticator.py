import pytest
import os
from src.pyrusapix import Authenticator

# Используем pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

@pytest.mark.asyncio
async def test_load_env_variables():
    """Тест загрузки переменных окружения."""
    assert os.getenv("PYRUS_API_LOGIN"), "Переменная PYRUS_API_LOGIN не загружена"
    assert os.getenv("PYRUS_API_SECRET"), "Переменная PYRUS_API_SECRET не загружена"
    assert os.getenv("PYRUS_API_BASE_URL") == "https://api.pyrus.com/v4"

@pytest.fixture
def authenticator():
    """
    Фикстура для создания экземпляра Authenticator с реальными переменными окружения.
    """
    login = os.getenv("PYRUS_API_LOGIN")
    secret = os.getenv("PYRUS_API_SECRET")
    base_url = os.getenv("PYRUS_API_BASE_URL")

    if not all([login, secret, base_url]):
        raise ValueError("Пожалуйста, задайте PYRUS_API_LOGIN, PYRUS_API_SECRET и PYRUS_API_BASE_URL в окружении")

    return Authenticator(login=login, secret=secret, base_url=base_url)

@pytest.mark.asyncio
async def test_authenticate_success(authenticator):
    """Тест успешной аутентификации."""
    await authenticator.authenticate()  # Теперь это работает через новый механизм
    access_token = await authenticator.get_access_token()
    assert access_token is not None and len(access_token) > 0, "Токен доступа не получен."

@pytest.mark.asyncio
async def test_request_with_token_success(authenticator):
    """Тест успешного выполнения запроса с токеном."""
    url = f"{authenticator.base_url}/profile"

    response = await authenticator.request_with_token("GET", url)

    # Проверяем, что пришел JSON-объект
    assert isinstance(response, dict), "Ответ должен быть JSON-объектом"
