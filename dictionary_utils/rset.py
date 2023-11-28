from functools import reduce
from typing import Union, List
from unittest import TestCase

def rset(obj: Union[dict, list], path: str, value: any) -> None:
    """
    Sets the value of a nested dictionary or list specified by a path.
    Paths are represented as a dot-separated string.
    If the path does not exist, it creates the necessary dictionaries or lists.
    Supports appending to lists using the 'append' keyword.
    """
    def _set_item(container, key):
        if isinstance(container, dict):
            if key == 'append':
                if not isinstance(container, list):
                    raise TypeError(f"'append' can only be used on lists, not on {type(container).__name__}")
                container.append(value)
                return container  # Alteração aqui
            elif key not in container:
                container[key] = {}
            return container[key]
        elif isinstance(container, list):
            if key == 'append':
                container.append(value)
                return container  # Alteração aqui
            elif ':' in key:
                start, end = map(int, key.split(':'))
                for i in range(len(container), end + 1):
                    container.append({} if i == end else [])
                return container[start:end+1]
            else:
                index = int(key)
                if index >= len(container):
                    container.extend([{}] * (index - len(container) + 1))
                return container[index]

    path_components = path.replace('[', '.').replace(']', '').split('.')
    last_key = path_components[-1]
    container = reduce(_set_item, [obj] + path_components[:-1])

    if isinstance(container, dict) and last_key != 'append':
        container[last_key] = value
    elif isinstance(container, list) and (last_key != 'append' or not path_components[:-1]):
        index = int(last_key) if ':' not in last_key else None
        if index is not None and index < len(container):
            container[index] = value
        elif last_key == 'append' or index == len(container):
            container.append(value)
        else:
            raise IndexError(f"Index {index} is out of range for list of length {len(container)}")


class TestRSetFunction(TestCase):

    def test_dict_path_exists(self):
        data = {'a': {'b': {'c': 42}}}
        rset(data, 'a.b.c', value='updated')
        self.assertEqual(data['a']['b']['c'], 'updated')

    def test_dict_path_does_not_exist(self):
        data = {}
        rset(data, 'x.y.z', value='new_value')
        self.assertEqual(data['x']['y']['z'], 'new_value')

    def test_list_path_exists(self):
        data = {'a': [{'b': 1}, {'b': 2}, {'b': 3}]}
        rset(data, 'a.1.b', value=99)
        self.assertEqual(data['a'][1]['b'], 99)

    def test_list_path_does_not_exist(self):
        data = {'a': [{'b': 1}, {'b': 2}, {'b': 3}]}
        rset(data, 'a.3.b', value=4)
        self.assertEqual(data['a'][3]['b'], 4)

    def test_list_path_slice_does_not_exist(self):
        data = {'a': [1, 2, 3, 4, 5, 50, 60, 70]}
        self.assertEqual(data['a'][5:8], [50, 60, 70])

    def test_list_path_does_not_exist_with_append(self):
        data = {'a': [1, 2, 3]}
        rset(data, 'a.append', value=4)
        self.assertEqual(data['a'], [1, 2, 3, 4])

    def test_list_path_does_not_exist_with_invalid_append(self):
        data = {'a': {'b': {'c': 42}}}
        with self.assertRaises(TypeError):
            rset(data, 'a.append.x', value='invalid_append')

    def test_list_path_does_not_exist_with_index_error(self):
        data = {'a': [1, 2, 3]}
        with self.assertRaises(IndexError):
            rset(data, 'a.5', value=10)
