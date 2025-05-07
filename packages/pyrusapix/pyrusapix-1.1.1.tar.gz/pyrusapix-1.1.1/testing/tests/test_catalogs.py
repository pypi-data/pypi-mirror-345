import pytest
from src.pyrusapix.catalog import CatalogAPI
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
async def catalog_api(authenticated_authenticator):
    """Фикстура для PyrusAPI с аутентифицированным Authenticator."""
    return CatalogAPI(authenticator=authenticated_authenticator)

@pytest.mark.asyncio
async def test_get_all_catalogs_not_empty(catalog_api):
    """Убедиться, что get_all_catalogs возвращает непустое значение."""
    catalogs = await catalog_api.get_all_catalogs()
    assert catalogs, "Список каталогов пустой."


@pytest.mark.asyncio
async def test_get_catalog_not_empty(catalog_api):
    """Убедиться, что get_catalog возвращает непустое значение."""
    catalog_id = 250144  # Замените на реальный catalog_id
    catalog = await catalog_api.get_catalog(catalog_id=catalog_id)
    assert catalog, "Каталог пустой."

@pytest.mark.asyncio
async def test_get_catalog_with_search_value(catalog_api):
    """Убедиться, что get_catalog с search_value возвращает ожидаемый результат."""
    catalog_id = 250144  # Замените на реальный catalog_id
    search_value = "Элемент11"
    expected_result = [{'item_id': 164538815, 'values': ['10', 'Элемент11', 'Элемент12', '1080891']}]
    
    catalog = await catalog_api.get_catalog(catalog_id=catalog_id, search_value=search_value)
    assert catalog == expected_result, f"Ожидалось {expected_result}, но получено {catalog}"

@pytest.mark.asyncio
async def test_get_catalog_with_search_value_and_only_item_id(catalog_api):
    """Убедиться, что get_catalog с search_value возвращает нужный item_id."""
    catalog_id = 250144  # Замените на реальный catalog_id
    search_value = "Элемент11"
    expected_result = [164538815]
    
    catalog = await catalog_api.get_catalog(catalog_id=catalog_id, search_value=search_value, return_item_id=True)
    assert catalog == expected_result, f"Ожидалось {expected_result}, но получено {catalog}"

@pytest.mark.asyncio
async def test_catalog_as_matrix_returns_correct_matrix(catalog_api):
    """
    Убедиться, что catalog_as_matrix возвращает корректную матрицу при передаче только catalog_id.
    """
    catalog_id = 250144  # Замените на реальный catalog_id
    expected_matrix = [
        ['Ключ', 'ТЕСТ', 'Колонка2', 'КолонкаМаршрутизация'],
        ['10', 'Элемент11', 'Элемент12', '1080891'],
        ['20', 'Элемент21', 'Элемент22', '1052571']
    ]

    matrix = await catalog_api.catalog_as_matrix(catalog_id=catalog_id)
    assert matrix == expected_matrix, f"Ожидалось {expected_matrix}, но получено {matrix}"

@pytest.mark.asyncio
async def test_catalog_as_matrix_get_item_index(catalog_api):
    """
    Убедиться, что catalog_as_matrix возвращает корректные индексы при передаче get_item_index.
    """
    catalog_id = 250144  # Замените на реальный catalog_id
    indices = await catalog_api.catalog_as_matrix(catalog_id=catalog_id, get_item_index="Элемент11")
    assert indices == [[1, 1]], f"Ожидалось [[1, 1]], но получено {indices}"

@pytest.mark.asyncio
async def test_catalog_as_matrix_append_row(catalog_api):
    """
    Убедиться, что catalog_as_matrix корректно добавляет строку при передаче append_row.
    """
    catalog_id = 250144  # Замените на реальный catalog_id
    expected_result = {
        'apply': True,
        'catalog_headers': [
            {'name': 'Ключ', 'type': 'text'},
            {'name': 'ТЕСТ', 'type': 'text'},
            {'name': 'Колонка2', 'type': 'text'},
            {'name': 'КолонкаМаршрутизация', 'type': 'workflow'}
        ]
    }  # Ожидаемый результат (может отличаться в зависимости от вашего справочника)

    catalog = await catalog_api.catalog_as_matrix(
        catalog_id=catalog_id,
        append_row=[["Тест1", "Тест2", "Тест3", "1080891"]]
    )
    # Проверяем, что ключи 'apply' и 'catalog_headers' присутствуют в ответе
    assert 'apply' in catalog and 'catalog_headers' in catalog, f"Ожидалось наличие ключей 'apply' и 'catalog_headers', но получено {catalog}"
    # Проверяем значение ключа 'apply'
    assert catalog['apply'] == expected_result['apply'], f"Ожидалось значение 'apply' {expected_result['apply']}, но получено {catalog['apply']}"
    # Проверяем наличие всех заголовков в ответе
    for header in expected_result['catalog_headers']:
        assert header in catalog['catalog_headers'], f"Ожидалось наличие заголовка {header}, но получено {catalog['catalog_headers']}"

