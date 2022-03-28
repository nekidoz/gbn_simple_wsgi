from dataclasses import dataclass
from framework.views import View, Admin

@dataclass
class Url:
    url: str
    view: View
    name: str = ""
    inMenu: bool = False


# Admin interface URLs
admin_urls = [
    Url('/admin/*', Admin(admin_root="admin"), "Административный интерфейс", True)
]
