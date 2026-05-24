from django import template

from ..gafete_utils import is_item_visible_in_face

register = template.Library()


@register.simple_tag
def gafete_item_visible(face_layout, face, key):
    return is_item_visible_in_face(face_layout, face, key)
