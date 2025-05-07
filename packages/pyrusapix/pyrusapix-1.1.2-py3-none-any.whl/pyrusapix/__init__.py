import os

class PyrusAPI:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self._forms = None
        self._tasks = None
        self._files = None
        self._catalog = None
        self._extractor = None

    @property
    def forms(self):
        if self._forms is None:
            from .forms import FormsAPI
            self._forms = FormsAPI(self.authenticator)
        return self._forms

    @property
    def tasks(self):
        if self._tasks is None:
            from .tasks import TasksAPI
            self._tasks = TasksAPI(self.authenticator)
        return self._tasks

    @property
    def files(self):
        if self._files is None:
            from .files import FilesAPI
            self._files = FilesAPI(self.authenticator)
        return self._files

    @property
    def catalog(self):
        if self._catalog is None:
            from .catalog import CatalogAPI
            self._catalog = CatalogAPI(self.authenticator)
        return self._catalog

    @property
    def extractor(self):
        if self._extractor is None:
            from .extractor import Extractor
            self._extractor = Extractor()
        return self._extractor

    def __getattr__(self, name):
        if name.startswith('get_'):
            # Если метод начинается с 'get_', пробуем делегировать его forms
            return getattr(self.forms, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# Экспортируем классы API
__all__ = ["Authenticator", "FormsAPI", "TasksAPI", "FilesAPI", "CatalogAPI", "Extractor", "PyrusAPI"]

# Импортируем Authenticator для удобства
from .authenticator import Authenticator