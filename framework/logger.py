from functools import wraps, total_ordering
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import sys

from framework.singleton import Singleton
from framework import settings


# Logger levels enumeration class
@total_ordering                 # implements all the other comparisons (Enum implements __eq__, we implement __lt__)
class LoggerLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


# Default logger level for the logging system
LOGGER_DEFAULT_LEVEL = LoggerLevel.DEBUG


# Abstract class implementing logger handler skeleton.
# Logger handler has similar function to that of the Python standard library:
# it implements formatting and writing log message to specific media and is called by Logger to do the job.
# This abstract class implements:
# - __init__() - turning handler on and off,
# setup of the minimum logging level for handler and default logging level for messages,
# - compose_message() - composing log message string,
# - validate_message() - deciding whether to write a log entry depending on the state of handler and message level.
# ATTRS:
# level - the minimum message logging level for the handler to log the message
# defaultLevel - default logging level for messages with no logging level specified
# isOn - flag showing whether the handler is on (logging messages)
class LoggerHandler(ABC):

    @abstractmethod
    def __init__(self, level: LoggerLevel, default_level: LoggerLevel, is_on: bool = True):
        self.level = level if level else LoggerFabric().defaultLevel
        self.defaultLevel = default_level if default_level else LoggerFabric().defaultLevel
        self.isOn = is_on

    @staticmethod
    def compose_message(message: str, level: LoggerLevel, source: str = "") -> str:
        return "{}, {}, {}, {}".format(datetime.now().isoformat(timespec='microseconds'), level.value, source, message)

    def validate_message(self, message: str, level: LoggerLevel = None, source: str = None):
        message_level = level if level else self.defaultLevel
        if self.isOn and message_level >= self.level:
            return self.compose_message(message=message, level=message_level, source=source)
        else:
            return None


# Concrete class of console logger handler. Implements actual writing to the console.
class LoggerConsoleHandler(LoggerHandler):

    def __init__(self, level: LoggerLevel = None, default_level: LoggerLevel = None,
                 is_on: bool = True):
        super().__init__(level, default_level, is_on)

    def log(self, message: str, level: LoggerLevel = None, source: str = None) -> bool:
        rendered_message = self.validate_message(message, level, source)
        if rendered_message:
            print(rendered_message)
            return True
        else:
            return False


# Concrete class of file logger handler. Implements actual writing to a file.
# ATTRS:
# fileName - full path and file name of the log file to log messages to
class LoggerFileHandler(LoggerHandler):

    def __init__(self, file_name: str, level: LoggerLevel = None, default_level: LoggerLevel = None,
                 is_on: bool = True):
        self.fileName = file_name
        super().__init__(level, default_level, is_on)

    def log(self, message: str, level: LoggerLevel = None, source: str = None) -> bool:
        rendered_message = self.validate_message(message, level, source)
        if rendered_message:
            try:
                with open(self.fileName, 'a', encoding=settings.HTML_ENCODING) as f:
                    f.write(rendered_message + "\n")
                return True
            except IOError as e:
                print("LoggerFileHandler: I/O error({}): {}".format(e.errno, e.strerror))
            except:
                print("LoggerFileHandler: Unexpected error: ()".format(sys.exc_info()[0]))
            return False
        else:
            return False


# The Logger class dispatches log requests to the logger handlers configured for this logger instance.
# __init__() - initializes the logger by storing its handlers and default properties
# log() - check if should log the message by checking whether the logger is on and
# message logging level is not below the minimum logger logging level,
# then call all the handlers to actually log the message
# ATTRS:
# handlers - array of 0 or more handlers (function pointers) to dispatch messages to
# level - the minimum message logging level for the logger to log the message
# defaultLevel - default logging level for messages with no logging level specified
# isOn - flag showing whether the logger is on (logging messages)
class Logger:

    def __init__(self, handlers: [], level: LoggerLevel, default_level: LoggerLevel, is_on: bool = True):
        # init handlers
        self.handlers = []
        for handler in handlers:
            self.handlers.append(LoggerFabric().handlers[handler])
        # init other parameters
        self.level = level if level else LoggerFabric().defaultLevel
        self.defaultLevel = default_level if default_level else LoggerFabric().defaultLevel
        self.isOn = is_on

    def log(self, message: str, level: LoggerLevel = None, source: str = None) -> bool:
        message_level = level if level else self.defaultLevel
        if self.isOn and message_level >= self.level:
            for handler in self.handlers:
                handler.log(message=message, level=level, source=source)
            return True
        else:
            return False

# This class should be actually called by any app to reference a logger and then log a message
# __init__() - sets the actual logger, default logging level and message source reference
# for subsequent calls to the Log instance object
# __call__() - logs the message (calls a logger instance) filling in omitted parameters
# ATTRS:
# logger - the actual logger function
# default_level - default level for any message with no level specified
# default_source - default message source for any message with no source specified
class Log:

    def __init__(self, logger, default_level: LoggerLevel = None, default_source: str = None):
        self.logger = LoggerFabric().loggers[logger]
        self.default_level = default_level if default_level else self.logger.defaultLevel
        self.default_source = default_source if default_source else ""

    def __call__(self, message: str, level: LoggerLevel = None, source: str = None) -> bool:
        return self.logger.log(message=message,
                               level=level if level else self.default_level,
                               source=source if source else self.default_source)


# Use this class to initialize the logging subsystem:
# turn in on and off, set handlers and loggers and the default message level
# ATTRIBUTES:
# isOn - logging is on flag
# loggers - dictionary of loggers - id and the respective Logger
# handlers - dictionary of handlers - id and the respective LoggerHandler
# defaultLevel - default logging level if not specified in individual messages
class LoggerFabric(Singleton):

    # Pass a dictionary of logger files if you want to use multiple.
    # Every time __init__() is called, the logger list is updated
    def __init__(self, turn_on: bool = True,
                 handlers: dict = None, loggers: dict = None,
                 default_level: LoggerLevel = None):
        if not hasattr(self, 'isOn'):
            self.isOn = turn_on

        # This should be called before initializing loggers and handlers - they use this default level at init
        if default_level:
            self.defaultLevel = default_level
        elif not hasattr(self, 'defaultLevel'):
            self.defaultLevel = LOGGER_DEFAULT_LEVEL

        # Init the handlers dictionary and set handlers if any passed
        if not hasattr(self, 'handlers'):       # initialize handlers dictionary if none yet
            self.handlers = {}
        if handlers:
            # first item in a given handler's dictionary is its class name, the rest are the initializer parameters
            for handler, parameters in handlers.items():
                self.handlers[handler] = globals()[parameters['handler']](**dict(list(parameters.items())[1:]))

        # Init the loggers dictionary and set loggers if any passed
        if not hasattr(self, 'loggers'):       # initialize loggers dictionary if none yet
            self.loggers = {}
        if loggers:
            # first item in a given handler's dictionary is its class name, the rest are the initializer parameters
            for logger, parameters in loggers.items():
                self.loggers[logger] = globals()[parameters['logger']](**dict(list(parameters.items())[1:]))


# Decorator to enable logging for a function
def logging(header: str = None, logger=None, level: LoggerLevel = LoggerLevel.DEBUG):
    def enable_logger(func):
        @wraps(func)
        def logged_function(*args, **kwargs):
            if LoggerFabric().isOn:
                print("FUNCTION: {}, logger: {}, level: {}".format(header, logger, level))
            return func(*args, **kwargs)
        return logged_function
    return enable_logger
