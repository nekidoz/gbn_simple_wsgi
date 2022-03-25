# REFERENCE DESIGN
from jinja2 import Template  # Используем шаблонизатор Jinja2

from framework.request import Request
from framework.response import Response
from framework import settings

class View:
    pass


# Generated view from a body string using minimal HTML headers and footers
# ATTRIBUTES:
# body - body string wrapped in minimal HTML headers and footers
# status_code - 200 by default
class Minimal(View):
    GENERIC_PREFIX = '<!DOCTYPE html><html lang="ru"><head><meta charset="' + \
                     settings.HTML_ENCODING + \
                     '"></head><body>'
    GENERIC_SUFFIX = "</body></html>"

    def __init__(self, body: str, status_code: int = settings.HTTP_CODE_OK):
        self.body = self.GENERIC_PREFIX + body + self.GENERIC_SUFFIX
        self.status_code = status_code

    def run(self) -> Response:
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
class Render(View):

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
                self.body = Minimal("Страница {} не найдена".format(template_name)).body
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
            return Render(status_code=settings.HTTP_CODE_NOTFOUND,
                          template_name=settings.PATH_TEMPLATES + settings.TEMPLATE_404,
                          raise_filenotfound=True,
                          title="Страница не найдена", parameter=request.path).run(request)
        except FileNotFoundError:
            return Minimal(status_code=settings.HTTP_CODE_NOTFOUND,
                           body="Страница {} не найдена".format(request.path))


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
                return Render(template_name=settings.PATH_TEMPLATES + settings.TEMPLATE_PARAMETER,
                              raise_filenotfound=True,
                              title='Параметр запроса',
                              params=request.environ,
                              param=request.path_array[len(request.path_array)-1]).run(request)
            except FileNotFoundError:
                return Minimal("Параметр '{}' : {}"
                               .format(request.path_array[2],
                                       request.environ[request.path_array[len(request.path_array)-1]])).run()

        # Корневая страница админки (e.g. /admin)
        elif request.path_array[len(request.path_array)-1] == self.admin_root:
            return Render(settings.PATH_TEMPLATES + settings.TEMPLATE_INDEX,
                          title='АДМИН - Главная страница',
                          params=request.environ, query_params=request.query_params).run(request)

        else:
            return Minimal("Это неизвестная страница админки: {}".format(request.path)).run()
