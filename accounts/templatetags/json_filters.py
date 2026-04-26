from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def json_attr(value):
    """
    Safely encode a Python object as JSON for use in HTML data attributes.
    When used with single quotes in HTML, we escape single quotes in the JSON.
    """
    json_str = json.dumps(value)
    # Escape single quotes for HTML attribute context (since we use single quotes around the attribute)
    escaped = json_str.replace("'", "&#39;")
    return mark_safe(escaped)
