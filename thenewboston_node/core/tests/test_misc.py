from thenewboston_node.core.utils.misc import humanize_camel_case


def test_humanize_camel_case():
    assert humanize_camel_case('ThisIsACamelCase') == 'This is a camel case'
