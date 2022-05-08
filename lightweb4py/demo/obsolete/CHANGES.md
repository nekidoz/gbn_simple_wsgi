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

###02.04.2022 - Lesson 4 homework

1. IMPORTANT!! FOR THE LATEST RELEASE SEE changes as of 14.04.2022
FRAMEWORK: Added Persistence (database) functionality in /framework/persistence.py.
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
 
##05.04.2022 - Lesson 5 homework

1. FRAMEWORK: Added Logger functionality in /framework/logger.py.
The library implements logging functionality which is a subset of Python logger, i.e.:
- LoggerHandlers that implement formatting and saving log messages to specific media - files, console.
File and Console handlers are currently implemented. 
- Loggers the implement dispatching log messages to their assigned LoggerHandlers.
- Log objects that store default configuration for logging - Logger reference, logging level, message source - 
to minimize the coding effort.  
- Individual loggers and handlers can be turned on and off, 
can assign default logging level to messages with no logging level specified, 
and can be filtering messages by logging level.
- The following classes and objects are defined:

    - LoggerLevel - Logger levels enumeration class
    - LOGGER_DEFAULT_LEVEL - Default logger level for the logging system
    - LoggerHandler - Abstract class implementing logger handler skeleton. 
    Logger handler has similar function to that of the Python standard library:
    it implements formatting and writing log message to specific media and is called by Logger to do the job.
    This abstract class implements:
        - init() - turning handler on and off,
        setup of the minimum logging level for handler and default logging level for messages,
        - compose_message() - composing log message string,
        - validate_message() - deciding whether to write a log entry depending on the state of handler 
        and message level.
    - LoggerConsoleHandler - Concrete class of console logger handler. Implements actual writing to the console.
    - LoggerFileHandler - Concrete class of file logger handler. Implements actual writing to a file.
    - Logger - The Logger class dispatches log requests to the logger handlers configured for this logger instance.
    The following functions are implemented:
        - __init__() - initializes the logger by storing its handlers and default properties
        - log() - check if should log the message by checking whether the logger is on and
        message logging level is not below the minimum logger logging level,
        then call all the handlers to actually log the message
    - Log - This class should be actually called by any app to reference a logger and then log a message.
    The following functions are implemented:
        - __init__() - sets the actual logger, default logging level and message source reference
        for subsequent calls to the Log instance object
        - __call__() - logs the message (calls a logger instance) filling in omitted parameters
    - LoggerFabric - Use this class to initialize the logging subsystem:
    turn in on and off, set handlers and loggers and the default message level

A typical file to configure the logging subsystem can look like the following.
It configures three log handlers - console, debug file and runtime file - 
and two loggers - debug and runtime - both logging to a file and the console. 

    handlers = {
        'console': {
            'handler': 'LoggerConsoleHandler',
            'level': 0,
            'default_level': 0,
            'is_on': True,
        },
        'debug_file': {
            'handler': 'LoggerFileHandler',
            'file_name': 'debug.log',
            'level': 0,
            'default_level': 0,
            'is_on': True,
        },
        'app_file': {
            'handler': 'LoggerFileHandler',
            'file_name': 'app.log',
            'level': 0,
            'default_level': 0,
            'is_on': True,
        },
    }
    
    loggers = {
        'debug': {
            'logger': 'Logger',
            'handlers': ['console', 'debug_file'],
            'level': 0,
            'default_level': 0,
            'is_on': True,
        },
        'runtime': {
            'logger': 'Logger',
            'handlers': ['console', 'app_file'],
            'level': 0,
            'default_level': 0,
            'is_on': True,
        },
    }

The typical usage of the subsystem can look like the following:

    # Initialize the logging subsystem
    logger = LoggerFabric(handlers=handlers, loggers=loggers)
    
    # Initialize two loggers 
    log_d = Log(settings.LOGGER_DEBUG, LoggerLevel.DEBUG, 'app')
    log_r = Log(settings.LOGGER_RUNTIME, LoggerLevel.INFO, 'app')
    
    Log the messages
    log_d("Test debug message")
    log_r("Test runtime message")

