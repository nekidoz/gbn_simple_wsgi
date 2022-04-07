# REFERENCE STRUCTURE
from framework.urls import Url

from views import Index, Contact
from element_edit import ElementEditView
from category import Category
from course import Course, CourseEditView


import settings

app_urls = [
    Url('/', Index, {}, "Главная страница", True),
    Url('/category/edit/*', ElementEditView, {'element_class': Category,
                                              'element_html_class_name': "Category",
                                              'html_template_form': settings.PATH_APP + "element_edit.html"},
        "Категории курсов", False),
    Url('/course/edit/*', CourseEditView, {'element_class': Course,
                                           'element_html_class_name': "Course",
                                           'html_template_form': settings.PATH_APP + "element_edit.html"},
        "Курсы", False),
    Url('/contact', Contact, {}, "Обратная связь", True)
]
