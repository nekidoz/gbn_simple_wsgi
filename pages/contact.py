from Templator import render

HTML_TEMPLATE = "pages/contact.html"

def contact(environ):
    try:
        return "200 OK", render(HTML_TEMPLATE)
    except FileNotFoundError:
        return "404 not found", f"{HTML_TEMPLATE} not found"

