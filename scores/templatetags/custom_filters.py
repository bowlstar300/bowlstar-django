from django import template

register = template.Library()

@register.filter
def to(value):
    """指定した数の範囲で繰り返す"""
    return range(1, int(value) + 1)
