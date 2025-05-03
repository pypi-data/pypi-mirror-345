from copy import deepcopy
import re
from collections.abc import Mapping, MutableMapping, Callable
from typing import Any, Hashable, Iterable, Literal, TypeAlias


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
    RE_V0 = re.compile("^[^a-zA-Z]")
    RE_V = re.compile("[^a-zA-Z0-9_]")

    def __init__(self,
                 data: Mapping | MutableMapping | None,
                 *,
                 grouping: Mapping[str, str] | None = None,
                 default_group_name: str | None = "public",
                 key_ignorecase: bool = False):
        super().__init__()
        self.__grouping = dict({} if grouping is None else grouping)
        self.__default_group_name = default_group_name
        self.__key_ignorecase = key_ignorecase

        if data is None:
            self.__data_dict = {}
        elif isinstance(data, Mapping):
            self.__data_dict = data
        else:
            raise ValueError("`data` must be a dict")

        self.__curr_group_name = ""
        self.__curr_group_prefix = ""
        self.__curr_group_type = ""

        self.__saved_grouped_keys = None
        self._set_curr_group_name("")

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
        key_prefixed = self.__process_dict_key(key, "del")
        del self.__data_dict[key_prefixed]

    # def __eq__(self, other: Self) -> bool:
    #     """Defines how to determine equality of two objects.
    #
    #     If this method is not defined, Python uses __iter__() to iterate
    #     through both objects and compare their values.
    #     """
    #     return (isinstance(other, self.__class__)
    #             and self.__data_dict == other.__data_dict)

    def __getattr__(self, group_name):
        self.__exists_group_name(group_name)
        if self.__curr_group_name == "":
            return self.__new_like_self(
                data=self.__data_dict,
                curr_group_name_ow=group_name
            )
        else:
            raise AttributeError(
                f"Select item in `{self.__class__.__name__}` object before"
                f" accessing attribute `{group_name}`"
            )

    def __getitem__(self, item):
        """Defines how to access values using the square brackets notation.

        Method:
         - Required by collections.abc.Mapping
         - Required by collections.abc.MutableMapping
        """
        value = self.__get_item(item)
        if (isinstance(value, Mapping)
                and not isinstance(value, self.__class__)):
            value = self.__class__(value,
                                   grouping=self.__grouping,
                                   default_group_name=self.__default_group_name,
                                   key_ignorecase=self.__key_ignorecase)
        return value

    def __iter__(self):
        """Defines how to iterate through the mapping.

        Method:
         - Required by collections.abc.Mapping
         - Required by collections.abc.MutableMapping
        """
        for key in self.__data_dict:
            if self.__curr_group_name == "":
                yield key
            else:
                _, _, _, key_unprefixed, key_group, _ = self.__decode_key(key)
                if key_group == self.__curr_group_name:
                    yield key_unprefixed
                else:
                    continue

    def __len__(self):
        """Defines the size of the mapping.

        Method:
         - Required by collections.abc.Mapping
         - Required by collections.abc.MutableMapping
        """
        return len(self.__saved_grouped_keys[self.__curr_group_name])

    # def __ne__(self, other):
    #     """Defines how to determine when two objects are not equal.
    #     """
    #     pass

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Defines how to set a new value for a key.

        Method:
         - Required by collections.abc.MutableMapping
        """
        key_prefixed = self.__process_dict_key(key, "set")
        self.__data_dict[key_prefixed] = value

    def __str__(self) -> str:
        #     """Special method to provide a user-friendly string representation."""
        repr_data = {key: value
                     for key, value in self.__items_nonrecursive_class()}
        return f"{repr_data}"

    def __repr__(self) -> str:
        """Produces an output that can be used to re-create the object."""
        repr_data = {key: value
                     for key, value in self.__items_nonrecursive_class()}
        return (f"{self.__class__.__name__}({repr_data},"
                f" grouping={self.__grouping},"
                f" default_group_name={self.__default_group_name},"
                f" key_ignorecase={self.__key_ignorecase})")

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

    def as_dict(self):
        as_dict = {}
        for key, value in self.items():
            as_dict[key] = value.as_dict() \
                if isinstance(value, self.__class__) \
                else value
        return as_dict

    def copy(self):
        return self.__new_like_self(data=deepcopy(self.__data_dict))

    def only(self, group_name: str | None = None) -> dict:
        if group_name:
            self.__exists_group_name(group_name)
            if self.__curr_group_name:
                raise ValueError(f"Select item in `{self.__class__.__name__}`"
                                 f" object before calling `only({group_name})`")
        else:
            if self.__curr_group_name == "":
                raise ValueError("No group to filter")
            else:
                group_name = self.__curr_group_name

        filtered = self.__iterate_only(self.__data_dict, group_name)
        return self.__new_like_self(filtered)

    def _set_curr_group_name(self, group_name: str) -> None:
        self.__key_ignorecase_map = {}
        self.__update_grouping()
        self.__curr_group_name = group_name
        self.__curr_group_prefix, self.__curr_group_type = \
            self.__get_group_metadata(group_name)
        for key in self.__data_dict:
            self.__process_dict_key(key, "init")

    def __decode_key(
            self,
            key: Hashable,
    ) -> tuple[Hashable, Hashable, str, Hashable, str, str]:
        key_prefixed = key
        key_group_name = self.__get_key_group(key_prefixed)
        key_prefix, key_group_type = self.__get_group_metadata(key_group_name)
        key_unprefixed = key_prefixed if key_group_type == "root" \
            else key_prefixed[len(key_prefix):]
        key_prefixed_norm = f"{key_prefix}{key_unprefixed.lower()}" \
            if self.__key_ignorecase and isinstance(key_unprefixed, str) \
            else key_prefixed

        return (key_prefixed,
                key_prefixed_norm,
                key_prefix,
                key_unprefixed,
                key_group_name,
                key_group_type)

    def __encode_key(
            self,
            key: Hashable,
            encode_for_group: str
    ) -> tuple[Hashable, Hashable, str, Hashable, str, str]:
        key_prefix, key_group_type = \
            self.__get_group_metadata(encode_for_group)

        if not (isinstance(key, str)
                or self.__curr_group_name
                in ["", self.__default_group_name]):
            ValueError(
                "A non-string key cannot be set in a base or non-public"
                " group"
            )
        key_unprefixed = key
        key_prefix = self.__curr_group_prefix
        key_group_name = self.__curr_group_name
        key_prefixed = f"{key_prefix}{key_unprefixed}"

        key_prefixed_norm = f"{key_prefix}{key_unprefixed.lower()}" \
            if self.__key_ignorecase and isinstance(key_unprefixed, str) \
            else key_prefixed

        return (key_prefixed,
                key_prefixed_norm,
                key_prefix,
                key_unprefixed,
                key_group_name,
                key_group_type)

    def __exists_group_name(self, group_name: str) -> None:
        if not (group_name == self.__default_group_name
                or group_name in self.__grouping.values()):
            raise AttributeError(
                f"`{self.__class__.__name__}` object has no group"
                f" `{group_name}`"
            )

    def __get_group_metadata(self, group_name: str) -> tuple[str, str]:
        if group_name == "":
            return "", "root"

        if (self.__default_group_name is not None
                and group_name == self.__default_group_name):
            return "", "default"

        for group_prefix, group_name_ in self.__grouping.items():
            if group_name == group_name_:
                return group_prefix, "named"

        raise ValueError(f"Unknown `group_name` ({group_name}) ")

    def __get_item(self, key):
        key_prefixed, key_prefixed_norm, key_group = self.__rebase_key(key)
        if self.__key_ignorecase:
            key_prefixed = self.__key_ignorecase_map[key_prefixed_norm]

        if key_prefixed in self.__data_dict:
            return self.__data_dict[key_prefixed]
        else:
            print("fucked")
            raise KeyError(key)

    def __get_key_group(self, key: Hashable) -> str:
        if isinstance(key, str):
            for group_prefix, group_name in self.__grouping.items():
                if key.startswith(group_prefix):
                    return group_name
            if self.__default_group_name is not None:
                return self.__default_group_name
        return ""

    def __items_nonrecursive_class(self):
        for key in self.keys():
            yield key, self.__get_item(key)

    def __iterate_only(self, in_: Any, group_name: str):
        if isinstance(in_, Mapping):
            data_gd = self.__new_like_self(data=in_)
            data_gd._set_curr_group_name(group_name)
            out = {}
            for key, value in data_gd.__items_nonrecursive_class():
                out[key] = self.__iterate_only(value, group_name)
            return out
        return in_

    def __new_like_self(self,
                        data: Mapping | MutableMapping | None,
                        curr_group_name_ow: str | None = None):
        like = self.__class__(data,
                              grouping=self.__grouping,
                              default_group_name=self.__default_group_name,
                              key_ignorecase=self.__key_ignorecase)
        if curr_group_name_ow is not None:
            like._set_curr_group_name(curr_group_name_ow)
        return like

    def __process_dict_key(
            self,
            key: Hashable,
            stage: Literal["del", "init", "set"]
    ) -> Hashable:
        """
        Update internal saved group keys if new key is set or an existing key
        is deleted.
        """
        if stage == "del":
            key_prefixed, key_prefixed_norm, key_group = self.__rebase_key(key)
            if not key_group == "":
                self.__saved_grouped_keys[key_group].remove(key_prefixed_norm)
            self.__saved_grouped_keys[""].remove(key_prefixed_norm)
            if self.__key_ignorecase:
                del self.__key_ignorecase_map[key_prefixed_norm]
        elif stage == "init":
            key_prefixed, key_prefixed_norm, _, _, key_group, _ = \
                self.__decode_key(key)
            if not key_group == "":
                self.__saved_grouped_keys[key_group].append(key_prefixed_norm)
            self.__saved_grouped_keys[""].append(key_prefixed_norm)
            if self.__key_ignorecase:
                self.__key_ignorecase_map[key_prefixed_norm] = key_prefixed
        else:
            key_prefixed, key_prefixed_norm, key_group = self.__rebase_key(key)
            if key_prefixed_norm not in self.__saved_grouped_keys[""]:
                if not key_group == "":
                    self.__saved_grouped_keys[key_group] \
                        .append(key_prefixed_norm)
                self.__saved_grouped_keys[""].append(key_prefixed_norm)
            if self.__key_ignorecase:
                self.__key_ignorecase_map[key_prefixed_norm] = key_prefixed

        return key_prefixed

    def __rebase_key(
            self, key: Hashable
    ) -> tuple[Hashable, Hashable, str]:
        key_prefixed, key_prefixed_norm, _, _, key_group, key_group_type = \
            self.__decode_key(key)

        if (key_group_type == "default"
                and self.__curr_group_name in self.__grouping.values()):
            key_prefixed, key_prefixed_norm, _, _, key_group, _ = \
                self.__encode_key(key, self.__curr_group_name)

        return key_prefixed, key_prefixed_norm, key_group

    def __update_grouping(self):
        self.__saved_grouped_keys = {"": []}

        for group_prefix, group_name in self.__grouping.items():
            if not (isinstance(group_prefix, str) and group_prefix):
                raise ValueError(
                    "`grouping` must have prefix (key) as a non-empty string"
                )
            self.__validate_group_name(group_name)
            self.__saved_grouped_keys[group_name] = []

        if self.__default_group_name is not None:
            self.__validate_group_name(self.__default_group_name)
            self.__saved_grouped_keys[self.__default_group_name] = []

    def __validate_group_name(self, group_name: str):
        if not (isinstance(group_name, str) and group_name):
            raise ValueError(
                "`grouping` must have name (value) as a non-empty string"
            )
        if self.RE_V0.match(group_name) or self.RE_V.match(group_name):
            raise ValueError(
                "`grouping` names (values) must contain only  alphabets,"
                " numbers and underscore, and start only with an alphabet"
            )
        if group_name in self.__saved_grouped_keys:
            raise ValueError(
                f"`grouping` must contain unique names (values) including"
                f" public group name, {group_name} is repeated"
            )
