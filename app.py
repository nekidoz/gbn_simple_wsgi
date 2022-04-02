"""
Чтобы запустить приложение, наберите: gunicorn simple_wsgi:application
"""

from pprint import pprint

from framework.framework import Framework
from framework.views import BaseViewLayout, BaseViewSection
from urls import app_urls
from category import Category
from course import Course

import settings

# Прочие константы
EMAIL_ADMIN = "nekidoz@yandex.ru"

app = Framework(app_urls, use_admin=True)                   # Create application object
if not (Category.register() and Course.register()):         # Initialize persistence data
    print("Failed to init data sources")
layout = BaseViewLayout()                                   # Initialize the Base view
if layout.status_code != 200:
    print("BaseView layout error: {}: template {} not found".format(layout.status_code, layout.status_message))
layout.render_html_include(BaseViewSection.left_sidebar, settings.PATH_APP+"left_sidebar.html", clear_template=True,
                           urls=app.get_clean_urls(for_menu_only=True))
