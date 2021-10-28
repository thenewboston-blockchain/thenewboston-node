from thenewboston_node.business_logic.models import (
    NodeDeclarationSignedChangeRequestMessage, SignedChangeRequestMessage
)


def test_can_deserialize_from_base_class():
    instance = SignedChangeRequestMessage.deserialize_from_dict({
        'signed_change_request_type': 'nd',
        'node': {
            'network_addresses': ['00ee'],
            'fee_amount': 3,
            'identifier': '00aa'
        }
    })
    assert isinstance(instance, NodeDeclarationSignedChangeRequestMessage)
    assert instance.signed_change_request_type == 'nd'
    assert instance.node.network_addresses == ['00ee']
    assert instance.node.fee_amount == 3
    assert instance.node.identifier == '00aa'


def test_can_deserialize_from_child_class_with_signed_change_request_type():
    instance = NodeDeclarationSignedChangeRequestMessage.deserialize_from_dict({
        'signed_change_request_type': 'nd',
        'node': {
            'network_addresses': ['00ee'],
            'fee_amount': 3,
            'identifier': '00aa'
        }
    })
    assert isinstance(instance, NodeDeclarationSignedChangeRequestMessage)
    assert instance.signed_change_request_type == 'nd'
    assert instance.node.network_addresses == ['00ee']
    assert instance.node.fee_amount == 3
    assert instance.node.identifier == '00aa'


def test_can_deserialize_from_child_class_without_signed_change_request_type():
    instance = NodeDeclarationSignedChangeRequestMessage.deserialize_from_dict({
        'node': {
            'network_addresses': ['00ee'],
            'fee_amount': 3,
            'identifier': '00aa'
        }
    })
    assert isinstance(instance, NodeDeclarationSignedChangeRequestMessage)
    assert instance.signed_change_request_type == 'nd'
    assert instance.node.network_addresses == ['00ee']
    assert instance.node.fee_amount == 3
    assert instance.node.identifier == '00aa'
