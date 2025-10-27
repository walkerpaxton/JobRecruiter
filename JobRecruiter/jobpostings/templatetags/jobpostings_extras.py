# In jobpostings/templatetags/jobpostings_extras.py
from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(dictionary, key):
    """
    Allows dictionary lookups using a variable key in Django templates.
    Usage: {{ my_dictionary|lookup:my_key }}
    """
    # Ensure key exists before accessing 'applications'
    data = dictionary.get(key)
    if data is None:
        # Return something that won't break length filter or loops
        return {'applications': []}
    return data

# Add any other custom filters or tags you might have here