# frontend/templatetags/frontend_custom_filters.py
from django import template
from django.db.models import Q, Sum
import re
from collections import defaultdict
from backend.models import BookedPackage
from django.utils.text import slugify as django_slugify

register = template.Library()


@register.filter
def truncate_chars(value, max_length):
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value


@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='without_label')
def without_label(field):
    return field.as_widget(attrs={'class': 'form-control', 'placeholder': field.label})


@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def title_case(value):
    """
    Converts comma-separated values into title case
    E.g., 'engineMounts,gurneyBubble' to 'EngineMounts, GurneyBubble'
    """
    if not value:
        return ''
    
    # Split the string by commas
    parts = value.split(',')
    
    # Title case each part (convert first letter of each word to uppercase)
    # This handles camelCase by finding capital letters and adding spaces before them
    formatted_parts = []
    for part in parts:
        # Convert first letter to uppercase
        if part:
            # Handle camelCase by keeping existing capital letters
            formatted = part[0].upper() + part[1:]
            formatted_parts.append(formatted)
    
    # Join parts with comma and space
    return ', '.join(formatted_parts)

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divides the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
    
@register.filter
def group_by_build_type(images):
    """Group images by their build_type attribute."""
    grouped = defaultdict(list)
    for image in images:
        grouped[image.build_type].append(image)

    return dict(grouped)
@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key, return empty list if key not found."""
    return dictionary.get(key, [])
@register.filter
def custom_floatformat(value, arg=0):
    """
    Format a number to the specified number of decimal places and optionally append a % sign.
    """
    try:
        value = float(value)
        decimal_places = int(arg)
        # Round to specified decimal places
        formatted_value = f"{value:.{decimal_places}f}"
        # Remove decimals if decimal_places is 0
        if decimal_places == 0:
            formatted_value = str(int(round(value)))
        return formatted_value
    except (ValueError, TypeError):
        return value  # Return unchanged if not a number
    
register.filter
def filter_by_build_type(images, build_type):
    """Filter images by the specified build type."""
    if not build_type:
        return images  # Return all images if no build type is specified
    return [image for image in images if image.build_type == build_type]

register.filter
def get_status_badge_class(status):
    """Return Bootstrap badge class based on status."""
    status_classes = {
        'confirmed': 'bg-success',
        'pending': 'bg-warning',
        'cancelled': 'bg-danger',
        'completed': 'bg-success',
        'in_progress': 'bg-primary',
        'awaiting_payment': 'bg-warning',
    }
    return status_classes.get(status, 'bg-info')

@register.filter
def build_type_label(value):
    return dict(BookedPackage.BUILD_TYPE_CHOICES).get(value, "Unknown")


@register.filter
def is_feature_available(feature, car_model_title):
    if car_model_title == 'Mark I':
        return feature.in_mark_I
    elif car_model_title == 'Mark II':
        return feature.in_mark_II
    elif car_model_title == 'Mark IV':
        return feature.in_mark_IV
    return True

@register.filter
def filter_by_section(features, section):
    return [feature for feature in features if feature.section == section]


@register.filter
def slugify(value):
    return django_slugify(value)

@register.filter
def sum_attr(queryset, attr):
    return queryset.aggregate(total=Sum(attr))['total'] or 0


@register.filter
def map(value, attr):
    """
    Extract the specified attribute from each item in the input list or queryset.
    
    Args:
        value: Iterable (list, queryset, etc.) containing objects.
        attr: String name of the attribute to extract from each object.
    
    Returns:
        List of attribute values.
    """
    try:
        return [getattr(item, attr) for item in value]
    except (AttributeError, TypeError):
        return []