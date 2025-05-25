# backend/templatetags/custom_filters.py

from django import template

register = template.Library()


@register.filter
def truncate_chars(value, max_length):
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value


@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})