The output of the commands above can look like this:

    2022-04-04T23:49:35.893175, 0, app, Test debug message
    2022-04-04T23:49:35.893541, 1, app, Test runtime message

There first message will also be output to the debug.log file,
and the second - to the app.log file.

2. APP: Added file logs.py with the default logger configuration and logger init commands to app.py.

##07.04.2022 - Lesson 6 homework

1. FRAMEWORK: Added @debug function (method) decorator to the Logger library /framework/logger.py 
(Lesson 5 official homework). 
It can also be applied to a class definition.
It prints two log messages with the function name: before and after running the function code. 
It can be used with or without parameters:

        # Log to the default logger (see LoggerFactory class initializer parameters below) and default level
        @debug
        class Index:

        # Log to the specified logger and/or with the specified level (both parameters being optional)
        @debug(logger='runtime', level=LoggerLevel.INFO)
        class Contact:

- Output of the decorator could look like the following. 
Logger name field has been added after the debug level field.

        2022-04-06T23:04:34.331026, DEBUG, debug, Index, Execution started
        2022-04-06T23:04:34.331419, DEBUG, debug, Index, Execution finished
        2022-04-06T23:04:47.546540, INFO, runtime, Contact, Execution started
        2022-04-06T23:04:47.546912, INFO, runtime, Contact, Execution finished

- Added default_logger parameter to the LoggerFactory class initializer, 
e.g. for use with the @debug decorator (see above):

        logger = LoggerFabric(handlers=handlers, loggers=loggers, default_logger=settings.LOGGER_DEBUG)

To show the functionality, added @debug headers to the Contact() and Index() views of the app in views.py.

2. FRAMEWORK: added @url class decorator to the Framework module /framework/framework.py
(Lesson 5 official homework).
It is applied to a view class, not a method, because we do not initialize views 
until their instances are created for display. So we actually need to pass the whole class to the routing function
for it to first call __init__() method to initialize the view ans then call its run() method to render its content.

To make the functionality work, modified the Framework class to be Singleton and made some other minor changes 
to the way the view structure is initialized and used in the Framework class.

To show the functionality, added a @url header to the Contact() view of the app in views.py.

3. FRAMEWORK: Class-Based Views (CBV)

(CHANGED on 16.04.2022, please see changes)
The CBV concept and Mixin usage possibility has been implemented in the framework since 28.03.2022 
(see 28.03.2022 - Lesson 3 homework).
Its implementation description is provided here for convenience because implementing it was the homework for today. 

- All views are implemented as subclasses of the View class (/framework/views.py). 
    - Every view should implement the run() method called by the framework to render the view. 
    A Request instance of the current WSGI request is passed to the method, 
    and it should return a Response object to the framework:
    
            def run(self, request: Request, *args, **kwargs) -> Response:
                pass
   
    - Any view can implement the __init__() method to accept parameters, 
    or/and implement the __new__() method, e.g. to make the class conform to singleton architecture. 
    The default View has no __init__() or other initially called methods. 
    - Any view can inherit other classes (multiple inheritance).
    - View is instantiated each time it is called, right before calling its run() method. 
    To make its data persistent or to perform pre- or post-initialization tasks on the view class, 
    you can make it a singleton, for example, add the Singleton class to the list of the view's base classes.
    
- The app's view structure should be configured in the Url (/framework/urls.py) array 
and is supposed to be placed in the app's urls.py file. 
Each Url entry should have the following fields:
    - URL of the view page, starting with a backslash and without a backslash at the end (if not root url);
    - type reference (class name) of the class implementing the target view;
    - dictionary of parameters to pass to the class initializer when its object is instantiated (can be empty dict);
    - (optional) name of the view for the app's navigation menu;
    - (optional) flag indicating whether this item should appear in the app's navigation menu 
    (returned by the Framework().get_clean_urls(for_menu_only=True) method)
    
