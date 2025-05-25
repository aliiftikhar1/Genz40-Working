# frontend/templatetags/reservation_tags.py
from django import template
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def has_pending_features(booked_package):
    return booked_package.new_features.filter(status='pending').exists()

@register.simple_tag
def pending_features_total(booked_package):
    total = booked_package.new_features.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    return f"{total:.2f}"