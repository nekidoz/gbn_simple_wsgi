###28.03.2022

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
 