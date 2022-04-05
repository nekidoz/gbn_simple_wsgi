import settings

handlers = {
    'console': {
        'handler': 'LoggerConsoleHandler',
        'level': 0,
        'default_level': 0,
        'is_on': True,
    },
    'debug_file': {
        'handler': 'LoggerFileHandler',
        'file_name': settings.PATH_LOGS + 'debug.log',
        'level': 0,
        'default_level': 0,
        'is_on': True,
    },
    'app_file': {
        'handler': 'LoggerFileHandler',
        'file_name': settings.PATH_LOGS + 'app.log',
        'level': 0,
        'default_level': 0,
        'is_on': True,
    },
}

loggers = {
    settings.LOGGER_DEBUG: {
        'logger': 'Logger',
        'handlers': ['console', 'debug_file'],
        'level': 0,
        'default_level': 0,
        'is_on': True,
    },
    settings.LOGGER_RUNTIME: {
        'logger': 'Logger',
        'handlers': ['console', 'app_file'],
        'level': 0,
        'default_level': 0,
        'is_on': True,
    },
}