@pytest.mark.asyncio
async def test_catalog_as_matrix_delete_row(catalog_api):
    """
    Убедиться, что catalog_as_matrix корректно удаляет строку при передаче delete_row.
    """
    catalog_id = 250144  # Замените на реальный catalog_id
    expected_result = {
        'apply': True,
        'deleted': [
            {'item_id': 164824453, 'values': ['Тест1', 'Тест2', 'Тест3', '1080891']}
        ],
        'catalog_headers': [
            {'name': 'Ключ', 'type': 'text'},
            {'name': 'ТЕСТ', 'type': 'text'},
            {'name': 'Колонка2', 'type': 'text'},
            {'name': 'КолонкаМаршрутизация', 'type': 'workflow'}
        ]
    }  # Ожидаемый результат (может отличаться в зависимости от вашего справочника)

    catalog = await catalog_api.catalog_as_matrix(
        catalog_id=catalog_id,
        delete_row="Тест1"  # Передаём ключ для удаления строки
    )
    
    # Проверяем, что ключи 'apply', 'deleted' и 'catalog_headers' присутствуют в ответе
    assert 'apply' in catalog and 'deleted' in catalog and 'catalog_headers' in catalog, f"Ожидалось наличие ключей 'apply', 'deleted' и 'catalog_headers', но получено {catalog}"
    # Проверяем значение ключа 'apply'
    assert catalog['apply'] == expected_result['apply'], f"Ожидалось значение 'apply' {expected_result['apply']}, но получено {catalog['apply']}"
    # Проверяем наличие всех заголовков в ответе
    for header in expected_result['catalog_headers']:
        assert header in catalog['catalog_headers'], f"Ожидалось наличие заголовка {header}, но получено {catalog['catalog_headers']}"
    # Проверяем наличие удаленной строки в ответе
    assert catalog['deleted'] == expected_result['deleted'], f"Ожидалось значение 'deleted' {expected_result['deleted']}, но получено {catalog['deleted']}"

@pytest.mark.asyncio
async def test_catalog_as_matrix_edit_index(catalog_api):
    """
    Убедиться, что catalog_as_matrix корректно изменяет ячейку при передаче edit_index.
    """
    catalog_id = 250144  # Замените на реальный catalog_id
    expected_result = {
        'apply': True, 
        'updated': [{'item_id': 164538815, 'values': ['10', 'Тест0', 'Элемент12', '1080891']}], 
        'catalog_headers': [
            {'name': 'Ключ', 'type': 'text'}, 
            {'name': 'ТЕСТ', 'type': 'text'}, 
            {'name': 'Колонка2', 'type': 'text'}, 
            {'name': 'КолонкаМаршрутизация', 'type': 'workflow'}
        ]
    } # Ожидаемый результат (может отличаться в зависимости от вашего справочника)

    catalog = await catalog_api.catalog_as_matrix(
        catalog_id=catalog_id,
        edit_index=[[1, 1, "Тест0"]]  # Изменяем значение в ячейке [1, 1] на "Тест0"
    )
    assert 'apply' in catalog and 'updated' in catalog and 'catalog_headers' in catalog, f"Ожидалось наличие ключей 'apply', 'updated' и 'catalog_headers', но получено {catalog}"
    assert catalog['apply'] == expected_result['apply'], f"Ожидалось значение 'apply' {expected_result['apply']}, но получено {catalog['apply']}"
    assert catalog['updated'] == expected_result['updated'], f"Ожидалось значение 'updated' {expected_result['updated']}, но получено {catalog['updated']}"
    for header in expected_result['catalog_headers']:
        assert header in catalog['catalog_headers'], f"Ожидалось наличие заголовка {header}, но получено {catalog['catalog_headers']}"

    # Возвращаем значение обратно
    catalog = await catalog_api.catalog_as_matrix(
        catalog_id=catalog_id,
        edit_index=[[1, 1, "Элемент11"]]  # Изменяем значение в ячейке [1, 1] обратно на "Элемент11"
    )