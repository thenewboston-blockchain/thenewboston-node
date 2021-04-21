import pytest

from thenewboston_node.core.utils.collections import map_values, replace_keys


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


@pytest.mark.parametrize(
    'source,expected_result', (  # yapf: disable
        (['upper'], ['upper']),
        ({'upper': 'text'}, {'upper': 'TEXT'}),
        ({'outer': [{'upper': 'text'}]}, {'outer': [{'upper': 'TEXT'}]}),
        ({'upper': ['one', 'two']}, {'upper': ['ONE', 'TWO']}),
        ({'outer': {'upper': 'text'}}, {'outer': {'upper': 'TEXT'}}),
        ({'upper': {}}, {'upper': {}}),
        ({'upper': []}, {'upper': []}),
        ({'upper': ()}, {'upper': []}),
        ({'no_upper': None}, {'no_upper': None}),
        ({'no_upper': 'text'}, {'no_upper': 'text'}),
    )  # yapf: enable
)
def test_map_values(source, expected_result):
    replace_map = {
        'upper': str.upper,
    }

    result = map_values(source, replace_map)

    assert result == expected_result


@pytest.mark.parametrize(
    'source,expected_result', (  # yapf: disable
        ({'outer': [{'upper': 'text'}]}, {'outer': [{'UPPER': 'text'}]}),
        ({'outer': [[{'upper': 'text'}]]}, {'outer': [[{'UPPER': 'text'}]]}),
        ({'outer': {'upper': 'text'}}, {'outer': {'UPPER': 'text'}}),
    )  # yapf: enable
)
def test_map_subkeys(source, expected_result):
    replace_map = {
        'outer': str.upper,
    }

    result = map_values(source, replace_map, subkeys=True)

    assert result == expected_result
