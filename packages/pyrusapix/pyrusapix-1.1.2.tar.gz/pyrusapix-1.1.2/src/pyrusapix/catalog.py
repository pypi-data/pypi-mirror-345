import aiohttp
from typing import List, Dict, Any, Optional, Union
from .exceptions import APIRequestError  # Импортируем нужное исключение


class CatalogAPI:
    """Класс для работы со справочниками в Pyrus API."""

    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.base_url = self.authenticator.base_url

    async def get_catalog(
        self,
        catalog_id: int,
        include_deleted: bool = False,
        search_value: Optional[str] = None,
        return_item_id: bool = False  # Новый параметр
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], List[int]]:
        """
        Получение справочника со всеми элементами или поиск элемента по значению.
        """
        url = f"{self.base_url}/catalogs/{catalog_id}"
        params = {"include_deleted": "true" if include_deleted else "false"}

        # Используем request_with_token для выполнения запроса
        catalog = await self.authenticator.request_with_token("GET", url, params=params)

        if search_value:
            async def _search_items(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
                if 'items' not in catalog:
                    raise APIRequestError("Неверный формат справочника: отсутствует ключ 'items'.")
                found_items = []
                for item in catalog['items']:
                    if search_value in item.get('values', []):
                        found_items.append(item)
                return found_items

            found_items = await _search_items(catalog)
            if return_item_id:
                try:
                    return [item['item_id'] for item in found_items]
                except KeyError as e:
                    raise APIRequestError(f"Неверный формат элемента: отсутствует 'item_id'. {str(e)}")
            else:
                return found_items
        else:
            return catalog

    async def get_all_catalogs(self) -> List[Dict[str, Any]]:
        """
        Получение всех справочников без элементов.
        """
        url = f"{self.base_url}/catalogs"
        return await self.authenticator.request_with_token("GET", url)

    async def create_catalog(
        self, name: str, catalog_headers: List[str], items: List[Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """
        Создание нового справочника.
        """
        url = f"{self.base_url}/catalogs"
        payload = {"name": name, "catalog_headers": catalog_headers, "items": items}
        return await self.authenticator.request_with_token("PUT", url, json=payload)

    async def sync_catalog(
        self,
        catalog_id: int,
        catalog_headers: List[str],
        items: List[Dict[str, List[str]]],
        apply: bool = True,
    ) -> Dict[str, Any]:
        """
        Синхронизация справочника.
        """
        url = f"{self.base_url}/catalogs/{catalog_id}"
        payload = {"apply": apply, "catalog_headers": catalog_headers, "items": items}
        return await self.authenticator.request_with_token("POST", url, json=payload)

    async def update_catalog(
        self,
        catalog_id: int,
        upsert: Optional[List[Dict[str, List[str]]]] = None,
        delete: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Изменение справочника (добавление, обновление, удаление записей).
        """
        url = f"{self.base_url}/catalogs/{catalog_id}/diff"
        payload = {"upsert": upsert, "delete": delete}
        payload = {key: value for key, value in payload.items() if value}
        return await self.authenticator.request_with_token("POST", url, json=payload)

    async def catalog_as_matrix(
        self,
        catalog_id: int,
        edit_index: Optional[List[List[Union[int, str]]]] = None,
        new_row: Optional[List[str]] = None,
        append_row: Optional[List[List[str]]] = None,
        get_item_index: Optional[str] = None,
        delete_row: Optional[str] = None,
        apply: bool = True
    ) -> Union[List[List[str]], Dict[str, Any], List[List[int]]]:
        """
        Работа со справочником как с матрицей.
        """
        catalog = await self.get_catalog(catalog_id)
        try:
            items = catalog['items']
            headers_info = catalog['catalog_headers']
        except KeyError as e:
            raise APIRequestError(f"Неверный формат справочника: отсутствует ключ {str(e)}")
        num_columns = len(headers_info)

        if append_row is not None:
            upsert_data = []
            for row in append_row:
                if len(row) != num_columns:
                    raise APIRequestError(f"Неверное количество значений для новой строки. Ожидалось {num_columns}, получено {len(row)}")
                upsert_data.append({"values": row})
            result = await self.update_catalog(catalog_id, upsert=upsert_data)
            return result

        if delete_row is not None:
            result = await self.update_catalog(catalog_id, delete=[delete_row])
            return result

        if edit_index is not None or new_row is not None:
            for row_index, col_index, new_value in edit_index or []:
                if row_index >= 0 and 0 <= col_index < len(items[0].get('values', [])):
                    if row_index == 0 and col_index == 0:
                        raise APIRequestError("Изменение ячейки [0, 0] запрещено")
                    if row_index == 0:
                        try:
                            headers_info[col_index]['name'] = new_value
                        except (IndexError, KeyError) as e:
                            raise APIRequestError(f"Ошибка изменения заголовка: {str(e)}")
                    else:
                        try:
                            items[row_index - 1]['values'][col_index] = new_value
                        except (IndexError, KeyError) as e:
                            raise APIRequestError(f"Ошибка изменения значения ячейки: {str(e)}")
                else:
                    raise APIRequestError(f"Неверные индексы: [{row_index}, {col_index}]")

            if new_row is not None:
                if len(new_row) != num_columns:
                    raise APIRequestError(f"Неверное количество значений для новой строки. Ожидалось {num_columns}, получено {len(new_row)}")
                items.append({"values": new_row})

            if apply:
                # Преобразуем catalog_headers к нужному формату
                catalog_headers = [header['name'] for header in headers_info]
                # Преобразуем items к нужному формату
                formatted_items = [{'values': item['values']} for item in items]
                result = await self.sync_catalog(
                    catalog_id=catalog_id,
                    apply=apply,
                    catalog_headers=catalog_headers,
                    items=formatted_items
                )
                return result

        if get_item_index is not None:
            indices = []
            for i, item in enumerate(items):
                for j, value in enumerate(item.get('values', [])):
                    if value == get_item_index:
                        indices.append([i + 1, j])
            return indices

        # Формируем матрицу
        matrix = []
        headers = [header['name'] for header in headers_info]
        matrix.append(headers)
        for item in items:
            matrix.append(item.get('values', []))
        return matrix