# Global app settings
from framework.persistence import PersistenceEngineType

PATH_APP = "app/"                   # app files directory
PATH_DB = PATH_APP + "database/"    # database directory
PATH_LOGS = PATH_APP + "logs/"      # logs path

# Categories data config
CATEGORIES_DATA_FILE = PATH_DB + "categories.json"      # Data file
CATEGORIES_STORAGE = PersistenceEngineType.JSON         # Storage engine
# Courses data config
COURSES_DATA_FILE = PATH_DB + "courses.json"            # Data file
COURSES_STORAGE = PersistenceEngineType.JSON            # Storage engine

# Logger types
LOGGER_DEBUG = "debug"                                  # Debug logger name
LOGGER_RUNTIME = "runtime"                              # Runtime logger name
