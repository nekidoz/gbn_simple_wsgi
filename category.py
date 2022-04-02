import uuid

from framework.persistence import Persistence, PersistenceSerializable

import settings


class Category(PersistenceSerializable):
    id: uuid.UUID
    name: str

    def __init__(self, id: uuid.UUID = None, name: str = None):
        if id:
            self.id = id
        else:
            self.id = uuid.uuid4()
        self.name = name

    # Register Category's Persistence storage
    @staticmethod
    def register() -> bool:
        return Persistence.register(Category, settings.CATEGORIES_STORAGE, settings.CATEGORIES_DATA_FILE)
