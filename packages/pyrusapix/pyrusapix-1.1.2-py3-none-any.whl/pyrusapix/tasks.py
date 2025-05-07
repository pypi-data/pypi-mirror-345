import aiohttp
from .extractor import Extractor  # Импортируем Extractor
from typing import List, Dict, Any, Optional, Union
from .exceptions import APIRequestError  # Импортируем исключение для API-запросов

class TasksAPI:
    """Класс для работы с задачами по форме в Pyrus API."""

    def __init__(self, authenticator, extractor: Optional[Extractor] = None):
        self.authenticator = authenticator
        self.extractor = extractor if extractor else Extractor()  # Создаём Extractor, если не передан
        self.base_url = self.authenticator.base_url

    async def get_task(
        self,
        task_id: int,
        return_field_codes: Optional[List[str]] = None,
        return_fields_id: Optional[List[int]] = None
    ) -> Union[Dict[str, Any], Dict[str, str]]:
        """
        Получение задачи по идентификатору.
        """
        url = f"{self.base_url}/tasks/{task_id}"
        try:
            task_details = await self.authenticator.request_with_token("GET", url)
        except Exception as e:
            raise APIRequestError(f"Ошибка при получении задачи {task_id}: {e}")
        
        try:
            if return_field_codes and return_fields_id:
                aggregated_by_codes = await self.extractor.extract_value_fields(task_details, return_field_codes)
                aggregated_by_ids = await self.extractor._search_fields_by_codes_with_ids(task_details, return_fields_id)
                aggregated_fields = {**aggregated_by_codes, **aggregated_by_ids}
                return aggregated_fields
            elif return_field_codes:
                return await self.extractor.extract_value_fields(task_details, return_field_codes)
            elif return_fields_id:
                return await self.extractor._search_fields_by_codes_with_ids(task_details, return_fields_id)
            else:
                return task_details
        except Exception as e:
            raise APIRequestError(f"Ошибка при обработке данных задачи {task_id}: {e}")
    
    async def create_task(
        self,
        form_id: Optional[int] = None,
        fields: Optional[List[Dict[str, Any]]] = None,
        due_date: Optional[str] = None,
        due: Optional[str] = None,
        duration: Optional[int] = None,
        subscribers: Optional[List[Union[int, str]]] = None,
        parent_task_id: Optional[int] = None,
        list_ids: Optional[List[int]] = None,
        attachments: Optional[List[Union[str, Dict[str, Any]]]] = None,
        scheduled_date: Optional[str] = None,
        scheduled_datetime_utc: Optional[str] = None,
        approvals: Optional[List[List[Dict[str, Any]]]] = None,
        fill_defaults: bool = False,
    ) -> Dict[str, Any]:
        """
        Создание задачи по форме.
        """
        url = f"{self.base_url}/tasks"
        payload = {
            "form_id": form_id,
            "fields": fields,
            "due_date": due_date,
            "due": due,
            "duration": duration,
            "subscribers": subscribers,
            "parent_task_id": parent_task_id,
            "list_ids": list_ids,
            "attachments": attachments,
            "scheduled_date": scheduled_date,
            "scheduled_datetime_utc": scheduled_datetime_utc,
            "approvals": approvals,
            "fill_defaults": fill_defaults,
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        try:
            return await self.authenticator.request_with_token("POST", url, json=payload)
        except Exception as e:
            raise APIRequestError(f"Ошибка при создании задачи: {e}")

    async def update_task_comment(
        self,
        task_id: int,
        text: Optional[str] = None,
        formatted_text: Optional[str] = None,
        edit_comment_id: Optional[int] = None,
        due_date: Optional[str] = None,
        due: Optional[str] = None,
        duration: Optional[int] = None,
        cancel_due: bool = False,
        action: Optional[str] = None,
        approval_choice: Optional[str] = None,
        reassign_to: Optional[Union[int, str]] = None,
        field_updates: Optional[List[Dict[str, Any]]] = None,
        field_updates_by_codes: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Union[str, Dict[str, Any]]]] = None,
        added_list_ids: Optional[List[int]] = None,
        removed_list_ids: Optional[List[int]] = None,
        scheduled_date: Optional[str] = None,
        scheduled_datetime_utc: Optional[str] = None,
        cancel_schedule: bool = False,
        channel: Optional[Dict[str, Any]] = None,
        spent_minutes: Optional[int] = None,
        skip_satisfaction: bool = False,
        skip_notification: bool = False,
    ) -> Dict[str, Any]:
        """
        Добавление комментария в задачу.
        """
        url = f"{self.base_url}/tasks/{task_id}/comments"
        processed_field_updates_by_codes = None
        if field_updates_by_codes:
            try:
                processed_field_updates_by_codes = await self._field_updates_by_codes(task_id, field_updates_by_codes)
            except Exception as e:
                raise APIRequestError(f"Ошибка при обработке обновлений полей по кодам: {e}")

        payload = {
            "text": text,
            "formatted_text": formatted_text,
            "edit_comment_id": edit_comment_id,
            "due_date": due_date,
            "due": due,
            "duration": duration, 
            "cancel_due": cancel_due if cancel_due else None,
            "action": action,
            "approval_choice": approval_choice,
            "reassign_to": reassign_to,
            "field_updates": field_updates if processed_field_updates_by_codes is None else processed_field_updates_by_codes,
            "attachments": attachments,
            "added_list_ids": added_list_ids,
            "removed_list_ids": removed_list_ids,
            "scheduled_date": scheduled_date,
            "scheduled_datetime_utc": scheduled_datetime_utc,
            "cancel_schedule": cancel_schedule if cancel_schedule else None,
            "channel": channel,
            "spent_minutes": spent_minutes,
            "skip_satisfaction": skip_satisfaction,
            "skip_notification": skip_notification,
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        try:
            return await self.authenticator.request_with_token("POST", url, json=payload)
        except Exception as e:
            raise APIRequestError(f"Ошибка при обновлении комментария задачи {task_id}: {e}")

    async def _field_updates_by_codes(
        self, task_id: int, field_updates_by_codes: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Преобразует обновления полей по кодам в формат, необходимый API.
        """
        try:
            print(f"Запускаем _field_updates_by_codes для task_id={task_id}")
            print(f"Получены коды полей: {field_updates_by_codes}")
            codes = list(field_updates_by_codes.keys())
            if not codes:
                print("⚠️ Список кодов пуст, ничего не обновляем")
                return []
            # Получаем информацию о полях задачи
            field_info = await self.get_task(task_id, return_fields_id=codes)
            print(f"📥 Получены идентификаторы и типы полей: {field_info}")
            if not isinstance(field_info, dict):
                raise APIRequestError("Ожидался словарь с идентификаторами и типами полей.")
            code_to_id_map = {
                code: (int(field_id), field_type)
                for (field_id, field_type), code in zip(field_info.items(), codes)
            }
            print(f"✅ Сопоставление кодов и ID: {code_to_id_map}")
            field_updates = []
            for code, value in field_updates_by_codes.items():
                if code not in code_to_id_map:
                    print(f"⚠️ Код {code} не найден в полученных данных, пропускаем")
                    continue
                field_id = code_to_id_map[code]
                field_updates.append({"id": field_id, "value": value})
            field_updates.reverse()
            return field_updates
        except Exception as e:
            raise APIRequestError(f"Ошибка в _field_updates_by_codes: {e}")

    async def _search_fields_by_codes_with_ids(
        self, task_details: Dict[str, Any], field_codes: List[str]
    ) -> Dict[str, str]:
        """Ищет поля по кодам и возвращает {id: type}"""
        target_codes = set(field_codes)
        result = {}

        def search_fields(fields):
            for field in fields:
                code = field.get("code")
                # Если код в списке искомых
                if code in target_codes:
                    try:
                        result[str(field["id"])] = field.get("type", "unknown")
                    except KeyError as e:
                        raise APIRequestError(f"Ошибка поиска поля: отсутствует 'id'. {str(e)}")
                
                # Рекурсивный поиск в таблицах
                if field.get("type") == "table":
                    for row in field.get("value", []):
                        search_fields(row.get("cells", []))

        # Проверяем, содержится ли задача в объекте или передана напрямую
        task_data = task_details.get("task", task_details)
        search_fields(task_data.get("fields", []))
        
        # Сохраняем порядок из field_codes и преобразуем ID в строки
        ordered_result = {}
        for code in field_codes:
            for field in task_data.get("fields", []):
                if field.get("code") == code:
                    try:
                        ordered_result[str(field["id"])] = field.get("type", "unknown")
                        break
                    except KeyError as e:
                        raise APIRequestError(f"Ошибка обработки поля: отсутствует 'id'. {str(e)}")
        
        return ordered_result

    async def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Удаление задачи.
        """
        url = f"{self.base_url}/tasks/{task_id}"
        try:
            return await self.authenticator.request_with_token("POST", url)
        except Exception as e:
            raise APIRequestError(f"Ошибка при удалении задачи {task_id}: {e}")