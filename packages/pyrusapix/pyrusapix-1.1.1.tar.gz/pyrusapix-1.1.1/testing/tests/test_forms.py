import pytest
from src.pyrusapix.forms import FormsAPI
from src.pyrusapix.authenticator import Authenticator

@pytest.fixture
def authenticator():
    """
    Фикстура для создания экземпляра Authenticator с реальными переменными окружения.
    """
    import os
    login = os.getenv("PYRUS_API_LOGIN")
    secret = os.getenv("PYRUS_API_SECRET")
    base_url = os.getenv("PYRUS_API_BASE_URL")

    if not all([login, secret, base_url]):
        raise ValueError("Пожалуйста, задайте PYRUS_API_LOGIN, PYRUS_API_SECRET и PYRUS_API_BASE_URL в окружении")

    return Authenticator(login=login, secret=secret, base_url=base_url)

@pytest.fixture
async def authenticated_authenticator(authenticator):
    """Асинхронно аутентифицируем Authenticator."""
    await authenticator.authenticate()
    return authenticator

@pytest.fixture
async def forms_api(authenticated_authenticator):
    """Фикстура для PyrusAPI с аутентифицированным Authenticator."""
    return FormsAPI(authenticator=authenticated_authenticator)

@pytest.mark.asyncio
async def test_get_forms_not_empty(forms_api):
    """Убедиться, что get_forms возвращает непустое значение."""
    forms = await forms_api.get_forms()
    assert forms, "Список форм пустой."

@pytest.mark.asyncio
async def test_get_form_details_not_empty(forms_api):
    """Убедиться, что get_form_details возвращает непустое значение."""
    form_id = 1526882  # Замените на реальный form_id
    form_details = await forms_api.get_form_details(form_id=form_id)
    assert form_details, "Описание формы пустое."

@pytest.mark.asyncio
async def test_get_form_register_not_empty(forms_api):
    """Убедиться, что базовый метод get_form_register возвращает непустое значение."""
    form_id = 1526882  # Замените на реальный form_id
    register_data = await forms_api.get_form_register(form_id=form_id)
    assert register_data, "Реестр задач пустой."

@pytest.mark.asyncio
async def test_get_task_ids_by_filter(forms_api):
    """Тест получения task_id по фильтру."""
    form_id = 1526882  # Замените на реальный form_id
    filter_value = {"textField": "Текст"}  # Реальные данные фильтра

    # Запрос task_ids по фильтру
    task_ids = await forms_api.get_form_register(
        form_id=form_id, filter_value=filter_value, return_only_task_ids=True
    )

    # Проверяем, что результат содержит ожидаемый task_id
    assert task_ids == [255949790], f"Ожидалось [255949790], но получено {task_ids}"

@pytest.mark.asyncio
async def test_get_form_register_by_catalog(forms_api):
    """Тест обработки задач с каталогами."""
    form_id = 1526882  # Замените на реальный form_id
    filter_value = {"directoryField": "Элемент11"}  # Реальные данные фильтра

    # Запрос tasks по фильтру
    tasks = await forms_api.get_form_register(
        form_id=form_id, filter_value=filter_value
    )

    # Ожидаем, что хотя бы одна задача соответствует фильтру
    assert len(tasks) > 0, f"Ожидалось хотя бы одно совпадение, но задачи не найдены."
    assert any(task["id"] == 255949790 for task in tasks), (
        f"Ожидалось, что задача с id=255949790 будет найдена, "
        f"но она отсутствует в результатах: {tasks}"
    )

@pytest.mark.asyncio
async def test_get_form_register_with_return_field_codes(forms_api):
    """Тест метода get_form_register с возвратом определённых полей."""
    form_id = 1526882  # Укажите ID формы
    return_field_codes = ["directoryField"]  # Поля, которые нужно вернуть

    # Вызов метода для получения задач
    tasks = await forms_api.get_form_register(
        form_id=form_id, return_field_codes=return_field_codes
    )

    expected_result = [['10', 'Элемент11', 'Элемент12', '1080891'], ['20', 'Элемент21', 'Элемент22', '1052571']]

    assert tasks == expected_result, f"Ожидалось {expected_result}, но получено {tasks}"

@pytest.mark.asyncio
async def test_get_task_with_filter_field_and_return_value(forms_api):
    """Тест обработки задачи с фильтрацией по элементу и возвратом определённого значения."""
    form_id = 1526882  # ID формы
    filter_value = {"directoryField": "Элемент11"}  # Фильтр по элементу каталога
    return_field_codes = ["textField"]  # Поля, которые нужно вернуть

    # Вызов метода для получения задач
    tasks = await forms_api.get_form_register(
        form_id=form_id,
        filter_value=filter_value,
        return_field_codes=return_field_codes
    )

    expected_result = ['Текст']
    assert tasks == expected_result, f"Ожидалось {expected_result}, но получено {tasks}"
