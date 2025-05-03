import re
from collections import OrderedDict
from collections.abc import Mapping, MutableMapping, Callable
from typing import Any, Hashable, Iterable, Self, TypeAlias


_DictInit: TypeAlias = Mapping | Iterable[tuple[Hashable, Any]]


class GroupDict(MutableMapping, dict):
    """
    This class is a subclass of MutableMapping first, as its update() method
    uses self.__setitem__(), whereas dict.update() does not use self.update().
    dict is kept second so that isinstance(GroupDict(), dict) is True.

    collections.abc.MutableMapping is a subclass of collections.abc.Mapping.
    Examples of collections.abc.MutableMapping are:
     - collections.Counter
     - collections.defaultdict
     - collections.OrderedDict
     - dict

    References:
     - https://realpython.com/python-mappings/
     - https://docs.python.org/3/library/collections.abc.html
    """
    def __init__(self,
                 data: _DictInit,
                 *,
                 grouping: Mapping[str, str] | None = None,
                 recursive: bool = False,
                 ignorecase_get: bool = False,
                 callable_keyiter: Callable | str | None = None,
                 ordered: bool = False,
                 **kwargs):
        """If ordered, use OrderedDict. Since Python 3.7, dictionaries are
        ordered by default, however:
         - {"a": 1, "b": 2} == {"b": 2, "a": 1} is True
         - OrderedDict({"a": 1, "b": 2}) == OrderedDict({"b": 2, "a": 1})
           is False
        """
        super().__init__()
        self.__recursive = recursive
        self.__ignorecase_get = ignorecase_get
        if not (isinstance(callable_keyiter, (Callable, str))
                or callable_keyiter is None):
            raise ValueError("`callable_keyiter` must be callable, or a string"
                             " value that is a string function, e.g. `lower`")
        self.__callable_keyiter = callable_keyiter
        self.__ordered = ordered

        self._store_data = self.__init_dict()
        self._store_grouped_keys = {"": [], "public": []}
        self._store_group = ""

        self.__grouping = dict({} if grouping is None else grouping)

        re_v0, re_v = re.compile("^[^a-zA-Z]"), re.compile("[^a-zA-Z0-9_]")
        group_set = set()
        for prefix, group in self.__grouping.items():
            if not (isinstance(prefix, str) and prefix
                    and isinstance(group, str) and group):
                raise ValueError("`grouping` must have both prefix (key) and"
                                 " name (value) as non-empty strings")
            if re_v0.match(group) or re_v.match(group):
                raise ValueError("`grouping` names (values) must contain only"
                                 " alphabets, numbers and underscore, and start"
                                 " only with an alphabet")
            if group in group_set or group == 'public':
                raise ValueError("`grouping` must contain unique names"
                                 " (values), name `public` is reserved.")
            else:
                self._store_grouped_keys[group] = []
                group_set.add(group)

        self.update(dict(data, **kwargs))

        self._dict_keys_changed = False
        self._iter_idx = None

    # def __contains__(self, item):
    #     """Defines how to determine membership of the mapping.
    #
    #     If this method is not defined, Python uses the .__getitem__() special
    #     method to look for the item.
    #     `in` check; optional method, if not defined, uses __getitem__ method.
    #     - If this method is present, isinstance(obj, Container) is True
    #       automatically.
    #     """
    #     pass

    def __delitem__(self, key):
        """Defines how to delete an item in the mapping.

        Method:
         - Required by collections.abc.MutableMapping
        """
        key_base, key_base_alt, _, _, key_group =\
            self.__base_prefix_key_group(key)

        del self._store_data[key_base_alt]
        self._store_grouped_keys[key_group].remove(key_base_alt)
        self._store_grouped_keys[""].remove(key_base_alt)
        self._dict_keys_changed = True

    # def __eq__(self, other: Self) -> bool:
    #     """Defines how to determine equality of two objects.

    #     If this method is not defined, Python uses __iter__() to iterate
    #     through both objects and compare their values.
    #     """
    #     if isinstance(other, Mapping):
    #         other = self.__new_like_self(data=other)
    #         return self._store_data == other._store_data
    #     else:
    #         return NotImplemented

    def __getattr__(self, item):
        self.__validate_group_name(item)
        if self._store_group == "":
            return self.__new_like_self(
                data={},
                store_data_ow=self._store_data,
                store_grouped_keys_ow=self._store_grouped_keys,
                store_group_ow=item
            )
        else:
            raise AttributeError(f"Select item in `{self.__class__.__name__}`"
                                 f" object before accessing attribute `{item}`")

    def __getitem__(self, item):
        """Defines how to access values using the square brackets notation.

        Method:
         - Required by collections.abc.Mapping
         - Required by collections.abc.MutableMapping
        """
        key_base, key_base_alt, _, _, _ = self.__base_prefix_key_group(item)

        if self.__ignorecase_get:
            data_value = self._store_data[key_base_alt][1]
            if self.__recursive and isinstance(data_value, Mapping):
                value = self.__init_dict()
                for _key, _val in data_value.items():
                    key_base, key_base_alt, _, _, _ =\
                        self.__base_prefix_key_group(_key, "")
                    value[key_base_alt] = (key_base, _val)
            else:
                value = data_value
        else:
            value = self._store_data[key_base]

        if self.__recursive and isinstance(value, Mapping):
            like_self = self.__new_like_self(
                data={},
                store_data_ow=value,
                store_grouped_keys_ow=self.__force_grouped_keys(value),
                store_group_ow="",
            )
            value = like_self
        return value

    def __iter__(self):
        """Defines how to iterate through the mapping.

        Method:
         - Required by collections.abc.Mapping
         - Required by collections.abc.MutableMapping
        """
        self._dict_keys_changed = False
        self._iter_idx = -1
        return self

    def __len__(self):
        """Defines the size of the mapping.

        Method:
         - Required by collections.abc.Mapping
         - Required by collections.abc.MutableMapping
        """
        return len(self._store_grouped_keys[self._store_group])

    # def __ne__(self, other):
    #     """Defines how to determine when two objects are not equal.
    #     """
    #     pass

    def __next__(self) -> str:
        if self._dict_keys_changed:
            raise RuntimeError(f"{self.__class__.__name__} changed keys or size"
                               f" during iteration")
        self._iter_idx += 1
        key_list = self._store_grouped_keys[self._store_group]
        if self._iter_idx >= len(key_list):
            raise StopIteration

        key = key_list[self._iter_idx]
        _, key_base_alt, _, key, _ = self.__base_prefix_key_group(key, "")

        if self.__ignorecase_get:
            key = self._store_data[key_base_alt][0]
            _, _, _, key, _ = self.__base_prefix_key_group(key, "")

        if isinstance(self.__callable_keyiter, Callable):
            key = self.__callable_keyiter(key)
        elif isinstance(self.__callable_keyiter, str):
            key = getattr(key, self.__callable_keyiter)()

        return key

    def __repr__(self) -> str:
        """Produces an output that can be used to re-create the object."""
        repr_data = self.__init_dict()
        for key in self._store_grouped_keys[self._store_group]:
            if self.__ignorecase_get:
                store_data_tuple = self._store_data[key]
                repr_data[store_data_tuple[0]] = store_data_tuple[1]
            else:
                repr_data[key] = self._store_data[key]

        return (f"{self.__class__.__name__}({repr_data},"
                f" grouping={self.__grouping},"
                f" recursive={self.__recursive},"
                f" ignorecase_get={self.__ignorecase_get},"
                f" ordered={self.__ordered})")

    def __setattr__(self, key, value):
        if key == "_store_group":
            setattr(self, "_store_prefix", self.__get_group_prefix(value))
        super().__setattr__(key, value)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Defines how to set a new value for a key.

        Method:
         - Required by collections.abc.MutableMapping
        """
        if self._store_group not in ["", "public"] and not isinstance(key, str):
            raise ValueError("For grouping, only string keys can be used")

        if self.__recursive and isinstance(value, Mapping):
            value = self.__init_dict(value)

        key_base, key_base_alt, _, _, key_group =\
            self.__base_prefix_key_group(key)

        if key_base_alt not in self._store_grouped_keys[key_group]:
            self._store_grouped_keys[key_group].append(key_base_alt)
            self._store_grouped_keys[""].append(key_base_alt)
            self._dict_keys_changed = True

        self._store_data[key_base_alt] = (key_base, value)\
            if self.__ignorecase_get\
            else value

    # def __str__(self):
    #     """Special method to provide a user-friendly string representation."""
    #     return f"{self._store_data}"
    #
    # def clear(self):
    #     """Defines how to remove all the items from the mapping.
    #     """
    #     pass
    #
    # def get(self, key, /):
    #     """Defines an alternative way to access values using keys. This method
    #      allows to set a default value to use if the key isn’t present in the
    #      mapping.
    #      """
    #     pass
    #
    # def items(self):
    #     """Defines how to access the key-value pairs in the mapping.
    #     """
    #     pass
    #
    # def keys(self):
    #     """Defines how to access the keys in the mapping.
    #     """
    #     pass
    #
    # def pop(self, key, /):
    #     """Defines how to remove a key from a mapping and return its value.
    #     """
    #     pass
    #
    # def popitem(self):
    #     """Defines how to remove and return the most recently added item in a
    #      mapping.
    #      """
    #     pass
    #
    # def setdefault(self, key, default=None, /):
    #     """setdefault(): Defines how to add a key with a default value if the
    #     key isn’t already in the mapping.
    #     """
    #     pass
    #
    # def update(self, m, /, **kwargs):
    #     """Defines how to update a dictionary using data passed as an argument
    #     to this method.
    #
    #     dict.update() does not seem to call self.__setitem__(), whereas
    #     MutableMapping.update() does, hence overwriting this method.
    #     """
    #     MutableMapping.update(self, m, **kwargs)
    #
    # def values(self):
    #     """Defines how to access the values in the mapping.
    #     """
    #     pass

    def copy(self):
        data = dict(self._store_data.values()) if self.__ignorecase_get \
            else self._store_data
        return self.__new_like_self(data=data)

    def only(self, group: str | None = None) -> dict:
        if group:
            self.__validate_group_name(group)
            if self._store_group:
                raise ValueError(f"Select item in `{self.__class__.__name__}`"
                                 f" object before calling `only({group})`")
            start_map = self.copy()
        else:
            if self._store_group == "":
                raise ValueError("No group to filter")
            else:
                start_map = self.copy()
                group = self._store_group
                start_map._store_group = ""

        return self._iterate_only(start_map, group)

    def _iterate_only(self, values: Mapping | list | tuple | set, group: str):
        if isinstance(values, Mapping):
            out = {}
            if not isinstance(values, self.__class__):
                values = self.__new_like_self(values)
            values = getattr(values, group)
            for key, value in values.items():
                if isinstance(value, (Mapping, list, tuple, set)):
                    out[key] = self._iterate_only(value, group)
                else:
                    out[key] = value
        else:
            value_type = "tuple" if isinstance(values, tuple) \
                else "set" if isinstance(values, set) \
                else "list"

            if not value_type == "list":
                values = list(values)

            out = []
            for item in values:
                if isinstance(item, (Mapping, list, tuple, set)):
                    out.append(self._iterate_only(item, group))
                else:
                    out.append(item)
            out = tuple(out) if value_type == "tuple" \
                else set(out) if value_type == "set" \
                else out

        return out

    def __base_prefix_key_group(
            self, key: Hashable, ref_group: str | None = None
    ) -> tuple[Hashable, Hashable, str, Hashable, str]:
        if ref_group is None:
            ref_group = self._store_group
        if ref_group in ["", "public"]:
            key_base, key_prefix, key_unprefixed, key_group =\
                key, "", key, "public"
            if isinstance(key, str):
                for prefix, group in self.__grouping.items():
                    if key.startswith(prefix):
                        key_prefix, key_unprefixed, key_group =\
                            prefix, key[len(prefix):], group
                        break
            if ref_group == "public" and not key_group == "public":
                raise ValueError(f"`{key}` invalid for group `public`, use"
                                 f" group `{key_group}` instead")
        else:
            key_unprefixed, key_group = key, ref_group
            for prefix, group in self.__grouping.items():
                if ref_group == group:
                    key_prefix = prefix
                    break
            key_base = f"{key_prefix}{key_unprefixed}"

        key_base_alt = f"{key_prefix}{key_unprefixed.lower()}"\
            if self.__ignorecase_get and isinstance(key_unprefixed, str)\
            else key_base

        return key_base, key_base_alt, key_prefix, key_unprefixed, key_group

    def __force_grouped_keys(self, data: Mapping):
        grouped_keys = {"": [], "public": []}
        for key, _ in data.items():
            _, _, _, _, key_group = self.__base_prefix_key_group(key, "")
            if key_group not in grouped_keys:
                grouped_keys[key_group] = []
            grouped_keys[""].append(key)
            grouped_keys[key_group].append(key)
        return grouped_keys

    def __get_group_prefix(self, group: str) -> str:
        prefix = None
        if group in ["", "public"]:
            prefix = ""
        else:
            for loop_prefix, loop_group in self.__grouping.items():
                if group == loop_group:
                    prefix = loop_prefix
                    break
        if prefix is None:
            raise AttributeError(f"Invalid `grouping` name `{group}`")
        return prefix

    def __init_dict(self, data: _DictInit | None = None) -> dict | OrderedDict:
        if data is None:
            data = {}
        return OrderedDict(data) if self.__ordered else dict(data)

    def __new_like_self(self,
                        data: _DictInit,
                        *,
                        store_data_ow: _DictInit | None = None,  # ow=overwrite
                        store_grouped_keys_ow: dict | None = None,
                        store_group_ow: str | None = None) -> Self:
        like_self = self.__class__(data,
                                   grouping=self.__grouping,
                                   recursive=self.__recursive,
                                   ignorecase_get=self.__ignorecase_get,
                                   callable_keyiter=self.__callable_keyiter,
                                   ordered=self.__ordered)

        if store_data_ow is not None:
            like_self._store_data = store_data_ow
        if store_grouped_keys_ow is not None:
            like_self._store_grouped_keys = store_grouped_keys_ow
        if store_group_ow is not None:
            like_self._store_group = store_group_ow

        return like_self

    def __validate_group_name(self, group: str) -> None:
        if not (group == "public" or group in list(self.__grouping.values())):
            raise ValueError(f"`{self.__class__.__name__}` object has no"
                             f" group `{group}`")
