# https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
from collections import OrderedDict
from collections.abc import Mapping
from typing import (Any, Callable, Hashable, Iterable, MutableMapping,
                    Self, TypeAlias)
_NestedDictInit: TypeAlias = Mapping | Iterable[tuple[Hashable, Any]]


class NestedDict(MutableMapping, dict):
    """A super ``dict``-like object that has ``collections.defaultdict``,
    ``collections.OrderedDict``, case-insensitiviy and recursion rolled
    into one.

    Initially sourced from requests.structures and heavily modified.
    Implements all methods and operations of
    ``MutableMapping`` as well as dict's ``copy``. When key case-insensitivity
    is turned on, also provides various dict methods with newer ``_truecase``
    versions.

    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case-insensitive::

        cid = NestedDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True

    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.

    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.
    """
    def __init__(self,
                 data: _NestedDictInit = {},                                     # NOQA
                 *,
                 key_ignorecase: bool = False,
                 ordereddict: bool = False,
                 default_factory: Callable[[], Any] | None = None,
                 build_ancestry: bool = False,
                 read_from_ancestry_incl: bool | str | list = False,
                 read_from_ancestry_excl: bool | str | list = False,
                 write_to_ancestry_incl: bool | str | list = False,
                 write_to_ancestry_excl: bool | str | list = False,
                 **kwargs):
        self._key_ignorecase = key_ignorecase
        self._ordereddict = ordereddict
        self.default_factory = default_factory

        self._build_ancestry = build_ancestry

        self._read_from_ancestry_incl = \
            _ancestry_keys(read_from_ancestry_incl)
        self._read_from_ancestry_incl_lower = \
            _ancestry_keys(read_from_ancestry_incl, True)
        self._read_from_ancestry_excl = \
            _ancestry_keys(read_from_ancestry_excl)
        self._read_from_ancestry_excl_lower = \
            _ancestry_keys(read_from_ancestry_excl, True)

        self._write_to_ancestry_incl = \
            _ancestry_keys(write_to_ancestry_incl)
        self._write_to_ancestry_incl_lower = \
            _ancestry_keys(write_to_ancestry_incl, True)
        self._write_to_ancestry_excl = \
            _ancestry_keys(write_to_ancestry_excl)
        self._write_to_ancestry_excl_lower = \
            _ancestry_keys(write_to_ancestry_excl, True)

        self._parent = None
        self._bound_to_key = None
        self._store = OrderedDict() if self._ordereddict else dict()
        self.update(dict(data, **kwargs))                    # calls __setitem__

    def __bool__(self):
        return bool(self._store)

    def __contains__(self, key):
        if self._contains_locally(key):
            return True
        elif not self._readable_from_ancestry(key):
            return False

        key_ancestry = [key]
        ancestry_search = [ancestor for _, ancestor in self.ancestry_chain]
        while ancestry_search:
            key_ancestry.append(ancestry_search[0]._bound_to_key)               # NOQA
            ancestry_search = ancestry_search[1:]
            for ancestor in ancestry_search:
                search_node = ancestor
                keys_matched = True
                for key_ in key_ancestry[-2::-1]:
                    if isinstance(search_node, self.__class__):
                        if search_node._contains_locally(key_):
                            search_node = search_node[key_]
                        else:
                            keys_matched = False
                    else:
                        try:
                            search_node = search_node[key_]
                        except Exception:                                       # NOQA
                            keys_matched = False
                    if not keys_matched:
                        break
                if keys_matched:
                    return True

        return False

    # def __cmp__(self, other):
    #     __le__, __lt__, __ge__, __gt__
    #     raise AttributeError("")

    def __delitem__(self, key):
        if (not self._contains_locally(key)
                and self._writable_to_ancestry(key)
                and self._parent is not None
                and key in self._parent):
            del self._parent[key]
        else:
            if self._contains_locally(key):
                value = self[key]
                if isinstance(value, self.__class__):
                    value._parent = None
            self._delitem_locally(key)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self._store == other._store
                and self.key_ignorecase == other.key_ignorecase)

    def __getitem__(self, key):
        got_item = False

        if self._contains_locally(key):
            value = self._store[_str_lower(key)][1] if self._key_ignorecase \
                else self._store[key]
            got_item = True
        elif self._readable_from_ancestry(key):
            key_ancestry = [key]
            ancestry_search = [self] + self.ancestry_chain
            while ancestry_search:
                key_ancestry.append(ancestry_search[0]._bound_to_key)
                ancestry_search = ancestry_search[1:]
                keys_matched = False
                for ancestor in ancestry_search:
                    search_node = ancestor
                    keys_matched = True
                    for key_ in key_ancestry[-2::-1]:
                        if isinstance(search_node, self.__class__):
                            if search_node._contains_locally(key_):
                                search_node = search_node[key_]
                            else:
                                keys_matched = False
                        else:
                            try:
                                search_node = search_node[key_]
                            except Exception:                                   # NOQA
                                keys_matched = False
                        if not keys_matched:
                            break
                    if keys_matched:
                        value = search_node
                        got_item = True
                        break
                if keys_matched:
                    break

        if not got_item:
            if self._default_factory is not None:
                value = self.__missing__(key)
            else:
                raise KeyError(key)

        return value                                                            # NOQA

    def __iter__(self):
        yield from self._store

        if self._parent is not None:
            for key in self._parent:
                if (key not in self._store
                        and self._readable_from_ancestry(key)):
                    yield key

    def __len__(self):
        return len([key for key in self])

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        if not self._contains_locally(key):
            self[key] = self._default_factory()
        return self[key]

    def __or__(self, other):
        self_ignorecase_flipped = False
        if self.key_ignorecase:
            self.key_ignorecase = False
            self_ignorecase_flipped = True

        other_ignorecase_flipped = False
        if isinstance(other, self.__class__):
            if other.key_ignorecase:
                other.key_ignorecase = False
                other_ignorecase_flipped = True

        orred = self._store | other

        if self_ignorecase_flipped:
            self.key_ignorecase = True

        if other_ignorecase_flipped:
            other.key_ignorecase = True

        return other.like(orred) if isinstance(other, self.__class__) \
            else orred

    def __repr__(self):
        return (f"{self.__class__.__name__}({dict(self.items_keys_truecase())},"
                f" key_ignorecase={self._key_ignorecase},"
                f" ordereddict={self._ordereddict},"
                f" default_factory={self._default_factory},"
                f" build_ancestry={self._build_ancestry},"
                f" read_from_ancestry_incl={self._read_from_ancestry_incl},"
                f" read_from_ancestry_excl={self._read_from_ancestry_excl},"
                f" write_to_ancestry_incl={self._write_to_ancestry_incl},"
                f" write_to_ancestry_excl={self._write_to_ancestry_excl})")

    def __setitem__(self, key, value):
        if isinstance(value, Mapping):
            if not isinstance(value, self.__class__):
                value = self.like(value)
            if self._build_ancestry:
                value._parent = self
                value._bound_to_key = key

        if self._key_ignorecase:
            # Use the lowercased key for lookups, but store the actual key
            # alongside the value
            self._store[_str_lower(key)] = (key, value)
        else:
            self._store[key] = value

    @property
    def bound_to_key(self):
        return self._bound_to_key

    @property
    def default_factory(self):
        return self._default_factory

    @default_factory.setter
    def default_factory(self, factory: Callable[[], Any]):
        if not (factory is None or isinstance(factory, Callable)):
            raise TypeError(f"'{type(factory)}' object is not callable")
        self._default_factory = factory

    @property
    def key_ignorecase(self):
        return self._key_ignorecase

    @key_ignorecase.setter
    def key_ignorecase(self, ignorecase: bool):
        if not (ignorecase := bool(ignorecase)) == self._key_ignorecase:
            self._key_ignorecase = ignorecase
            if self._key_ignorecase:
                self._store = {_str_lower(key): (key, value)
                               for key, value in self._store.items()}
            else:
                self._store = {value[0]: value[1]
                               for value in self._store.values()}

    @property
    def parent(self):
        return self._parent

    @property
    def ancestry_chain(self):
        return ([(self._bound_to_key, self)]
                + ([] if self._parent is None else self._parent.ancestry_chain))

    @property
    def root(self):
        return self if self._parent is None else self._parent.root

    def copy(self):
        return self.like(self._store.values() if self._key_ignorecase
                         else dict(self))

    def get(self, key, default=None):
        if self._contains_locally(key):
            return self[key]
        elif self._parent is None:
            return default
        else:
            return self._parent.get(key, default)

    def get_truecase(self, key, default=None):
        if self._key_ignorecase:
            value = default
            if (key_lower := _str_lower(key)) in self._store:
                value_ = self._store[key_lower]
                if value_[0] == key:
                    value = value_[1]
            return value
        else:
            return self.get(key, default)

    def items(self):
        return NestedDictItemsView(self)

    def items_keys_truecase(self):
        return NestedDictItemsView(self, keys_truecase=True)

    def keys(self):
        return NestedDictKeysView(self)

    def keys_truecase(self):
        return NestedDictKeysView(self, keys_truecase=True)

    def pop(self, key, *args):
        if (not self._contains_locally(key)
                and self._writable_to_ancestry(key)
                and self._parent is not None
                and key in self._parent):
            return self._parent.pop(key)
        else:
            if self._contains_locally(key):
                value = self[key]
                if self._key_ignorecase:
                    value = value[1]
                if isinstance(value, self.__class__):
                    value._parent = None
                self._delitem_locally(key)
        return self._store.pop(key, *args)

    def pop_truecase(self, key, default):
        if self._key_ignorecase:
            popped = default
            if (key_lower := _str_lower(key)) in self._store:
                value = self._store[key_lower]
                if value[0] == key:
                    popped = value[1]
                    self._delitem_locally(key)
        else:
            popped = self._store.pop(key, default)
        return popped

    def popitem(self):
        # popitem is allowed only on current dict, not on ancestry, as it will
        # eventually delete current dict, and that will make no sense.
        popped_item = self._store.popitem()
        if self._key_ignorecase:
            key, value = popped_item
            popped_item = (key, value[1])
        return popped_item

    def popitem_truecase(self):
        popped_item = self._store.popitem()
        if self._key_ignorecase:
            popped_item = popped_item[1]
        return popped_item

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    # def update(self, *args, **kwargs):
    #     self._store.update(*args, **kwargs)

    def values(self):
        return NestedDictValuesView(self)

    def like(self, data: _NestedDictInit) -> Self:
        return self.__class__(
            data,
            key_ignorecase=self._key_ignorecase,
            ordereddict=self._ordereddict,
            default_factory=self._default_factory,
            build_ancestry=self._build_ancestry,
            read_from_ancestry_incl=self._read_from_ancestry_incl,
            read_from_ancestry_excl=self._read_from_ancestry_excl,
            write_to_ancestry_incl=self._write_to_ancestry_incl,
            write_to_ancestry_excl=self._write_to_ancestry_excl
        )

    def _contains_locally(self, key):
        return (_str_lower(key) if self._key_ignorecase else key) in self._store

    def _delitem_locally(self, key):
        del self._store[_str_lower(key) if self._key_ignorecase else key]

    def _readable_from_ancestry(self, key) -> bool:
        if (not self._build_ancestry
                or self._parent is None
                or self._read_from_ancestry_incl is False
                or self._read_from_ancestry_excl is True):
            return False

        key_lower = _str_lower(key)
        return ((self._read_from_ancestry_incl is True
                 or key in self._read_from_ancestry_incl
                 or (self._key_ignorecase
                     and key_lower in self._read_from_ancestry_incl_lower))
                and
                (self._read_from_ancestry_excl is False
                    or key not in self._read_from_ancestry_excl
                    or (self._key_ignorecase
                        and key_lower
                        not in self._read_from_ancestry_excl_lower)))

    def _writable_to_ancestry(self, key) -> bool:
        if (not self._build_ancestry
                or self._parent is None
                or self._write_to_ancestry_incl is False
                or self._write_to_ancestry_excl is True):
            return False

        key_lower = _str_lower(key)
        return ((self._write_to_ancestry_incl is True
                 or key in self._write_to_ancestry_incl
                 or (self._key_ignorecase
                     and key in self._write_to_ancestry_incl_lower))
                and
                (self._write_to_ancestry_excl is False
                    or key not in self._write_to_ancestry_excl
                    or (self._key_ignorecase
                        and key_lower
                        not in self._write_to_ancestry_excl_lower)))


