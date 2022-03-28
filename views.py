# REFERENCE DESIGN
from framework.response import Response
from framework.request import Request
from framework.views import View, BaseView, SimpleView, MinimalView
from framework.singleton import Singleton
from framework.urls import Url

# Imports for Contact class
from datetime import datetime
import os
import settings


# Main page controller  - SINGLETON! Initialize it with menu urls when Framework is initialized!
class Index(View, Singleton):
    HTML_TEMPLATE = settings.PATH_APP + "index_body.html"             # Page template

    # Initialize urls property with the passed array, or with empty array if not yet initialized
    def __init__(self, urls: [Url] = None):
        if urls is not None:
            self.urls = urls
        elif not hasattr(self, 'urls'):
            self.urls = []
        #print("urls {}: param: {} self: {}".format(id(self), urls, self.urls))

    def run(self, request: Request, *args, **kwargs) -> Response:
        return BaseView(self.HTML_TEMPLATE, title="Главная страница", urls=self.urls).run(request)


# Page Controller для формы обратной связи
# Состав:
# - файл contact.html шаблона формы обратной связи в папке page controller'ов
# - файл contact_success.html шаблона сообщения об успехе формы обратной связи в папке page controller'ов
# - папка contact_messages/ для файлов сообщений в папке page controller'ов с правами записи в нее,
#   или права на создание такой папки в папке page controller'ов
# Метод GET отображает форму.
# Метод POST записывает данные формы в папку сообщений в файл с именем в формате YYYY-MM-DDTHH-MM-SS_email.
class Contact(View):

    HTML_TEMPLATE_FORM = settings.PATH_APP + "contact_body.html"             # Шаблон формы обратной связи
    HTML_TEMPLATE_SUCCESS = settings.PATH_APP + "contact_success_body.html"  # Шаблон страницы успеха
    PATH_CONTACT_MESSAGES = settings.PATH_APP + "contact_messages/"     # Папка для файлов сообщений
    QPARAM_NAME = "name"                                                # Параметры POST с полями сообщения
    QPARAM_EMAIL = "email"
    QPARAM_TITLE = "title"
    QPARAM_MESSAGE = "msg"

    def run(self, request: Request, *args, **kwargs) -> Response:
        if request.method == "GET":             # GET: отобразить форму обратной связи
            return BaseView(self.HTML_TEMPLATE_FORM, *args, **kwargs).run(request)

        elif request.method == "POST":          # POST: обработать данные формы обратной связи
                                            # Сформировать строку сообщения
            message = "Имя: {}\nEmail: {}\nЗаголовок: {}\nСообщение: {}"\
                .format(request.query_params.get(self.QPARAM_NAME),
                        request.query_params.get(self.QPARAM_EMAIL),
                        request.query_params.get(self.QPARAM_TITLE),
                        request.query_params.get(self.QPARAM_MESSAGE))
            message_html = message.replace("\n", "<br>")

            try:                            # Создать папку сообщений
                os.mkdir(self.PATH_CONTACT_MESSAGES)
            except FileExistsError:         # Если уже существует, ОК
                pass

            try:                            # Записать сообщение в файл с именем в формате YYYY-MM-DDTHH-MM-SS_email
                with open(self.PATH_CONTACT_MESSAGES +
                          datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + "_" +
                          request.query_params.get(self.QPARAM_EMAIL), 'w') as output_file:
                    output_file.write(message)
            except FileNotFoundError:
                return MinimalView(status_code=404,
                                   body="Папка сообщений не найдена - возможно, отсутствуют права доступа.").run()

                                            # Отобразить страницу успеха
            return BaseView(self.HTML_TEMPLATE_SUCCESS, message=message_html, *args, **kwargs).run(request)

        else:                                                   # Неизвестный метод - ошибка
            return MinimalView(status_code=418, body="Неизвестный метод HTTP: {}".format(request.method)).run()