Following is the example structure of the file:

        from framework.urls import Url
        
        from views import Index, Contact
        from element_edit import ElementEditView
        from category import Category
        from course import Course, CourseEditView
        
        
        import settings
        
        app_urls = [
            Url('/', Index, {}, "Главная страница", True),
            Url('/course/edit/*', CourseEditView, {'element_class': Course,
                                                   'element_html_class_name': "Course",
                                                   'html_template_form': settings.PATH_APP + "element_edit.html"},
                "Курсы", False),
            Url('/contact', Contact, {}, "Обратная связь", True)
        ]

- The @url (/framework/framework.py) decorator can be used on any view's class instead of configuring urls in the file 
(see this changes section above).
- There is an advanced view base class BaseView (/framework/views.py) subclassing the View class 
(see 28.03.2022 - Lesson 3 homework). It can be used for displaying a segmented class-based view 
with headers/footers and sidebars. It can be further subclassed or called directly.

4. APP: Class-Based Views (CBV)

(CHANGED on 16.04.2022, please see changes)
The CBV concept and Mixins were used in the app since 28.03.2022 (see 28.03.2022 - Lesson 3 homework).
The brief description of the classes is provided here for convenience 
because implementing it was the homework for today. 

- All the app's view classes use the framework's BaseView class to render pages. 
They do not subclass the BaseView class (see 28.03.2022 - Lesson 3 homework).
- The ElementEditView (element_edit.py) class subclasses the framework's View class 
and implements basic editing capabilities for a database record form having a 'name' field. 
It uses the framework's BaseView class to render the page (see 02.04.2022 - Lesson 4 homework).
It is used directly to edit categories (category.py). 
- The CourseEditView (course.py) class subclasses ElementEditView and implements additional fields editing 
to edit course records.
- The app uses urls.py config file as well as the @url decorator to configure its urls.

##14.04.2022 - Lesson 7 Homework

1. (FIRST INTRODUCED ON 02.04.2022)
FRAMEWORK: Modified Persistence (database) functionality in /framework/persistence.py.
The library implements get/set/delete functionality for custom classes.
Custom class should contain an 'id' field identifying each class instance. 
In case id is duplicated, more than one instance can be returned by the the library's data manipulating methods. 
Currently implemented are the JSON storage engine.
On 14.04.2022:
- SQLite (sqlite3) support was added as external class PersistenceSQLite in framework/persistence_sqlite.py.
- PersistenceEngineType enumeration was eliminated and engine type was made a string literal to make it possible to add 
other storage engines support without modifying /framework/persistence.py framework module.
- Persistence class was modified to store the list of storage engines as well as classes:
    - register() method was renamed to register_class() to register classes,
    - register_engine() method was added to register engines external to the Framework.
- in PersistenceEngine class and subclasses, the delete() method parameter changed to the id of the element to delete.

Following is the list of classes and constants in /framework/persistence.py:

- ENGINE_JSON - string literal for JSON engine type
- Persistence - facade class implementing 3 methods:
    - register_engine() - (added 14.04.2022) to register an engine engine_type with class engine_initializer,
    - register_class() - (renamed 14.04.2022) to register a class class_to_register to be stored 
    in database of type engine_type with data found at data_source;
    - engine() - to get database engine instance for registered class for_class
- PersistenceEngine - interface with abstract __init()__, get(), set() and delete() methods 
for engine initialization and data retrieval/saving/deletion;
- PersistenceDataConfig - database internal configuration settings class
- PersistenceSerializable - interface to be inherited by custom classes to be saved to JSON files;
- PersistenceJSONCodec - class implementing JSON encoding and decoding for custom (PersistenceSerializable) classes;
- PersistenceJSON - class implementing JSON data retrieval/saving/deletion, one data type (class) per file 
(tested only on custom classes), automatically registered in the Persistence class, implementing the following methods:
    - get() - get the stored data in a list; 
    if element_id is specified, only the element(s) with the specified id is (are) returned;
    - set() - replaces the element(s) in the stored data with matching id(s) 
    with the scalar element passed to this method, 
    or append the element passed to the method to the stored data if no matching id found;
    - delete() - delete the first stored element with the id matching the one passed to this method, 
    if any match found (parameter changed to the element id on 14.04.2022)

