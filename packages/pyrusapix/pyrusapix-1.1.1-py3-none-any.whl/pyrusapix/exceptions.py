# exceptions.py

class PyrusAPIError(Exception):
    """Базовое исключение для всех ошибок библиотеки."""
    pass

class AuthenticationError(PyrusAPIError):
    """Ошибка аутентификации."""
    pass

class APIRequestError(PyrusAPIError):
    """Ошибка при выполнении запроса к API."""
    pass

class ExtractorError(PyrusAPIError):
    """Ошибка при извлечении или обработке данных задач."""
    pass