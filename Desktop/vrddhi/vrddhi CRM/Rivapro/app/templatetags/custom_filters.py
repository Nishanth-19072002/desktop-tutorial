from django import template
from app.models import SubModuleVisibility

register = template.Library()

@register.filter
def is_submodule_visible(user, submodule):
    try:
        visibility = SubModuleVisibility.objects.get(user=user, submodule=submodule)
        return visibility.is_visible
    except SubModuleVisibility.DoesNotExist:
        return False


