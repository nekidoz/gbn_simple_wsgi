# REFERENCE STRUCTURE
from framework.urls import Url

from views import Index, Contact
from element_edit import ElementEditView
from category import Category
from course import Course, CourseEditView

import settings

app_urls = [
    Url('/', Index(), "Главная страница", True),
    Url('/category/edit/*',
        ElementEditView(Category, "Category", settings.PATH_APP + "element_edit.html"), "Категории курсов", False),
    Url('/course/edit/*',
        CourseEditView(Course, "Course", settings.PATH_APP + "element_edit.html"), "Курсы", False),
    Url('/contact', Contact(), "Обратная связь", True)
]
