from functools import reduce
from typing import Union, List
from unittest import TestCase

def rget(obj: Union[dict, list], path: str, default: any = None) -> any:
    """
    Returns the value of a nested dictionary or list specified by a path.
    Paths are represented as a dot-separated string.
    If the path does not exist, returns the default value or raises a KeyError.
    """
    def _get_item(container, key):
        try:
            if isinstance(container, dict):
                return container[key]
            elif isinstance(container, list):
                if ':' in key:
                    start, end = map(int, key.split(':'))
                    return container[start:end]
                else:
                    return container[int(key)]
            else:
                return default
        except (KeyError, IndexError, ValueError):
            return default

    path_components = path.replace('[', '.').replace(']', '').split('.')
    result = reduce(_get_item, [obj] + path_components)

    return result


class TestRGetFunction(TestCase):

    def test_dict_path_exists(self):
        data = {'a': {'b': {'c': 42}}}
        result = rget(data, 'a.b.c')
        self.assertEqual(result, 42)

    def test_dict_path_does_not_exist_with_default(self):
        data = {'a': {'b': {'c': 42}}}
        result = rget(data, 'x.y.z', default='not found')
        self.assertEqual(result, 'not found')

    def test_list_path_exists(self):
        data = {'a': [{'b': 1}, {'b': 2}, {'b': 3}]}
        result = rget(data, 'a.1.b')
        self.assertEqual(result, 2)

    def test_list_path_slice_exists(self):
        data = {'a': [1, 2, 3, 4, 5]}
        result = rget(data, 'a.1:4')
        self.assertEqual(result, [2, 3, 4])

    def test_list_path_does_not_exist_with_default(self):
        data = {'a': [{'b': 1}, {'b': 2}, {'b': 3}]}
        result = rget(data, 'x.y.z', default='not found')
        self.assertEqual(result, 'not found')
