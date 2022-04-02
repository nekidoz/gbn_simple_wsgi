###28.03.2022 - Lesson 3 homework

1. Complete refactor: created framework in the framework/ directory

2. Added Lesson 3 functionality - template inheritance and inclusion, i.e.:
- Created hierarchical template structure in framework/template/baseview:
    - base_view_template.html - base template with 5 sections: header, footer, left sidebar, right sidebar, and body;
    - 4 include templates for base templates for 4 sections, excluding body
- Created BaseView* classes implementing this functionality in /framework.views.py:
    - BaseViewSection - base view sections enumerator
    - BaseViewTagData - jinja2 tags and template data for base view sections
    - BaseViewLayout - singleton class used to manage layout used by all BaseView-inheriting classes for 
    rendering templates, initialized with the default templates from framework/template/baseview at init,
    with the following public functions:
        - set_template() - set a user jinja2 template for the specified section,
        - render_html_include() - render a jinja2 template as static html include for the specified section.
    - BaseView - class used to render the view.

To use the functionality with the default base view, page body should look like this:

    {% extends base_view_template %}
    {% block baseview_body %}
    <!-- body html without headers and footers -->
    {% endblock %}

Include templates for various sections can be any jinja2 templates without html headers and footers.

Initialization in the main app might look like this:

    # Initialize base view layout manager
    layout = BaseViewLayout()       
    
    # Optionally check for template load errors
    if layout.status_code != 200:   
        print("BaseView layout error: {}: template {} not found".format(layout.status_code, layout.status_message))

    # Render custom template as static html include, clearing default template and passing app urls for render
    layout.render_html_include(BaseViewSection.left_sidebar, "left_sidebar.html", clear_template=True,
                           urls=app.get_clean_urls(for_menu_only=True))

View class using this functionality could look like this:

    class Index(View, Singleton):
    
        # Initialize urls property with the passed array, or with empty array if not yet initialized
        def __init__(self, urls: [Url] = None):
            if urls is not None:
                self.urls = urls
            elif not hasattr(self, 'urls'):
                self.urls = []
    
        def run(self, request: Request, *args, **kwargs) -> Response:
            return BaseView("index_body.html", title="Главная страница", urls=self.urls).run(request)

3. Updated application functionality:
- Made all application pages use BaseView class with 5-section base template. 
- Added navigation menu to the left sidebar of the base view.

###31.03.2022 - Lesson 4 homework

1. FRAMEWORK: Added Persistence (database) functionality in /framework.persistence.py.
The library implements get/set/delete functionality for custom classes.
Custom class should contain an 'id' field identifying each class instance. 
In case id is duplicated, more than one instance can be returned by the the library's data manipulating methods. 
Currently implemented is the JSON storage engine.

    - PersistenceEngineType - enumeration containing implemented storage engine type ids
    - PersistenceEngine - interface with abstract get(), set() and delete() methods for data retrieval/saving/deletion;
    - PersistenceDataConfig - database internal configuration settings class
    - Persistence - facade class implementing 2 methods:
        - register() - to register a class class_to_register to be stored in database of type engine_type 
        with data found at data_source;
        - engine() - to get database engine instance for registered class for_class
    - PersistenceSerializable - interface to be inherited by custom classes to be saved to JSON files;
    - PersistenceJSONCodec - class implementing JSON encoding and decoding for custom (PersistenceSerializable) classes;
    - PersistenceJSON - class implementing JSON data retrieval/saving/deletion, one data type (class) per file 
    (tested only on custom classes), implementing the following methods:
        - get() - get the stored data in a list; 
        if element_id is specified, only the element(s) with the specified id is (are) returned;
        - set() - replaces the element(s) in the stored data with matching id(s) 
        with the scalar element passed to this method, 
        or append the element passed to the method to the stored data if no matching id found;
        - delete() - delete the first stored element with the id matching the element passed to this method, 
        if any match found  
    
The usage model can be like this:

    from framework import PersistenceSerializable, PersistenceEngineType, Persistence
    
    class Category (PersistenceSerializable):   # Some custom class
        id: uuid.UUID
        name: str
        description: str

    categories: [Category] = None
    
    # Initialize persistent storage for the Category class        
    if not Persistence.register(Category, PersistenceEngineType.JSON, 'categories.json'):
        print("Failed to init data sources")
    else:
        categories = Persistence.engine(Category).get()             # load data from JSON
            
        # ... Do something with data
            
        Persistence.engine(Category).set(new_or_modified_category)  # save data to JSON

        # ... Do something else
        
        Persistence.engine(Category).delete(category_to_delete)     # delete an entry

2. FRAMEWORK: Implemented some minor code improvements:

- Made an Interface (abstract class) from View base class in /framework/views;
- Removed redundant code for template loading in BaseView class BaseViewLayout in /framework/views - 
moved it into protected function _load_template();
    
3. APP: Added Lesson 4 homework functionality:
- Created ElementEditView class in element_edit.py/element_edit.html 
implementing basic functionality to create/edit a data instance:
    - 'name' input field processing to edit the respective field of an instance;
    - 'save', 'save new', 'cancel', 'delete' buttons processing;
- Created category.py module to handle education courses categories:
    - Category class holds category data, initializes instance ids and registers the class in Persistence library;
    - Category items can be directly edited using ElementEditView class;
- Created course.py module to deal with education courses:
    - Course class holds course data, initializes instance ids and registers the class in Persistence library;
    - CourseEditView inherits ElementEditView and implements assigning a category to a course;
    - element_edit.html integrates additional controls for course editing using jinja2 processing functionality;
- All the data for courses and categories is managed using Persistence library with JSON storage engine.
- Updated the main application page (Index() view) to show available categories and courses.
 
