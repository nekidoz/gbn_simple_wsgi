# sws - simple_wsgi settings and generic functions file
from jinja2 import Template             # Используем шаблонизатор Jinja2

# Ключи и константы для парсинга параметров запроса
ENV_PATH_KEY = "PATH_INFO"          # Ключ словаря параметра с полным путем текущей страницы
ENV_PATH_SEP = "/"                  # Разделитель URL (напр. /about/company)
ENV_QUERY_KEY = "QUERY_STRING"      # Ключ словаря параметра со строкой запроса
ENV_QUERY_SEP = "&"                 # Разделитель параметров запроса (напр. a=2&c=3)
ENV_QUERY_KV_SEP = "="              # Разделитель ключей и значений в параметрах запроса (напр. a=2)
ENV_REQ_METHOD = "REQUEST_METHOD"   # Ключ словаря с методом запроса
ENV_REQ_GET = "GET"                 # Значение параметра для запроса GET
ENV_REQ_POST = "POST"               # Значение параметра для запроса POST
ENV_CONTENT_LEN_KEY = "CONTENT_LENGTH"  # Ключ параметра с длиной контента для запроса POST
ENV_WSGI_INPUT_KEY = "wsgi.input"   # Ключ параметра со взодными данными WSGI для запроса POST

# Структура каталогов приложения
PATH_TEMPLATES = "templates/"           # путь к шаблонам html-страниц
PATH_STATIC = "static/"                 # путь к статическим (произвольным, не обрабатываемым приложением) страницам
PATH_PAGE_CONTROLLERS = "pages/"        # путь к page-контроллерам

# Константы для работы с HTML
HTML_ENCODING = "utf-8"
HTML_GENERIC_PREFIX = '<!DOCTYPE html><html lang="ru"><head><meta charset="' + \
                      HTML_ENCODING + \
                      '"></head><body>'
HTML_GENERIC_SUFFIX = "</body></html>"
HTML_200 = "200 OK"
HTML_404 = "404 not found"
HTML_418 = "418 I’m a teapot"


# Wrap pageBody string into minimum sufficient HTML5 meta information
def htmlWrap(pageBody):
    return HTML_GENERIC_PREFIX + pageBody + HTML_GENERIC_SUFFIX

def render(template_name, **kwargs):
    """
    Минимальный пример работы с шаблонизатором
    :param template_name: имя шаблона
    :param kwargs: параметры для передачи в шаблон :return:
    """

    # Открываем шаблон по имени
    with open(template_name, encoding='utf-8') as f:
        # Читаем
        template = Template(f.read())

    # рендерим шаблон с параметрами
    return template.render(**kwargs)