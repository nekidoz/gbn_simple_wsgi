# SETTINGS
from jinja2 import Environment, PrefixLoader, FileSystemLoader, select_autoescape
from pprint import pprint

from framework.singleton import Singleton


# ATTRIBUTES:
# jinja_env - Jinja environment
# PARAMETERS:
# template_path - path(s) to search for Jinja templates - can be a str or a list of str to be searched in order
class Environ(Singleton):

    # Initialize app and admin urls
    def __init__(self, template_path=None):
        # Initialize jinja environment - app and fw templates will be selected by prefix
        if not hasattr(self, 'jinja_env'):
            self.jinja_env = Environment(loader=PrefixLoader({
                TEMPLATES_FW: FileSystemLoader(searchpath=PATH_JINJA_TEMPLATES,
                                               encoding=HTML_ENCODING),
                TEMPLATES_APP: FileSystemLoader(searchpath=template_path if template_path else "./",
                                                encoding=HTML_ENCODING)
            }), autoescape=select_autoescape(
                enabled_extensions=('txt'),
                default_for_string=False,
                default=False
            ))
            # print(self.jinja_env.list_templates(extensions=['html']))


PATH_FRAMEWORK = "framework/"

# jinja templates directories
PATH_JINJA_TEMPLATES = PATH_FRAMEWORK + "templates/"
TEMPLATES_APP = "app"
TEMPLATES_FW = "fw"

# HTTP codes
HTTP_CODE_OK = 200
HTTP_CODE_NOTFOUND = 404
HTTP_CODE_TEAPOT = 418

# standard urls
URL_NOT_FOUND = '/notfound'
STATUS_NOT_FOUND = "307 Temporary redirect"

# Константы для работы с HTML
HTML_ENCODING = "utf-8"
