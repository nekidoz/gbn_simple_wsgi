from framework.views import View
from framework.request import Request
from framework.response import Response
from framework.persistence import Persistence
from framework.views import MinimalView, BaseView


# PARAMS:
# element_class - class of the element to edit
# element_html_class_name - element class name to pass ti html template
# html_template_form - html form to use as a template
# HTML FORM
# element - the element to hold the data passed from this view to the html template
class ElementEditView(View):

    def __init__(self, element_class, element_html_class_name: str, html_template_form: str):
        self.element_class = element_class
        self.element_html_class_name = element_html_class_name
        self.html_template_form = html_template_form

    def run(self, request: Request, *args, **kwargs) -> Response:
        element_id = request.path_array[len(request.path_array)-1]
        if request.method == "GET":             # GET: отобразить форму редактирования элемента
            # Get the element with the specified id
            element = Persistence.engine(self.element_class).get(element_id)
            # category not found - create
            if not element or (element == []):
                element = [self.element_class()]
                is_new = True
            else:
                is_new = False
            return BaseView(self.html_template_form,
                            element=element[0], element_class = self.element_html_class_name, is_new=is_new,
                            *args, **kwargs).run(request)

        elif request.method == "POST":          # POST: обработать данные формы обратной связи
            # Get button type and delete it to leave only the element properties in the query parameters
            button = request.query_params["button"]
            del request.query_params["button"]
            # Assume all the query parameters in the request are the destination element properties
            if button == "save":
                Persistence.engine(self.element_class).set(self.element_class(id=element_id, **request.query_params))
            elif button == "save_new":
                Persistence.engine(self.element_class).set(self.element_class(**request.query_params))
            elif button == "delete":
                Persistence.engine(self.element_class).delete(self.element_class(id=element_id, **request.query_params))
            else:
                pass
                #pprint("Cancel requested")
            #return MinimalView("OK").run(request)
            return Response(status_code="302 Found", headers={'Location': '/'})
