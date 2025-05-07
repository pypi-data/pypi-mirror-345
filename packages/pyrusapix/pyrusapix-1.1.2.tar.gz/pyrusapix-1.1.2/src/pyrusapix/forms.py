import aiohttp
from typing import Optional, List, Dict, Any
from .extractor import Extractor  # Импортируем Extractor
from .exceptions import APIRequestError  # Импортируем исключение для API-запросов

class FormsAPI:
    """Унифицированный класс для работы с формами."""

    def __init__(self, authenticator, extractor: Optional[Extractor] = None):
        self.authenticator = authenticator
        self.extractor = extractor if extractor else Extractor()  # Создаём Extractor, если не передан
        self.base_url = self.authenticator.base_url

    async def get_forms(self) -> List[Dict[str, Any]]:
        """Получить список доступных форм для пользователя."""
        url = f"{self.base_url}/forms"
        try:
            forms_data = await self.authenticator.request_with_token("GET", url)
            return forms_data
        except Exception as e:
            raise APIRequestError(f"Ошибка при получении списка форм: {e}")

    async def get_form_details(self, form_id: int) -> Dict[str, Any]:
        """Получить подробности формы."""
        url = f"{self.base_url}/forms/{form_id}"
        try:
            form_details = await self.authenticator.request_with_token("GET", url)
            return form_details
        except Exception as e:
            raise APIRequestError(f"Ошибка при получении деталей формы {form_id}: {e}")

    async def get_form_register(
        self,
        form_id: int,
        steps: Optional[List[int]] = None,
        task_ids: Optional[List[int]] = None,
        include_archived: Optional[bool] = None,
        field_ids: Optional[List[int]] = None,
        fld_filters: Optional[Dict[int, str]] = None,
        due_filter: Optional[str] = None,
        format: Optional[str] = None,
        delimiter: Optional[str] = None,
        encoding: Optional[str] = None,
        simple_format: Optional[bool] = None,
        modified_before: Optional[str] = None,
        modified_after: Optional[str] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        closed_before: Optional[str] = None,
        closed_after: Optional[str] = None,
        item_count: Optional[int] = None,
        filter_value: Optional[Dict[str, Any]] = None,
        return_field_codes: Optional[List[str]] = None,
        return_only_task_ids: Optional[bool] = False,
        **kwargs,
    ) -> Any:
        """
        Получить реестр формы с применёнными фильтрами.

        :return:
            - Если return_only_task_ids=True: список ID задач List[int].
            - Если return_field_codes указан: словарь агрегированных данных {код_поля: значения}.
            - Иначе: список задач List[Dict[str, Any]].
        """
        url = f"{self.base_url}/forms/{form_id}/register"

        # Собираем параметры для запроса
        params = {
            "steps": ",".join(map(str, steps)) if steps else None,
            "task_ids": ",".join(map(str, task_ids)) if task_ids else None,
            "include_archived": "y" if include_archived else None,
            "field_ids": ",".join(map(str, field_ids)) if field_ids else None,
            "due_filter": due_filter,
            "format": format,
            "delimiter": delimiter,
            "encoding": encoding,
            "simple_format": "y" if simple_format else None,
            "modified_before": modified_before,
            "modified_after": modified_after,
            "created_before": created_before,
            "created_after": created_after,
            "closed_before": closed_before,
            "closed_after": closed_after,
            "item_count": item_count,
            **kwargs,
        }
        # Убираем параметры с None
        params = {key: value for key, value in params.items() if value is not None}

        # Добавляем фильтры по полям fld{field_id}
        if fld_filters:
            for field_id, filter_value_str in fld_filters.items():
                params[f"fld{field_id}"] = filter_value_str

        try:
            register_data = await self.authenticator.request_with_token("GET", url, params=params)
        except Exception as e:
            raise APIRequestError(f"Ошибка при получении реестра формы {form_id}: {e}")

        # Извлекаем задачи из полученных данных
        tasks = register_data.get("tasks", [])

        # Если передан filter_value, фильтруем задачи через Extractor
        if filter_value:
            try:
                tasks = await self._filter_tasks_by_value(tasks, filter_value)
            except Exception as e:
                raise APIRequestError(f"Ошибка фильтрации задач: {e}")

        # Если переданы return_field_codes, агрегируем данные через Extractor
        if return_field_codes:
            try:
                return await self.extractor.extract_value_fields(tasks, return_field_codes)
            except Exception as e:
                raise APIRequestError(f"Ошибка извлечения полей задач: {e}")

        # Если указан return_only_task_ids, возвращаем только ID задач
        if return_only_task_ids:
            try:
                return [task["id"] for task in tasks if "id" in task]
            except Exception as e:
                raise APIRequestError(f"Ошибка извлечения идентификаторов задач: {e}")

        return tasks
    
    async def _filter_tasks_by_value(self, tasks: List[Dict[str, Any]], filter_value: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Выбирает только то, что соответствует этому."""
        filtered_tasks = []

        for task in tasks:
            try:
                match_found = True
                for code, value in filter_value.items():
                    # Находим поле с нужным кодом
                    field = next((f for f in task.get("fields", []) if f.get("code") == code), None)
                    if not field:
                        match_found = False
                        break

                    # Проверяем значение
                    field_value = field.get("value")
                    field_type = field.get("type")
                    if field_type == "catalog":
                        if isinstance(value, str):
                            if field_value and 'values' in field_value and value in field_value['values']:
                                continue
                            else:
                                match_found = False
                                break
                        elif isinstance(value, dict):
                            for k, v in value.items():
                                if not isinstance(field_value, dict) or field_value.get(k) != v:
                                    match_found = False
                                    break
                            if not match_found:
                                break
                        else:
                            match_found = False
                            break
                    else:
                        if isinstance(value, dict):
                            for k, v in value.items():
                                if not isinstance(field_value, dict) or field_value.get(k) != v:
                                    match_found = False
                                    break
                        else:
                            if field_value != value:
                                match_found = False
                                break

                if match_found:
                    filtered_tasks.append(task)
            except Exception:
                # При ошибке в обработке конкретной задачи просто пропускаем её
                continue

        return filtered_tasks