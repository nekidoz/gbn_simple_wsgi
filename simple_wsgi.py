from Templator import render
from page_controllers import page_controller
from urllib.parse import unquote

"""
Чтобы запустить приложение, наберите: gunicorn simple_wsgi:application
"""

# Ключи и константы для парсинга параметров запроса
ENVIRON_PATH_KEY = "PATH_INFO"          # Ключ словаря параметра с полным путем текущей страницы
ENVIRON_PATH_SEP = "/"                  # Разделитель URL (напр. /about/company)
ENVIRON_QUERY_KEY = "QUERY_STRING"      # Ключ словаря параметра со строкой запроса
ENVIRON_QUERY_SEP = "&"                 # Разделитель параметров запроса (напр. a=2&c=3)
ENVIRON_QUERY_KV_SEP = "="              # Разделитель ключей и значений в параметрах запроса (напр. a=2)
ENVIRON_REQ_METHOD = "REQUEST_METHOD"   # Ключ словаря с методом запроса
ENVIRON_REQ_GET = "GET"                 # Значение параметра для запроса GET
ENVIRON_REQ_POST = "POST"               # Значение параметра для запроса POST
ENVIRON_CONTENT_LEN_KEY = "CONTENT_LENGTH"  # Ключ параметра с длиной контента для запроса POST
ENVIRON_WSGI_INPUT_KEY = "wsgi.input"   # Ключ параметра со взодными данными WSGI для запроса POST

# Константы для работы с HTML
HTML_ENCODING = "utf-8"
HTML_GENERIC_PREFIX = '<!DOCTYPE html><html lang="ru"><head><meta charset="' + \
                      HTML_ENCODING + \
                      '"></head><body>'
HTML_GENERIC_SUFFIX = "</body></html>"

# Структура каталогов приложения
PATH_TEMPLATES = "templates/"           # путь к шаблонам html-страниц
PATH_STATIC = "static/"                 # путь к статическим (произвольным, не обрабатываемым приложением) страницам
PATH_PAGE_CONTROLLERS = "pages/"        # путь к page-контроллерам

# Темплейты
TEMPLATE_INDEX = "index.html"           # Главная страница
TEMPLATE_PARAMETER = "parameter.html"   # Страница индивидуальных параемтров
TEMPLATE_404 = "error404.html"          # Страница сообщения об ошибке URL
TEMPLATE_EXTENSION = ".html"            # Расширение файла страницы

# Прочие константы
EMAIL_ADMIN = "nekidoz@yandex.ru"

def htmlWrap(pageBody):
    return HTML_GENERIC_PREFIX + pageBody + HTML_GENERIC_SUFFIX

# Делит путь path на токены и удаляет последний токен, если он пустой (т.е. если URL кончается на /)
# Возвращает массив токенов пути
def parse_page_path(path: str):
    path_array = path.split(ENVIRON_PATH_SEP)
    if path_array[len(path_array) - 1].strip() == '':
        del path_array[len(path_array) - 1]
    return path_array

# Делит строку запроса на отдельные параметры
# Возвращает словарь параметров
def parse_query_params(query: str) -> dict:
    param_dict = {}
    if query:
        # Перед раскодированием избавимся от знаков '+', которыми заменены пробелы
        query = query.replace('+', ' ')
        params = query.split(ENVIRON_QUERY_SEP)             # Получение списка параметров запроса
        for param in params:
            key, value = param.split(ENVIRON_QUERY_KV_SEP)  # Получение ключа и значения для каждого параметра
            param_dict[key] = unquote(value)
    return param_dict

# Возвращает строку запроса из тела запроса POST
def fetch_post_query_parameters(environ) -> str:
    content_length_data = environ.get(ENVIRON_CONTENT_LEN_KEY)  # Получаем длину тела
                                                                # Приводим к int
    content_length = int(content_length_data) if content_length_data else 0
    content = environ[ENVIRON_WSGI_INPUT_KEY].read(content_length) if content_length > 0 else b''
    query_str = content.decode(encoding=HTML_ENCODING) if content else ""
    return query_str

