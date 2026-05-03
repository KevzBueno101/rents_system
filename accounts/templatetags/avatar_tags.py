from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def show_avatar(context, profile, size=16, font_size=8):
    request = context.get('request')
    from django.template.loader import render_to_string
    html = render_to_string('partials/avatar.html', {
        'profile': profile,
        'size': size,
        'font_size': font_size,
    }, request=request)
    return mark_safe(html)