Following is the list of classes and constants in /framework/persistence.py (added 14.04.2022):

- PersistenceSQLite - class implementing SQLite (sqlite3) data retrieval/saving/deletion with the same functionality
as the PersistenceJSON class above.
NOTE that this class is NOT automatically registered with the Persistence class and needs to be MANUALLY registered
(see usage example below).

The usage model can be like this:

    from framework.persistence import PersistenceSerializable, Persistence, ENGINE_JSON
    from framework.persistence_sqlite import PersistenceSQLite

    class Course(PersistenceSerializable):      # Some custom class
        id: uuid.UUID
        name: str
        description: str

    class Category(PersistenceSerializable):    # Some other custom class
        id: uuid.UUID
        name: str
        description: str

    courses: [Course] = None
    categories: [Category] = None
    
    # Register SQLite engine and initialize persistent storage for the Category and Course classes        
    if not (PersistenceSQLite.register() and                                  
            Persistence.register(Category, ENGINE_JSON, 'categories.json') and
            Persistence.register(Course, ENGINE_SQLITE, 'database.sqlite')):
        print("Failed to init data sources")
    else:
        categories = Persistence.engine(Category).get()             # load data from JSON
        categories = Persistence.engine(Course).get()               # load data from SQLite
            
        # ... Do something with data
            
        Persistence.engine(Category).set(new_or_modified_category)  # save data to JSON
        Persistence.engine(Course).set(new_or_modified_course   )   # save data to SQLite

        # ... Do something else
        
        Persistence.engine(Category).delete(category_id_to_delete)  # delete an entry
        Persistence.engine(Course).delete(course_id_to_delete)      # delete an entry

##16.04.2022 - Lesson 8 Homework

This release implements functionality not implemented in Lesson 6 Homework: 
- creating a student record,
- displaying the list of students,
- assigning students to courses.

1. FRAMEWORK: (!IMPORTANT!) Changed template file naming conventions after 
adopting Environment and Loader objects of Jinja2 framework 
to improve predictability of nested templates loading behaviour:
- created Environ singleton class in framework/settings.py that initializes Jinja2 Environment 
and assigns PrefixLoader loader to distinguish between the Framework and the App templates.
    - "fw" file path prefix represents framework templates root directory, and
    - "app" - the app templates root.

    All the pathnames of templates should now be specified relative to this prefixes.
    The app template root can be specified at the Environ class init.
    Its intended usage looks as follows:
    
        env = Environ('appfolder/templates/')        # Create environment object at app startup and init template root
        ...
        # Load the template appfolder/templates/sometemplate.html and render it
        result = Environ().jinja_env.get_template('app/sometemplate.html').render(**kwargs)
        
2. APP: Added Student class (student.py) to register students and assign them to Courses.
To accomplish that, reworked the ElementEditView class to make it a modular form for editing any types of data objects. 

- The ElementEditView (element_edit.py) class subclasses the framework's View class 
and implements basic editing (add/copy/modify/delete) capabilities for a database record form. 
It uses the framework's BaseView class to render the page (see 02.04.2022 - Lesson 4 homework).
It is used directly to edit Category records (category.py). 
- The CourseEditView (course.py) class subclasses ElementEditView and implements fetching additional fields 
to edit Course records.
- The StudentEditView (student.py) class subclasses ElementEditView and implements fetching additional fields 
to edit Student records.
- The app uses urls.py config file as well as the @url decorator to configure its urls. 
The configuration now looks as follows:

        app_urls = [
            Url('/', Index, {}, "Главная страница", True),
            Url('/course/edit/*', CourseEditView,
                {'element_class': Course,
                 'element_html_class_name': "Course",
                 'element_title': "Учебный курс",
                 'html_template_form': settings.TEMPLATES_APP + "/element_edit.html",
                 'editor_field_template_names': (settings.TEMPLATES_APP + "/element_edit_name_field.html",
                                                 settings.TEMPLATES_APP + "/element_edit_category_field.html", ),
                 },
                "Курсы", False),
]

