# Global app settings
from framework.persistence import PersistenceEngineType

PATH_APP = "app/"                   # app files directory
PATH_DB = PATH_APP + "database/"    # database directory

# Categories data config
CATEGORIES_DATA_FILE = PATH_DB + "categories.json"      # Data file
CATEGORIES_STORAGE = PersistenceEngineType.JSON         # Storage engine
# Courses data config
COURSES_DATA_FILE = PATH_DB + "courses.json"            # Data file
COURSES_STORAGE = PersistenceEngineType.JSON            # Storage engine

