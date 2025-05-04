import json


class Dict(dict):
    def path(self, key, default=None, mode='get'):
        """
        Retrieve or remove a value from a nested dictionary or list.

        Args:
            key (str): The dot-separated key path.
            default: The default value to return if the key is not found.
            mode (str): The operation mode, either 'get' or 'pop'. Defaults to 'get'.

        Returns:
            The value at the specified path, or the default value if not found.
        """
        obj = self
        for i, part in enumerate(parts := key.split('/')):
            try:
                index = int(part)
                is_index = True
            except ValueError:
                is_index = False

            match obj:
                case list() if is_index:
                    try:
                        if mode == 'pop' and i == len(parts) - 1:
                            obj = obj.pop(index)
                        else:
                            obj = obj[index]
                    except IndexError:
                        return default
                case dict() | Dict():
                    if part in obj:
                        if mode == 'pop' and i == len(parts) - 1:
                            obj = obj.pop(part, default)
                        else:
                            obj = obj.get(part, default)
                    else:
                        return default
                case _:
                    return default
        return Dict(obj) if isinstance(obj, dict) else obj

    def get(self, key, *args, **kwargs):
        value = super().get(key, *args, **kwargs)
        return Dict(value) if isinstance(value, dict) else value

    def gets(self, keys, default=None, serialize=False):
        """
        Retrieve values for multiple keys, optionally serializing them to JSON.

        Args:
            keys (iterable): List of keys to retrieve values for.
            default: The default value to return for missing keys.
            serialize (bool): Whether to serialize dicts and lists to JSON.

        Returns:
            list: Values corresponding to the keys, optionally serialized.

        Example:
            >>> my_dict = Dict({'a': {'b': {'c': [1, 2, 3]}}})
            >>> my_dict.gets(['a/b/c/1', 'a/b/c/-1'])
            [2, 3]
        """
        if default is None:
            default = {}
        return [
            json.dumps(val) if serialize and isinstance(val, (dict, list, Dict)) else val
            for k in keys
            for val in [self.path(k, default.get(k), mode='get')]
        ]

    def pops(self, keys, default=None, serialize=False):
        """
        Retrieve and remove values for the specified keys from the dictionary.

        If a key is not found, the default value is returned. If the value is a dictionary or list,
        it will be serialized to JSON if `serialize` is True.

        Args:
            keys (iterable): Keys to retrieve and remove.
            default (any, optional): Default value if key not found. Defaults to None.
            serialize (bool, optional): Whether to serialize dict/list values. Defaults to False.

        Returns:
            list: Values that were popped from the dictionary.

        Example:
            >>> my_dict = Dict({'a': 1, 'b': {'x': 10}, 'c': [1, 2, 3]})
            >>> my_dict.pops(['a', 'b', 'c'])
            [1, '{"x": 10}', '[1, 2, 3]']
            >>> my_dict
            {}
        """
        if default is None:
            default = {}
        return [
            json.dumps(val) if serialize and isinstance(val, (dict, list, Dict)) else val
            for k in keys
            for val in [self.path(k, default.get(k), mode='pop')]
        ]

    def filter(self, keys, default=None, serialize=False):
        return Dict(zip(keys, self.gets(keys, default, serialize)))

    def prints(self, serialize=False):
        for k, v in self.items():
            if serialize and isinstance(v, (dict, list, Dict)):
                v = json.dumps(v)
            print(f'{k}: {v}')

    def __getitem__(self, key):
        value = super().__getitem__(key)
        return Dict(value) if isinstance(value, dict) else value


if __name__ == '__main__':
    obj = Dict({'a': {'b': [1, 2, {'c': 3}]}})
    result = obj.gets(['a/b/2/c', 'a/b/0'])
    print(result)
    print(obj)