The editor_field_template_names dictionary entry contains a tuple of field templates 
that are loaded and concatenated in the specified sequence and then included into the editor_fields section
of the template specified in the html_template_form dictionary entry. 
Now the element_edit.html template implements the ElementEditView class's main template 
with the following on-demand field editing templates used for editing Category, Class and Student records:
- element_edit_category_field.html - category selection drop-down list box returning category_id,
- element_edit_course_field.html - course selection drop-down list box returning course_id,
- element_edit_name_field.html - general text field returning name,
- element_edit_person_fields.html - first_name, middle_name and last_name general text fields 
returning respective values.

To ease a list choice field creation in web forms, 
build_choice_list() function was added to the new miscellaneous.py library file.
It works with Persistence library and builds a list of categories specified in category_class 
to display in web form's drop-down list boxes. 
It gets the value of item_class.category_id_field with item_class.id = item_id and uses it 
to set the top-most category in the list.
It then puts an empty category and the rest of the categories in the list. 
if the item doesn't have a category, it puts an empty category at the top of the list
and the rest of the categories after it. So the resulting list looks like this:

    [assigned category of the item]
    <blank category (None)>
    <All the other categories>
    
##18.04.2022 - Lesson 9 Homework - Microservices

1. (FIRST INTRODUCED ON 02.04.2022, MODIFIED on 14.04.2022)
FRAMEWORK: Modified Persistence (database) functionality in /framework/persistence.py.
The library implements get/set/delete functionality for custom classes.
Custom class should contain an 'id' field identifying each class instance. 
In case id is duplicated, more than one instance can be returned by the the library's data manipulating methods. 
Currently implemented are the JSON and SQLite (sqlite3) storage engines.

On 18.04.2022:
- implemented append() method in PersistenceEngine class and subclasses which appends an instance record to the database 
without checking its contents; it doesn't load existing records from storage and thus doesn't require an id field 
in the stored class; together the get() and append() methods can be used to store records like e.g. logs and feedback
which usually don't require search optimization and unique record capabilities.
- note that append() is also implemented for JSON text files. 
It doesn't read the entire file but rather appends the new encoded item to its end.
For demo purposes, contact messages are stored in JSON (see notes below).

2. APP: Modified the app's contact page (feedback.py):
- Renamed the Contact class into FeedbackView and placed it in the separate file feedback.py; 
its url remained the same: /contact .
- Created Feedback class in feedback.py for storing feedback (contact messages) in Persistence storage.
- Added FeedbackListView class in feedback.py to display the list of feedback messages, 
top-most message being the latest; assigned it the /feedback url; added respective menu entry. 

3. MICROSERVICE DEMO APP: Implemented Microservice demo app - app_student.py. 
It doesn't use the main app's routines and data - only some of the settings.py constants.
It actually implements the minimum functional web application based on the Framework.
The Contact view is added to the app's url tree using a decorator to minimize configuration 
(the app actually doesn't have any config files).  
Run it with: 

        gunicorn -b 127.0.0.1:8001 app_student:app

    To run it together with the main app, run the main app with: 

        gunicorn [-b 127.0.0.1:8000] app:app

    The demo app implements the Contact class page used previously by the main app as its root (/) page. 
    It gathers user's contact details and their message and saves it to a disk file
    in the app/contact_messages directory. It then makes a POST request to the main app's URL:
    
        http://127.0.0.1:8000/contact
        
    and passes the contact message there for storage as if the main app's own /contact URL were called.
    
    To test the app:
    - run the main app and the demo app;
    - open http://127.0.0.1:8001 and leave a contact message;
    - check the message in the app/contact_messages directory named as <current_datetime>_<user_email>;
    - check the Feedback page of the main app at http://127.0.0.1:8000/feedback 
    to see that the message appeared there at the top of the list.
    