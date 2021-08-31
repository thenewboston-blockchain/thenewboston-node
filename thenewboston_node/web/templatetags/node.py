from django import template

from thenewboston_node.business_logic.node import get_node_identifier

register = template.Library()


@register.simple_tag
def node_identifier():
    return get_node_identifier()
