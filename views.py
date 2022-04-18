# REFERENCE DESIGN

from framework.response import Response
from framework.request import Request
from framework.views import View, BaseView, MinimalView
from framework.singleton import Singleton
from framework.persistence import Persistence
from framework.logger import debug, LoggerLevel

import settings
from category import Category
from course import Course
from student import Student


# Main page controller  - SINGLETON! Initialize it with menu urls when Framework is initialized!
#@debug
class Index(View, Singleton):
    HTML_TEMPLATE = settings.TEMPLATES_APP + "/index.html"             # Page template

    #@debug
    def run(self, request: Request, *args, **kwargs) -> Response:
        return BaseView(self.HTML_TEMPLATE,
                        title="Главная страница",
                        categories=Persistence.engine(Category).get(),
                        courses=Persistence.engine(Course).get(),
                        students=Persistence.engine(Student).get(),
                        ).run(request)
