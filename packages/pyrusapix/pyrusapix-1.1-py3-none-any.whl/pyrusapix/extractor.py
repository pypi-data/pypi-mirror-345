import aiohttp
import json
from typing import Optional, List, Dict, Union, Any
from .exceptions import ExtractorError  # Импортируем исключение для модуля Extractor



class Extractor:
    """Унифицированный класс для работы с JSON задачами."""

    def __init__(self):
        pass  # Можно добавить инициализацию, если потребуется

    async def extract_value_fields(
        self,
        json_data: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        return_field_codes: List[str]
    ) -> Dict[str, List[Any]]:
        """
        Извлекает и агрегирует значения полей задачи (или задач) по указанным кодам, включая вложенные структуры.
        
        Функция сама определяет, что ей передали:
        - JSON-строка (будет преобразована в объект),
        - Словарь с ключом "tasks" или "task",
        - Или даже сам объект задачи (если содержит ключ "fields"),
        - Либо список задач.

        :param json_data: JSON-строка или объект (словарь или список словарей) с задачами.
        :param return_field_codes: Список кодов полей, которые нужно извлечь.
        :return: Словарь, где ключи – коды полей, а значения – списки найденных значений.
        """
        
        # Если передана строка, пробуем преобразовать в объект
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                raise ExtractorError("Ошибка: передана некорректная JSON-строка.")

        # Определяем, что передано: список или словарь
        if isinstance(json_data, list):
            tasks = json_data  # Уже список
        elif isinstance(json_data, dict):
            if "tasks" in json_data and isinstance(json_data["tasks"], list):
                tasks = json_data["tasks"]
            elif "task" in json_data and isinstance(json_data["task"], dict):
                tasks = [json_data["task"]]  # Превращаем в список
            elif "fields" in json_data:
                tasks = [json_data]  # Это объект задачи
            else:
                raise ExtractorError("Ошибка: JSON не содержит 'tasks' или 'task', либо не выглядит как задача (нет 'fields').")
        else:
            raise ExtractorError("Ошибка: JSON должен быть строкой, словарем или списком словарей.")

        # Инициализируем словарь для хранения извлеченных данных
        aggregated_fields = {code: [] for code in return_field_codes}

        def process_field(field: Dict[str, Any]):
            """Обрабатывает одно поле задачи, извлекая значение по его коду."""
            code = field.get("code")
            field_type = field.get("type")
            value = field.get("value")

            if code in return_field_codes:
                if field_type == "catalog" and isinstance(value, dict):
                    # Используем только первый уровень "rows", если он есть
                    rows = value.get("rows", [value])
                    aggregated_fields[code].extend(rows)
                elif field_type == "multiple_choice" and isinstance(value, dict):
                    aggregated_fields[code].extend(value.get("choice_names", value))
                elif field_type == "person" and isinstance(value, dict):
                    first_name = value.get("first_name", "")
                    last_name = value.get("last_name", "")
                    aggregated_fields[code].append(f"{first_name} {last_name}".strip())
                elif field_type == "file" and isinstance(value, list):
                    aggregated_fields[code].extend([
                        {"name": f.get("name"), "size": f.get("size")}
                        for f in value if "name" in f and "size" in f
                    ])
                elif field_type == "form_link" and isinstance(value, dict):
                    aggregated_fields[code].append(value.get("task_id", value))
                elif field_type == "table" and isinstance(value, list):
                    # Обрабатываем только верхний уровень строк таблицы
                    for row in value:
                        row_data = {
                            cell.get("code"): cell.get("value")
                            for cell in row.get("cells", [])
                            if cell.get("code") in return_field_codes
                        }
                        if row_data:
                            aggregated_fields[code].append(row_data)
                else:
                    aggregated_fields[code].append(value)

            # Рекурсивно обрабатываем вложенные поля в таблицах
            if field_type == "table" and isinstance(value, list):
                for row in value:
                    for cell in row.get("cells", []):
                        process_field(cell)

        # Обрабатываем каждую задачу
        for task in tasks:
            for field in task.get("fields", []):
                process_field(field)

        # Возвращаем только те ключи, для которых найдены значения
        return {code: values for code, values in aggregated_fields.items() if values}