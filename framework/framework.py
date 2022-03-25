# This is the main framework class
from framework.request import Request
from framework import settings
from framework.views import View404
from framework.urls import admin_urls
from pprint import pprint


# ATTRIBUTES:
# urls - project URL array (initialized at init()
# request - parsed WSGI request (initialized at call()
# PARAMETERS:
# urls - array of user app urls
# use_admin - whether to use admin; if true, its urls from urls.py are appended to user urls
#
# router processes full URL paths and wildcard (e.g. /someurl/*) URLs (see urls.py for example)
class Framework:

    def __init__(self, urls, use_admin: bool = False):
        self.urls = urls
        # Add admin URLs if requested and if paths not occupied
        if use_admin:
            for url in admin_urls:
                if not any(user_url for user_url in self.urls if user_url.url == url.url):
                    self.urls.append(url)
        pprint(self.urls)

    # PARAMETERS:
    # environ: словарь данных от сервера
    # start_response: функция для ответа серверу
    def __call__(self, environ: dict, start_response, *args, **kwargs):
        self.request = Request(environ)         # Should be done first - protected functions use it
        #print("Path: {}".format(self.request.path))
        #print("Path array: {}".format(self.request.path_array))
        #print("Query parameters ({}): {}".format(self.request.method, self.request.query_params))
        #print("HTTP headers: ")
        #pprint(self.request.headers)

        view = self._get_view()
        if view:
            response = view.run(self.request)
            if not response:
                response = View404().run(self.request)
        else:
            response = View404().run(self.request)

        # сначала в функцию start_response передаем код ответа и заголовки
        start_response(str(response.status_code), response.headers.items())
        # возвращаем тело ответа в виде списка байтов
        return [response.body.encode(settings.HTML_ENCODING)]

    # Process full URL paths and wildcard (e.g. /someurl/*) URL processing
    def _get_view(self):
        for url in self.urls:

            # wildcard URL processing
            if len(url.url) >= 2 and url.url[-2:] == "/*":
                # Check for cases like /someurl and /someurl/someotherurl
                if len(self.request.path) == len(url.url) - 2 or \
                        (len(self.request.path) > len(url.url) - 2 and \
                         self.request.path[:(len(url.url)-1)] == url.url[:-1]):
                    return url.view

            # full URL processing
            else:
                if url.url == self.request.path:
                    return url.view
