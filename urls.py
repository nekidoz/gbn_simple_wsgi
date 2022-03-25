# REFERENCE STRUCTURE
from framework.urls import Url
from views import Index, Contact

app_urls = [
    Url('/', Index()),
    Url('/contact', Contact())
]