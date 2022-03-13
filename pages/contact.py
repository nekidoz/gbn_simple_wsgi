# Page Controller для формы обратной связи
# Состав:
# - файл contact.html шаблона формы обратной связи в папке page controller'ов
# - файл contact_success.html шаблона сообщения об успехе формы обратной связи в папке page controller'ов
# - папка contact_messages/ для файлов сообщений в папке page controller'ов с правами записи в нее,
#   или права на создание такой папки в папке page controller'ов
# Метод GET отображает форму.
# Метод POST записывает данные формы в папку сообщений в файл с именем в формате YYYY-MM-DDTHH-MM-SS_email.

from datetime import datetime
import os
import sws
from sws import render, htmlWrap

HTML_TEMPLATE_FORM = sws.PATH_PAGE_CONTROLLERS + "contact.html"         # Шаблон формы обратной связи
HTML_TEMPLATE_SUCCESS = sws.PATH_PAGE_CONTROLLERS + "contact_success.html"  # Шаблон страницы успеха
PATH_CONTACT_MESSAGES = sws.PATH_PAGE_CONTROLLERS + "contact_messages/" # Папка для файлов сообщений
QPARAM_NAME = "name"                                                    # Параметры POST с полями сообщения
QPARAM_EMAIL = "email"
QPARAM_TITLE = "title"
QPARAM_MESSAGE = "msg"


def contact(environ, query_dict):
    if environ[sws.ENV_REQ_METHOD] == sws.ENV_REQ_GET:      # GET: отобразить форму обратной связи
        try:
            return sws.HTML_200, render(HTML_TEMPLATE_FORM)
        except FileNotFoundError:
            return sws.HTML_404, htmlWrap("Страница {} не найдена".format(environ[HTML_TEMPLATE]))

    elif environ[sws.ENV_REQ_METHOD] == sws.ENV_REQ_POST:   # POST: обработать данные формы обратной связи
                                        # Сформировать строку сообщения
        message = "Имя: {}\nEmail: {}\nЗаголовок: {}\nСообщение: {}"\
            .format(query_dict.get(QPARAM_NAME),
                    query_dict.get(QPARAM_EMAIL),
                    query_dict.get(QPARAM_TITLE),
                    query_dict.get(QPARAM_MESSAGE))
        message_html = message.replace("\n", "<br>")

        try:                            # Создать папку сообщений
            os.mkdir(PATH_CONTACT_MESSAGES)
        except FileExistsError:         # Если уже существует, ОК
            pass

        try:                            # Записать сообщение в файл с именем в формате YYYY-MM-DDTHH-MM-SS_email
            with open(PATH_CONTACT_MESSAGES +
                      datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + "_" +
                      query_dict.get(QPARAM_EMAIL), 'w') as output_file:
                output_file.write(message)
        except FileNotFoundError:
            return sws.HTML_404, htmlWrap("Папка сообщений не найдена - возможно, отсутствуют права доступа.")

        try:                            # Отобразить страницу успеха
            return sws.HTML_200, render(HTML_TEMPLATE_SUCCESS, message=message_html)
        except FileNotFoundError:
            return sws.HTML_404, htmlWrap("Страница {} не найдена".format(environ[HTML_TEMPLATE]))

    else:                                                   # Неизвестный метод - ошибка
        return sws.HTML_418, htmlWrap("Неизвестный метод HTTP: {}".format(environ[sws.ENV_REQ_METHOD]))
