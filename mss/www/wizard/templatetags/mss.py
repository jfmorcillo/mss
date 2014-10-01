from django import template

register = template.Library()

@register.filter
def firstline(string):
    return string.split("\n")[0]


@register.filter(is_safe=True)
def markdown(value, arg=''):
    """
    Runs Markdown over a given value, optionally using various
    extensions python-markdown supports.

    Syntax::

        {{ value|markdown:"extension1_name,extension2_name..." }}

    To enable safe mode, which strips raw HTML and only returns HTML
    generated by actual Markdown syntax, pass "safe" as the first
    extension in the list.

    If the version of Markdown in use does not support extensions,
    they will be silently ignored.

    """
    try:
        import markdown
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in 'markdown' filter: The Python markdown library isn't installed.")
        return force_text(value)
    else:
        markdown_vers = getattr(markdown, "version_info", 0)
        if markdown_vers < (2, 1):
            if settings.DEBUG:
                raise template.TemplateSyntaxError(
                    "Error in 'markdown' filter: Django does not support versions of the Python markdown library < 2.1.")
            return force_text(value)
        else:
            extensions = [e for e in arg.split(",") if e]
            if extensions and extensions[0] == "safe":
                extensions = extensions[1:]
                return mark_safe(markdown.markdown(
                    force_text(value), extensions, safe_mode=True, enable_attributes=False))
            else:
                return mark_safe(markdown.markdown(
                    force_text(value), extensions, safe_mode=False))
