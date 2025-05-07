from django import template

register = template.Library()


@register.filter
def verbose_name(obj):
    if hasattr(obj, "_meta"):
        return obj._meta.verbose_name
    return str(obj)


@register.filter
def url_name(model, action):
    app_label = model._meta.app_label
    model_name = model._meta.model_name
    return f"{app_label}:{model_name}-{action}"


@register.filter
def mask(value):
    return "********"


@register.filter(name="add_class")
def add_class(field, css_classes):
    return field.as_widget(attrs={"class": css_classes})
