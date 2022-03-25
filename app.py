"""
Чтобы запустить приложение, наберите: gunicorn simple_wsgi:application
"""

from framework.framework import Framework
from urls import app_urls

# Прочие константы
EMAIL_ADMIN = "nekidoz@yandex.ru"

app = Framework(app_urls, use_admin=True)
