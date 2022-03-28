"""
Чтобы запустить приложение, наберите: gunicorn simple_wsgi:application
"""

from framework.framework import Framework
from framework.views import BaseViewLayout, BaseViewSection
from urls import app_urls
from views import Index
import settings

# Прочие константы
EMAIL_ADMIN = "nekidoz@yandex.ru"

app = Framework(app_urls, use_admin=True)                   # Create application object
index = Index(urls=app.get_clean_urls(for_menu_only=True))  # Initialize the Main (Index) page with menu urls
layout = BaseViewLayout()
if layout.status_code != 200:
    print("BaseView layout error: {}: template {} not found".format(layout.status_code, layout.status_message))
#layout.set_left_sidebar_template(settings.PATH_APP+"left_sidebar.html")
#if layout.status_code != 200:
#    print("BaseView layout error: {}: template {} not found".format(layout.status_code, layout.status_message))
layout.render_html_include(BaseViewSection.left_sidebar, settings.PATH_APP+"left_sidebar.html", clear_template=True,
                           urls=app.get_clean_urls(for_menu_only=True))
