from typing import Self
from .utils import dict_deepupdate


class AttributeDict(dict):
    """
    Converts a dictionary to attributes for convenience of usage. i.e. instead
    of a_dict["root_key"]["node_key"], you can use a_dict.root_key.node_key.

    The input dict is recursively converted to AttributeDict to achieve full
    tree access as attributes.
    """
    # __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__make_self_type(self)

    def __setitem__(self, key, value):
        value = self.__make_self_type(value)
        super().__setitem__(key, value)

    __setattr__ = __setitem__
    __getattr__ = dict.__getitem__

    def __make_self_type(self, source: dict):
        if isinstance(source, dict):
            if not isinstance(source, self.__class__):
                source = self.__class__(source)
            for key, value in source.items():
                if (isinstance(value, dict)
                        and not isinstance(value, self.__class__)):
                    source[key] = self.__class__(value)
        return source

    def copy(self):
        return self.__make_self_type(super().copy())

    def deepupdate(self,  new: Self | dict) -> None:
        new = self.__make_self_type(new)
        dict_deepupdate(self, new)
