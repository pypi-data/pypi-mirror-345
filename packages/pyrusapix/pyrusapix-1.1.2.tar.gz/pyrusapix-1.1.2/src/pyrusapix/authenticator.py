import aiohttp
from typing import Any
from .exceptions import AuthenticationError, APIRequestError  # Импорт исключений


class Authenticator:
    def __init__(self, login: str, secret: str, base_url: str):
        """
        Инициализация аутентификатора.
        :param login: Логин пользователя.
        :param secret: Секретный ключ пользователя.
        :param base_url: Базовый URL API.
        """
        self.login = login
        self.secret = secret
        self.base_url = base_url
        self.access_token = None

    async def authenticate(self):
        """Выполняет аутентификацию и получает access_token."""
        url = f"{self.base_url}/auth"
        payload = {"login": self.login, "security_key": self.secret}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        raise AuthenticationError(f"Ошибка аутентификации: статус {response.status}")
                    
                    data = await response.json()
                    self.access_token = data.get("access_token")

                    if not self.access_token:
                        raise AuthenticationError("Ошибка аутентификации: токен отсутствует в ответе.")

        except aiohttp.ClientError as e:
            raise APIRequestError(f"Ошибка сети при аутентификации: {str(e)}")

    async def get_access_token(self) -> str:
        """
        Возвращает токен доступа.
        Если токен отсутствует, выполняется аутентификация.
        """
        if not self.access_token:
            await self.authenticate()
        return self.access_token

    async def request_with_token(self, method: str, url: str, **kwargs) -> Any:
        """
        Выполняет запрос с авторизацией, обновляет токен при необходимости.
        Обрабатывает error_code в теле ответа:
        revoked_token, expired_token, invalid_token — означает,
        что токен нужно обновить и повторить запрос.

        В остальных случаях бросает исключение с подробным описанием.
        """
        try:
            # Первый запрос
            response_data = await self._make_request(method, url, **kwargs)
            
            # Проверяем, не вернулся ли код ошибки, связанный с токеном
            if isinstance(response_data, dict):
                error_code = response_data.get("error_code")
                if error_code in ("revoked_token", "expired_token", "invalid_token"):
                    # Токен невалиден, пробуем обновить и повторить запрос
                    await self.authenticate()
                    response_data = await self._make_request(method, url, **kwargs, retry=True)

            return response_data

        except aiohttp.ClientError as e:
            raise APIRequestError(f"Ошибка сети при выполнении запроса: {str(e)}")

    async def _make_request(self, method: str, url: str, retry: bool = False, **kwargs) -> Any:
        """
        Вспомогательный метод для отправки одного запроса.
        Если retry=True, значит это повторный запрос (токен уже обновлён).
        """
        # Получаем актуальный токен
        token = await self.get_access_token()

        # Фильтруем параметры, удаляя значения None
        params = kwargs.get('params', {})
        kwargs['params'] = {k: v for k, v in params.items() if v is not None}

        # Устанавливаем заголовки
        headers = kwargs.get('headers', {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as response:
                    data = await response.json()

                    # Проверяем статус ответа
                    if response.status == 200:
                        return data
                    
                    # Если это повторный запрос, но он снова не удался — выбрасываем ошибку
                    if retry:
                        raise APIRequestError(
                            f"Запрос повторно завершился ошибкой {response.status}. "
                            f"Тело ответа: {data}"
                        )

                    # Если ошибка связана с токеном, возвращаем данные, чтобы их обработал request_with_token
                    error_code = data.get("error_code")
                    if error_code in ("revoked_token", "expired_token", "invalid_token"):
                        return data
                    
                    # Если это другая ошибка API, выбрасываем исключение
                    raise APIRequestError(
                        f"Запрос завершился ошибкой {response.status}. "
                        f"error_code: {error_code}, "
                        f"подробности: {data}"
                    )

        except aiohttp.ClientError as e:
            raise APIRequestError(f"Ошибка сети при запросе к API: {str(e)}")