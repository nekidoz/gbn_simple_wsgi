# REFERENCE DESIGN
from framework.response import Response
from framework.request import Request
from framework.views import View, Render, Minimal

# Imports for Contact class
from datetime import datetime
import os
import settings

# Main page controller
class Index(View):
    HTML_TEMPLATE = settings.PATH_APP + "index.html"             # Page template

    def run(self, request: Request, *args, **kwargs) -> Response:
        return Render(self.HTML_TEMPLATE).run(request)

# Page Controller для формы обратной связи
# Состав:
# - файл contact.html шаблона формы обратной связи в папке page controller'ов
# - файл contact_success.html шаблона сообщения об успехе формы обратной связи в папке page controller'ов
# - папка contact_messages/ для файлов сообщений в папке page controller'ов с правами записи в нее,
#   или права на создание такой папки в папке page controller'ов
# Метод GET отображает форму.
# Метод POST записывает данные формы в папку сообщений в файл с именем в формате YYYY-MM-DDTHH-MM-SS_email.
class Contact(View):

    HTML_TEMPLATE_FORM = settings.PATH_APP + "contact.html"             # Шаблон формы обратной связи
    HTML_TEMPLATE_SUCCESS = settings.PATH_APP + "contact_success.html"  # Шаблон страницы успеха
    PATH_CONTACT_MESSAGES = settings.PATH_APP + "contact_messages/"     # Папка для файлов сообщений
    QPARAM_NAME = "name"                                                # Параметры POST с полями сообщения
    QPARAM_EMAIL = "email"
    QPARAM_TITLE = "title"
    QPARAM_MESSAGE = "msg"

    def run(self, request: Request, *args, **kwargs) -> Response:
        if request.method == "GET":             # GET: отобразить форму обратной связи
            return Render(self.HTML_TEMPLATE_FORM).run(request)

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
                return Minimal(status_code=404,
                               body="Папка сообщений не найдена - возможно, отсутствуют права доступа.").run()

                                            # Отобразить страницу успеха
            return Render(self.HTML_TEMPLATE_SUCCESS, message=message_html).run(request)

        else:                                                   # Неизвестный метод - ошибка
            return Minimal(status_code=418, body="Неизвестный метод HTTP: {}".format(request.method)).run()


