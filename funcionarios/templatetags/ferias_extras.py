from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Retorna um item de um dicionário pela sua chave"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_item(dictionary, key):
    """
    Template filter para acessar um item de um dicionário usando uma chave.
    Uso: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, [])
