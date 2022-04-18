import uuid

from framework.persistence import Persistence, PersistenceSerializable
from framework.request import Request
from framework.response import Response

from element_edit import ElementEditView
import settings


class Category(PersistenceSerializable):
    id: uuid.UUID
    name: str

    def __init__(self, id: uuid.UUID = None, name: str = None):
        self.id = id if id else uuid.uuid4()
        self.name = name

    # Register Category's Persistence storage
    @staticmethod
    def register() -> bool:
        return Persistence.register_class(Category, settings.CATEGORIES_STORAGE, settings.CATEGORIES_DATA_FILE)
