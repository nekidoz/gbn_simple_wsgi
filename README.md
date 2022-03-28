# Framework - простой фреймворк на Python
##  с примером его использования.

Чтобы запустить приложение, наберите: gunicorn app:app

Состав фреймворка (папка framework/):
templates/ - папка с html-файлами фреймворка, в т.ч. страницей 404 и админки
templates/baseview - папка с html-файлами класса BaseView (см. CHANGES.md от 28.03.2022)
framework.py - класс Framework, чей объект вызывается как приложение gunicorn, а в init() передаются url приложения;
               он получает параметры запроса, маршрутизирует его в требуемый вью и возмращает результат его работы;
               маршрутизация взможна как по полному url, так и по wildcard (например, /someurl/*)
request.py - класс Request, чей объект содержит параметры переданного wsgi сервером окружения
response.py - класс Response, чей объект содержит результаты работы вью
settings.py - некоторые константы общего пользования, которые не удалось распихать по классам
urls.py - класс Url для хранения информации для маршрутизации и объект urls с url админки
views.py - класс View для всех вью проекта, а также некоторые служебные вью:
    - Minimal - для отображения информации без использования темплейтов на файловой системе с минимальными заголовками
    - Render - для отображения параметризованных шаблонов из файлов с использованием jinja2
    - View404 - для отображения дефолтной страницы кода 404
    - Admin - вью админки, отображающее параметры из окружения wsgi
              и дающее возможность тестирования запросов get и 
    классы иерархических темплейтов BaseView (см. CHANGES.md от 28.03.2022):
    - BaseViewSection - base view sections enumerator
    - BaseViewTagData - jinja2 tags and template data for base view sections
    - BaseViewLayout - singleton class used to manage layout used by all BaseView-inheriting classes for 
    rendering templates, initialized with the default templates from framework/template/baseview at init,
    with the following public functions:
        - set_template() - set a user jinja2 template for the specified section,
        - render_html_include() - render a jinja2 template as static html include for the specified section.
    - BaseView - class used to render the view.
    В CHANGES.md от 28.03.2022 даны примеры использования BaseView.


Состав типового приложения (корневая папка проекта):
app.py - основной файл, где создается объект Framework и который используется для запуска приложения
settings.py - некоторые константы общего пользования, которые не удалось распихать по классам;
              в частности, содержит путь к папке файлов html приложения
urls.py - объект app_urls с url приложения
views.py - вью приложения; реализованы:
    - Index - вью главной страницы
    - Contact - вью для сообщений пользователя; файлы сообщений сохраняются в папке app/contact_messages
    (см. CHANGES.md от 28.03.2022)
    Эти вью используют систему иерархических темплейтов, реализованных классом BaseView.
    
Список страниц приложения:
/ - вью главной страницы
/contact - вью Contact
/admin - админка (из фреймворка)
