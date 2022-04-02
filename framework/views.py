# REFERENCE DESIGN
from abc import ABC, abstractmethod
from jinja2 import Template  # Используем шаблонизатор Jinja2
from dataclasses import dataclass
from enum import Enum
from pprint import pprint

from framework.request import Request
from framework.response import Response
from framework import settings
from framework.singleton import Singleton

# Структура каталогов приложения
PATH_TEMPLATES = "framework/templates/"                    # путь к шаблонам служебных html-страниц

# Admin Page templates
TEMPLATE_404 = "error404.html"  # Страница сообщения об ошибке URL
TEMPLATE_INDEX = "index.html"  # Главная страница
TEMPLATE_PARAMETER = "parameter.html"  # Страница индивидуальных параемтров


# View Interface
class View(ABC):

    @abstractmethod
    def run(self, request: Request, *args, **kwargs) -> Response:
        pass


# Generated view from a body string using minimal HTML headers and footers
# ATTRIBUTES:
# body - body string wrapped in minimal HTML headers and footers
# status_code - 200 by default
class MinimalView(View):
    GENERIC_PREFIX = '<!DOCTYPE html><html lang="ru"><head><meta charset="' + \
                     settings.HTML_ENCODING + \
                     '"></head><body>'
    GENERIC_SUFFIX = "</body></html>"

    def __init__(self, body: str, status_code: int = settings.HTTP_CODE_OK):
        self.body = self.GENERIC_PREFIX + body + self.GENERIC_SUFFIX
        self.status_code = status_code

    def run(self, request: Request, *args, **kwargs) -> Response:
        return Response(status_code=self.status_code, body=self.body)


# Generated view from template_name using jinja2 render()
# Returns standard 404 page if template_name not found
# PARAMETERS:
# init(template_name: str, status_code: int) - jinja2 template name, optional status code
# and optional throw filenotfound exception
# run(request) - Request object
# ATTRIBUTES:
# body - rendered body after init()
# status_code - 200 by default if template found, 404 if not
class SimpleView(View):

    def __init__(self,
                 template_name: str, status_code: int=settings.HTTP_CODE_OK,
                 raise_filenotfound: bool = False, **kwargs):
        """
        Минимальный пример работы с шаблонизатором
        :param template_name: имя шаблона
        :param kwargs: параметры для передачи в шаблон :return:
        """

        try:
            # Открываем шаблон по имени
            with open(template_name, encoding=settings.HTML_ENCODING) as f:
                # Читаем
                template = Template(f.read())
            # рендерим шаблон с параметрами
            self.body = template.render(**kwargs)
            self.status_code = status_code
        except FileNotFoundError:
            if not raise_filenotfound:
                # Template not found
                self.body = MinimalView("Страница {} не найдена".format(template_name)).body
                self.status_code = settings.HTTP_CODE_NOTFOUND
            else:
                # Throw FileNotFoundError - needed when this function is called for 404 page
                raise FileNotFoundError

    def run(self, request: Request, *args, **kwargs) -> Response:
        return Response(status_code=self.status_code, body=self.body)


class View404(View):

    @staticmethod
    def run(request: Request, *args, **kwargs):

        try:
            return SimpleView(status_code=settings.HTTP_CODE_NOTFOUND,
                              template_name=PATH_TEMPLATES + TEMPLATE_404,
                              raise_filenotfound=True,
                              title="Страница не найдена", parameter=request.path).run(request)
        except FileNotFoundError:
            return MinimalView(status_code=settings.HTTP_CODE_NOTFOUND,
                               body="Страница {} не найдена".format(request.path))


# *********************************************** BASE VIEW *******************************************************


# BaseView sections enumeration
class BaseViewSection(Enum):
    base_view = 1
    header = 2
    footer = 3
    left_sidebar = 4
    right_sidebar = 5

# BaseView section description data class
@dataclass
class BaseViewTagData:
    template_tag: str           # jinja2 template tag
    html_include_tag: str       # jinja2 variable (tag) to include rendered html
    default_template: str       # default template file


