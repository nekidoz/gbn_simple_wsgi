def application(environ, start_response):
    """
    :param environ: словарь данных от сервера
    :param start_response: функция для ответа серверу
    """

    params = """<!DOCTYPE html >
    <!DOCTYPE html>
    <html lang="ru"> 
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <title> Список параметров вызова </title>
    </head>
    <body>
    <div>
        <h1> Список параметров вызова </h1>
        <p> Нажмите на имени параметра, чтобы увидеть его содержимое </p>
        <ul>
    """

    for param in environ:
        params += '<li> <a href="{}"> {} </a> : {}</li>\n'.format(param, param, environ[param])

    params += """
        </ul>
    </div>
    </body>
    </html>
    """
    # сначала в функцию start_response передаем код ответа и заголовки
    start_response('200 OK', [('Content-Type', 'text/html')])
    # возвращаем тело ответа в виде списка из bite
    #return [b'Hello world from a simple WSGI application!']
    return [params.encode('utf-8')]