class NestedDictItemsView:
    def __init__(self, nested_dict: NestedDict, keys_truecase: bool = False):
        self._nested_dict = nested_dict
        self._keys_truecase = keys_truecase

    def __iter__(self):
        for key, value in self._nested_dict._store.items():                     # NOQA
            if self._nested_dict._key_ignorecase:                               # NOQA
                key_truecase, value = value
                if self._keys_truecase:
                    key = key_truecase
            yield key, value

        if self._nested_dict._parent is not None:                               # NOQA
            for key in self._nested_dict._parent.keys():                        # NOQA
                if (key not in self._nested_dict._store.keys()                  # NOQA
                        and self._nested_dict._readable_from_ancestry(key)):    # NOQA
                    yield (key, self._nested_dict._parent[key])                 # NOQA

    def __str__(self):
        return f"{self.__class__.__name__}({[item for item in self]})"


class NestedDictKeysView:
    def __init__(self, nested_dict: NestedDict, keys_truecase: bool = False):
        self._nested_dict = nested_dict
        self._keys_truecase = keys_truecase

    def __iter__(self):
        for key, value in self._nested_dict._store.items():                     # NOQA
            if self._nested_dict._key_ignorecase and self._keys_truecase:       # NOQA
                key = value[0]
            yield key

        if self._nested_dict._parent is not None:                               # NOQA
            for key in self._nested_dict._parent:                               # NOQA
                if (key not in self._nested_dict._store                         # NOQA
                        and self._nested_dict._readable_from_ancestry(key)):    # NOQA
                    yield key

    def __str__(self):
        return f"{self.__class__.__name__}({[key for key in self]})"


class NestedDictValuesView:
    def __init__(self, nested_dict: NestedDict):
        self._nested_dict = nested_dict

    def __iter__(self):
        for key in self._nested_dict._store.keys():                             # NOQA
            value = self._nested_dict._store[key]                               # NOQA
            if self._nested_dict._key_ignorecase:                               # NOQA
                value = value[1]
            yield value

        if self._nested_dict._parent is not None:                               # NOQA
            for key in self._nested_dict._parent.keys():                        # NOQA
                if (key not in self._nested_dict._store.keys()                  # NOQA
                        and self._nested_dict._readable_from_ancestry(key)):    # NOQA
                    yield self._nested_dict._parent[key]                        # NOQA

    def __str__(self):
        return f"{self.__class__.__name__}({[value for value in self]})"


def _ancestry_keys(keys: bool | str | list, lower_cased: bool = False):
    keys = [keys] if isinstance(keys, str) else keys
    if lower_cased and isinstance(keys, list):
        keys = [_str_lower(key) for key in keys]
    return keys


def _str_lower(text: Any) -> Any:
    return text.lower() if isinstance(text, str) else text
