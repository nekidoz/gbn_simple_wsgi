from dataclasses import dataclass
from framework.views import View, Admin

@dataclass
class Url:
    url: str
    view: View


# Admin interface URLs
admin_urls = [
    Url('/admin/*', Admin())
]
