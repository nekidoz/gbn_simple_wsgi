import uuid

from framework.persistence import Persistence, PersistenceSerializable
from framework.request import Request
from framework.response import Response

from element_edit import ElementEditView
from category import Category
import settings


class Course(PersistenceSerializable):
    id: uuid.UUID
    name: str
    category_id: uuid.UUID

    def __init__(self, id: uuid.UUID = None, name: str = None, category_id: uuid.UUID = None):
        if id:
            self.id = id
        else:
            self.id = uuid.uuid4()
        self.name = name
        self.category_id = category_id

    # Register Course's Persistence storage
    @staticmethod
    def register() -> bool:
        return Persistence.register_class(Course, settings.COURSES_STORAGE, settings.COURSES_DATA_FILE)


class CourseEditView(ElementEditView):

    # Override run(): load the existing course categories and
    # build a category list, adding an empty category and placing the course's category at the top of the list
    def run(self, request: Request, *args, **kwargs) -> Response:

        # Rebuild the category list, adding an empty category and placing the course's category at the top of the list
        if request.method == "GET":                         # only processing GET
            # Get the categories list - needed anyway by the form
            categories = Persistence.engine(Category).get()
            final_list = []  # final list of categories for the form

            # get the edited course instance and put it's category on top of the categories list
            course_id = request.path_array[len(request.path_array) - 1]
            course = Persistence.engine(Course).get(course_id)
            if course and course != []:                   # if the course instance found

                category_id = course[0].category_id
                if category_id:                             # if the course has a category assigned
                    # search for the course's category in the existing categories
                    category = [category for category in categories if category.id == category_id]
                    if category and category != []:         # if the course's category exists in the list
                        final_list.append(category[0])               # set the course's category as the first in the list
                        categories.remove(category[0])

            # create an empty category and put it on top or next to the course's category
            empty_category = Category(name="")
            empty_category.id = None                        # explicitly clear the id
            final_list.append(empty_category)

            # append the rest of the categories list
            final_list.extend(categories)

            return super().run(request, categories=final_list, *args, **kwargs)
        else:
            return super().run(request, *args, **kwargs)
