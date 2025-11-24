from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_env_var(name):
    print(getattr(settings, name, ''))
    return getattr(settings, name, '')