import json


class dict(dict):
    def __init__(self, iterable, **kwargs):
        if isinstance(iterable, list):
            iterable = {str(i): value for i, value in enumerate(iterable)}
        super().__init__(iterable, **kwargs)

    def path(self, key, default=None):
        # nested get
        if '/' in key:
            k1, k2 = key.split('/', 1)
            return dict(self[k1]).path(k2, default) if k1 in self else None
        else:
            return json.dumps(self[key]) if isinstance(self.get(key), (dict, list)) else self.get(key, default)

    def gets(self, keys, default=None):
        # nested gets
        if default is None:
            default = {}
        return [self.path(k, default.get(k)) for k in keys]

    # @property
    # def __class__(self):
    #     return super().__class__()
