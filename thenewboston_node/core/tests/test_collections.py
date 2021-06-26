from thenewboston_node.core.utils.collections import replace_keys


def test_replace_keys():
    replace_map = {
        'long_a': 'a',
        'long_b': 'b',
        'long_c': 'c',
        'long_d': 'd',
        'long_e': 'e',
        'long_f': 'f',
    }
    assert replace_keys({'long_a': 1}, replace_map) == {'a': 1}
    assert replace_keys([{'long_a': 1}], replace_map) == [{'a': 1}]
    assert replace_keys({'long_a': 1, 'long_b': 2}, replace_map) == {'a': 1, 'b': 2}
    assert replace_keys({
        'long_a': 1,
        'long_b': 2,
        'long_c': [1, 2, 3]
    }, replace_map) == {
        'a': 1,
        'b': 2,
        'c': [1, 2, 3]
    }
    assert replace_keys({
        'long_a': {
            'long_c': 1
        },
        'long_b': 2,
        'long_c': [1, 2, 3]
    }, replace_map) == {
        'a': {
            'c': 1
        },
        'b': 2,
        'c': [1, 2, 3]
    }
    assert replace_keys({
        'long_a': {
            'long_c': 1
        },
        'long_b': 2,
        'long_c': [{
            'long_d': 4
        }, 2, 3]
    }, replace_map) == {
        'a': {
            'c': 1
        },
        'b': 2,
        'c': [{
            'd': 4
        }, 2, 3]
    }
    assert replace_keys({
        'long_a': {
            'long_c': [1, 5, 6]
        },
        'long_b': 2,
        'long_c': [{
            'long_d': [1, 2, 3]
        }, 2, 3]
    }, replace_map) == {
        'a': {
            'c': [1, 5, 6]
        },
        'b': 2,
        'c': [{
            'd': [1, 2, 3]
        }, 2, 3]
    }
