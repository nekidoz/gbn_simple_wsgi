# Global app settings
from framework.persistence import ENGINE_JSON
from framework.persistence_sqlite import ENGINE_SQLITE

PATH_APP = "app/"                   # app files directory
PATH_DB = PATH_APP + "database/"    # database directory
PATH_LOGS = PATH_APP + "logs/"      # logs path

# SQLite datafile
SQLITE_DATA_FILE = PATH_DB + "database.db"

# Categories data config
#CATEGORIES_DATA_FILE = PATH_DB + "categories.json"      # Data file
#CATEGORIES_STORAGE = ENGINE_JSON                        # Storage engine
CATEGORIES_DATA_FILE = SQLITE_DATA_FILE                 # Data file
CATEGORIES_STORAGE = ENGINE_SQLITE                      # Storage engine
# Courses data config
#COURSES_DATA_FILE = PATH_DB + "courses.json"            # Data file
#COURSES_STORAGE = ENGINE_JSON                           # Storage engine
COURSES_DATA_FILE = SQLITE_DATA_FILE                    # Data file
COURSES_STORAGE = ENGINE_SQLITE                         # Storage engine

# Logger types
LOGGER_DEBUG = "debug"                                  # Debug logger name
LOGGER_RUNTIME = "runtime"                              # Runtime logger name
