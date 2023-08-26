from django import template

register = template.Library()


@register.filter()
def first_available_image(images):
    for img in images:
        if img.image:
            return img
    return None
