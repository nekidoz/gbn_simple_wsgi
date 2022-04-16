from dataclasses import dataclass

from framework.views import Admin, View404

# To support deferred init, separate the view class reference and init() params dictionary -
# now instantiate the view object after routing, in Framework._get_view()
@dataclass
class Url:
    url: str                #
    viewClass: object
    viewParams: dict
    name: str = ""
    inMenu: bool = False


# Admin interface URLs
admin_urls = [
    Url('/admin/*', Admin, {'admin_root': "admin"}, "Административный интерфейс", True),
    Url('/notfound', View404, {}, "", False),
]
