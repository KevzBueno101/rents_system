from django import template

register = template.Library()

@register.inclusion_tag('partials/avatar.html')
def show_avatar(profile, size=16, font_size=8):
    return {
        'profile'   : profile,
        'size'      : size,
        'font_size' : font_size,
    }