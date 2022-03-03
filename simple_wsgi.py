from Templator import render

"""
Чтобы запустить приложение, наберите: gunicorn simple_wsgi:application
"""

# Настройки
ENVIRON_PATH_KEY = "PATH_INFO"          # Ключ словаря с полным путем текущей страницы
ENVIRON_PATH_SEP = "/"                  # Разделитель URL
HTML_GENERIC_PREFIX = '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"></head><body>'
HTML_GENERIC_SUFFIX = "</body></html>"
EMAIL_ADMIN = "nekidoz@yandex.ru"
# Темплейты
TEMPLATE_INDEX = "index.html"           # Главная страница
TEMPLATE_PARAMETER = "parameter.html"   # Страница индивидуальных параемтров
TEMPLATE_404 = "error404.html"          # Страница сообщения об ошибке URL
TEMPLATE_EXTENSION = ".html"            # Расширение файла страницы

def htmlWrap(pageBody):
    return HTML_GENERIC_PREFIX + pageBody + HTML_GENERIC_SUFFIX

def application(environ, start_response):
    """
    environ: словарь данных от сервера
    start_response: функция для ответа серверу
    """

    # Разделить путь на токены и удалить последний токен, если он пустой
    path_array = environ[ENVIRON_PATH_KEY].split(ENVIRON_PATH_SEP)
    if path_array[len(path_array)-1].strip() == '':
        del path_array[len(path_array)-1]

    if len(path_array) > 2:     # Принимаем только URL 1 уровня от корня
        try:
            response = render(TEMPLATE_404, title="Страница не найдена", parameter=environ[ENVIRON_PATH_KEY])
        except FileNotFoundError:
            response = htmlWrap("Страница {} не найдена".format(environ[ENVIRON_PATH_KEY]))
        exitCode = '404 not found'

    elif len(path_array) > 1:   # Страница параметра или произвольная страница
        path_array[1] = path_array[1].strip()
        if path_array[1] in environ:    # Есть такой параметр
            try:
                response = render(TEMPLATE_PARAMETER, title='Параметр запроса', params=environ, param=path_array[1])
            except FileNotFoundError:
                response = htmlWrap("Параметр '{}' : {}".format(path_array[1], environ[path_array[1]]))
            exitCode = '200 OK'

        else:                           # Нет такого параметра - поищем страницу
            try:
                response = render(path_array[1] + TEMPLATE_EXTENSION)
                exitCode = '200 OK'

            except FileNotFoundError:   # Ничего не нашли - ошибка
                try:
                    response = render(TEMPLATE_404, title="Страница не найдена", parameter=environ[ENVIRON_PATH_KEY])
                except FileNotFoundError:
                    response = htmlWrap("Страница {} не найдена".format(environ[ENVIRON_PATH_KEY]))
                exitCode = '404 not found'

    else:                       # Корневая страница
        try:
            response = render(TEMPLATE_INDEX, title='Список параметров запроса', params=environ)
            exitCode = '200 OK'
        except FileNotFoundError:       # Нет корневой страницы
            try:
                response = render(TEMPLATE_404, title="Корневая страница не найдена, обратитесь к администратору",
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