def application(environ, start_response):
    """
    environ: словарь данных от сервера
    start_response: функция для ответа серверу
    """

    # Получить массив токенов пути страницы и словарь с параметрами запроса
    path_array = parse_page_path(environ[ENVIRON_PATH_KEY])     # Получить массив токенов пути для страницы
    if environ[ENVIRON_REQ_METHOD] == ENVIRON_REQ_GET:
        query_str = environ[ENVIRON_QUERY_KEY]                  # Строка запроса уже содержится в словаре метода GET
    elif environ[ENVIRON_REQ_METHOD] == ENVIRON_REQ_POST:
        query_str = fetch_post_query_parameters(environ)        # Получить строку запроса из тела метода POST
    else:
        query_str = ""                                          # Неизвестный метод - и строки запроса нет
    query_dict = parse_query_params(query_str)                  # Получить массив параметров запроса GET/POST
    print("Query parameters ({}): {}".format(environ[ENVIRON_REQ_METHOD], query_dict))

                                    # Смотрим, есть ли такой page-контроллер
    exitCode, response = page_controller('/'.join(token for token in path_array), environ)
    if exitCode:
        pass    # Если есть, ничего не делаем - все сделал page controller
    elif len(path_array) > 2:       # Принимаем только URL 1 уровня от корня
        try:
            response = render(PATH_TEMPLATES + TEMPLATE_404,
                              title="Страница не найдена", parameter=environ[ENVIRON_PATH_KEY])
        except FileNotFoundError:
            response = htmlWrap("Страница {} не найдена".format(environ[ENVIRON_PATH_KEY]))
        exitCode = '404 not found'

    elif len(path_array) > 1:       # Страница параметра или произвольная страница
        path_array[1] = path_array[1].strip()
        if path_array[1] in environ:    # Есть такой параметр
            try:
                response = render(PATH_TEMPLATES + TEMPLATE_PARAMETER,
                                  title='Параметр запроса', params=environ, param=path_array[1])
            except FileNotFoundError:
                response = htmlWrap("Параметр '{}' : {}".format(path_array[1], environ[path_array[1]]))
            exitCode = '200 OK'

        else:                       # Нет такого параметра - поищем страницу
            try:
                response = render(PATH_STATIC + path_array[1] + TEMPLATE_EXTENSION)
                exitCode = '200 OK'

            except FileNotFoundError:   # Ничего не нашли - ошибка
                try:
                    response = render(PATH_TEMPLATES + TEMPLATE_404,
                                      title="Страница не найдена", parameter=environ[ENVIRON_PATH_KEY])
                except FileNotFoundError:
                    response = htmlWrap("Страница {} не найдена".format(environ[ENVIRON_PATH_KEY]))
                exitCode = '404 not found'

    else:                       # Корневая страница
        try:
            response = render(PATH_TEMPLATES + TEMPLATE_INDEX,
                              title='Главная страница', params=environ, query_params=query_dict)
            exitCode = '200 OK'
        except FileNotFoundError:       # Нет корневой страницы
            try:
                response = render(PATH_TEMPLATES + TEMPLATE_404,
                                  title="Корневая страница не найдена, обратитесь к администратору",
                                  parameter=EMAIL_ADMIN)
            except FileNotFoundError:
                response = htmlWrap("Корневая страница не найдена, обратитесь к администратору: {}"
                                    .format(EMAIL_ADMIN))
            exitCode = '404 not found'

    # сначала в функцию start_response передаем код ответа и заголовки
    start_response(exitCode, [('Content-Type', 'text/html')])
    # возвращаем тело ответа в виде списка байтов
    #return [b'Hello world from a simple WSGI application!']
    return [response.encode('utf-8')]
