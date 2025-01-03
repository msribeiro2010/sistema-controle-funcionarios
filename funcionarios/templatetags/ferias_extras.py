from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Retorna um item de um dicionário pela sua chave"""
    if dictionary is None:
        return None
    return dictionary.get(key)