# BaseView class layout object used by all BaseView-inheriting classes for rendering base templates,
# and thus it is Singleton
# PARAMS:
# status_code - http status code of the last template load operation
# status_message - status message of the last template load operation
# isInit - __init__() already called flag
class BaseViewLayout(Singleton):
    _PATH_BASEVIEW_TEMPLATES = "framework/templates/baseview/"   # путь к шаблонам html-страниц темплейтов BaseView
    _template_settings = {
        BaseViewSection.base_view:
            BaseViewTagData(template_tag='base_view_template', html_include_tag='',
                            default_template=_PATH_BASEVIEW_TEMPLATES + "base_view_template.html"),
        BaseViewSection.header:
            BaseViewTagData(template_tag='header_template', html_include_tag='header_html_include',
                            default_template=_PATH_BASEVIEW_TEMPLATES + "header_template.html"),
        BaseViewSection.footer:
            BaseViewTagData(template_tag='footer_template', html_include_tag='footer_html_include',
                            default_template=_PATH_BASEVIEW_TEMPLATES + "footer_template.html"),
        BaseViewSection.left_sidebar:
            BaseViewTagData(template_tag='left_sidebar_template', html_include_tag='left_sidebar_html_include',
                            default_template=_PATH_BASEVIEW_TEMPLATES + "left_sidebar_template.html"),
        BaseViewSection.right_sidebar:
            BaseViewTagData(template_tag='right_sidebar_template', html_include_tag='right_sidebar_html_include',
                            default_template=_PATH_BASEVIEW_TEMPLATES + "right_sidebar_template.html")
    }
    _templates = {}                                 # templates to pass to renderer - currently empty
    _html_includes = {}                             # html includes to pass to renderer - currently empty

    # REQUIRED (call super() if redefined): Assign default base view template and include templates
    def __init__(self, set_default_templates:bool = True, raise_filenotfound: bool = False):

        # Only allow to init once
        if hasattr(self, 'isInit'):
            return
        # Load all the default templates: base and includes - abort if file not found; initialize html includes
        for section, section_data in self._template_settings.items():
            self._html_includes[section_data.html_include_tag] = ""                 # init html include field
            if set_default_templates or section == BaseViewSection.base_view:       # Base view displayed anyway
                if not self.set_template(section, raise_filenotfound=raise_filenotfound):
                    return
            else:
                self._templates[section_data.template_tag] = None
        # All templates loaded - return OK
        self.isInit = True                  # 'Already initialized' flag

    # RETURNS: boolean status and Template object
    def _load_template(self, template_name: str, raise_filenotfound: bool = False):
        try:
            # Open template file
            with open(template_name, encoding=settings.HTML_ENCODING) as f:
                # Read template file
                template = Template(f.read())
                self.status_code = settings.HTTP_CODE_OK
                self.status_message = "OK"
                return True, template
        except FileNotFoundError:
            # Template not found
            self.status_code = settings.HTTP_CODE_NOTFOUND
            self.status_message = template_name
            # Throw FileNotFoundError if requested
            if raise_filenotfound:
                raise FileNotFoundError
            else:
                return False, None

    # NOTE: load template from template_path/template_file_name or default template
    # into template dictionary entry; raise exception on file not found condition if requested
    def set_template(self, section: BaseViewSection,
                     template_file_name: str = None, template_path: str = None,
                     clear_html_include: bool = False, raise_filenotfound: bool = False) -> bool:
        section_data = self._template_settings[section]
        # determine template name - passed on or default
        template_name = ((template_path if template_path else "") + template_file_name) if template_file_name \
            else section_data.default_template
        # load template
        success, self._templates[section_data.template_tag] = self._load_template(template_name, raise_filenotfound)
        if success and clear_html_include:                   # Clear section's html include field if requested
            self._html_includes[section_data.html_include_tag] = ""
        return success

    def render_html_include(self, section: BaseViewSection,
                            template_file_name: str, template_path: str = None,
                            clear_template: bool = False, raise_filenotfound: bool = False, **kwargs) -> bool:
        section_data = self._template_settings[section]
        template_name = (template_path if template_path else "") + template_file_name
        # load template
        success, template = self._load_template(template_name, raise_filenotfound)
        if success:                 # Render the template if loaded
            self._html_includes[section_data.html_include_tag] = template.render(**kwargs)
            if clear_template:      # Clear section's template if requested
                self._templates[section_data.template_tag] = None
        else:
            self._html_includes[section_data.html_include_tag] = "Страница {} не найдена".format(template_name)
        return success

    @property
    def templates(self):
        return self._templates

    @property
    def html_includes(self):
        return self._html_includes


class BaseView(View):

    def __init__(self,
                 template_name: str, status_code: int=settings.HTTP_CODE_OK,
                 raise_filenotfound: bool = False, **kwargs):

        try:
            # Открываем шаблон по имени
            with open(template_name, encoding=settings.HTML_ENCODING) as f:
                # Читаем
                template = Template(f.read())

            # Get BaseViewLayout singleton instance
            layout = BaseViewLayout()
            # Render the template tree
            self.body = template.render(**layout.templates, **layout.html_includes, **kwargs)
            self.status_code = status_code
        except FileNotFoundError:
            if not raise_filenotfound:
                # Template not found
                self.body = MinimalView("Страница {} не найдена".format(template_name)).body
                self.status_code = settings.HTTP_CODE_NOTFOUND
            else:
                # Throw FileNotFoundError - needed when this function is called for 404 page
                raise FileNotFoundError

    def run(self, request: Request, *args, **kwargs) -> Response:
        return Response(status_code=self.status_code, body=self.body)

# *********************************************** BASE VIEW end ***************************************************

# Admin view - HTTP parameters and all that
# PARAMETERS:
# admin_root - path token of admin root, e.g. for /someurl/admin it should be "admin" (the default)
class Admin(View):

    def __init__(self, admin_root: str = "admin"):
        self.admin_root = admin_root

    def run(self, request: Request, *args, **kwargs) -> Response:

        # Есть такой параметр WSGI/HTTP
        if request.path_array[len(request.path_array)-1] in request.environ:
            try:
                return SimpleView(template_name=PATH_TEMPLATES + TEMPLATE_PARAMETER,
                                  raise_filenotfound=True,
                                  title='Параметр запроса',
                                  params=request.environ,
                                  param=request.path_array[len(request.path_array)-1]).run(request)
            except FileNotFoundError:
                return MinimalView("Параметр '{}' : {}"
                                   .format(request.path_array[2],
                                       request.environ[request.path_array[len(request.path_array)-1]])).run(request)

        # Корневая страница админки (e.g. /admin)
        elif request.path_array[len(request.path_array)-1] == self.admin_root:
            return SimpleView(PATH_TEMPLATES + TEMPLATE_INDEX,
                              title='АДМИН - Главная страница',
                              params=request.environ, query_params=request.query_params).run(request)

        else:
            return MinimalView("Это неизвестная страница админки: {}".format(request.path)).run(request)
