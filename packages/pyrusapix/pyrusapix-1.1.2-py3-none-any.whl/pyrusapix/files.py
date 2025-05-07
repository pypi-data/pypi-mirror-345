import requests
from .exceptions import APIRequestError  # Импортируем исключение для запросов к API

class FilesAPI:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.base_url = self.authenticator.base_url

    def upload_file(self, file_path):
        """Загрузка файла на сервер."""
        url = f"{self.base_url}/files/upload"
        try:
            # Получаем токен доступа (предполагается, что метод get_access_token синхронный или возвращает уже сохранённый токен)
            token = self.authenticator.get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            with open(file_path, 'rb') as file:
                files = {'file': (file_path, file, 'application/octet-stream')}
                response = requests.post(url, headers=headers, files=files)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Пытаемся обновить токен и повторить запрос
                self.authenticator.refresh_token()
                token = self.authenticator.get_access_token()
                headers = {"Authorization": f"Bearer {token}"}
                with open(file_path, 'rb') as file:
                    files = {'file': (file_path, file, 'application/octet-stream')}
                    response = requests.post(url, headers=headers, files=files)
                if response.status_code == 200:
                    return response.json()
            raise APIRequestError(f"Ошибка загрузки файла: Код {response.status_code}, {response.text}")
        except Exception as e:
            raise APIRequestError(f"Ошибка загрузки файла: {str(e)}")

    def get_file(self, file_id):
        """Получение информации о файле."""
        url = f"{self.base_url}/files/{file_id}"
        try:
            token = self.authenticator.get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                self.authenticator.refresh_token()
                token = self.authenticator.get_access_token()
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
            raise APIRequestError(f"Ошибка {response.status_code}: {response.text}")
        except Exception as e:
            raise APIRequestError(f"Ошибка получения файла: {str(e)}")
