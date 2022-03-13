# To add a page controller to the project:
# 1. Import page controller function into this file
# 2. Include URL/page controller function name pair into the urls dictionary;
#    start URL with the root slash
#
# Page controllers are passed control to by function page_controller();
# they should have the following parameters:
# 1. environ - HTTP request parameters, the same as the WSGI application receives;
# 2. query_dict - dictionary of query parameters-value pairs
# they should return the following values which are returned by the app to the WSGI server:
# 1. exitCode - string with request exit code, e.g. '200 OK' or '404 not found'
# 2. response - string with rendered HTTP response
# To signal a error, return an empty response and maybe some code
#
# To envoke a page controller, call the page_controller() function

# Import page controllers
from pages.contact import contact

# Page Controller URLs list
urls = {
    '/contact': 'contact'
}


# Looks up a page controller and pass control to it if found.
# Parameters:
# - url - url to envoke a page controller for*
# - environ - HTTP request environment as passed to the WSGI application
# Returns:
# 1. exitCode - string with request exit code, e.g. '200 OK' or '404 not found', an empty string if not found
# 2. response - string with rendered HTTP response, if any, and empty string if not found
def page_controller(url, environ, query_dict):
    exitCode: str = ""                      # Prepare for worse
    response: str = ""
    if url:                                 # If url passed, get controller name, function and run it
        page_controller_name = urls.get(url)
        if page_controller_name:
            page_controller_func = globals()[page_controller_name]
            exitCode, response = page_controller_func(environ, query_dict)
    return exitCode, response
