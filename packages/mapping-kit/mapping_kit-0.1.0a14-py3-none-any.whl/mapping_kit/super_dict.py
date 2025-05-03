# https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
from collections import OrderedDict
from collections.abc import Mapping
from typing import (Any, Callable, Hashable, Iterable, MutableMapping,
                    Self, TypeAlias)
from .utils import str_lower
_SuperDictInit: TypeAlias = Mapping | Iterable[tuple[Hashable, Any]]


class SuperDict(MutableMapping, dict):
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

        cid = SuperDict()
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
                 data: _SuperDictInit = {},                                     # NOQA
                 *,
                 key_ignorecase: bool = False,
                 ordereddict: bool = False,
                 default_factory: Callable[[], Any] | None = None,
                 **kwargs):
        self._key_ignorecase = key_ignorecase
        self._ordereddict = ordereddict
        self.default_factory = default_factory

        self._parent = None
        self._bound_key = None
        self._store = OrderedDict() if self._ordereddict else dict()
        self.update(dict(data, **kwargs))                    # calls __setitem__

    def __bool__(self):
        return bool(self._store)

    def __contains__(self, key):
        return self._contains(key)

    # def __cmp__(self, other):
    #     __le__, __lt__, __ge__, __gt__
    #     raise AttributeError("")

    def __delitem__(self, key):
        try:
            value = self._getitem(key, disable_default_factory=True)
            if isinstance(value, SuperDict):
                value._parent = None
        except KeyError:
            pass

        del self._store[str_lower(key) if self._key_ignorecase else key]

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self._store == other._store
                and self.key_ignorecase == other.key_ignorecase)

    def __getitem__(self, key):
        return self._getitem(key)

    def __iter__(self):
        return self._iter()

    def __len__(self):
        return len(self._store)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
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
                f" default_factory={self._default_factory})")

    def __setitem__(self, key, value):
        self._setitem(key, value)

    @property
    def bound_key(self):
        return self._bound_key

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
                self._store = {str_lower(key): (key, value)
                               for key, value in self._store.items()}
            else:
                self._store = {value[0]: value[1]
                               for value in self._store.values()}

    @property
    def parent(self):
        return self._parent

    @property
    def ancestry_chain(self):
        return ([(self._bound_key, self)]
                + ([] if self._parent is None else self._parent.ancestry_chain))

    @property
    def ancestry_bound_key_chain(self):
        return ([self._bound_key]
                + ([] if self._parent is None
                   else self._parent.ancestry_bound_key_chain))

    @property
    def root(self):
        return self if self._parent is None else self._parent.root

    def copy(self):
        return self.like(self._store.values() if self._key_ignorecase
                         else dict(self))

    def get(self, key, default=None):
        try:
            return self._getitem(key, disable_default_factory=True)
        except KeyError:
            return default

    def get_key_truecase(self, key, default=None):
        try:
            value = self._getitem(key, disable_default_factory=True)
            if self._key_ignorecase:
                key_truecase, value = value
                if not key == key_truecase:
                    raise KeyError
            return value
        except KeyError:
            return default

    def items(self):
        return SuperDictItemsView(self)

    def items_keys_truecase(self):
        return SuperDictItemsView(self, keys_truecase=True)

    def keys(self):
        return SuperDictKeysView(self)

    def keys_truecase(self):
        return SuperDictKeysView(self, keys_truecase=True)

    def like(self, data: _SuperDictInit) -> Self:
        return self.__class__(
            data,
            key_ignorecase=self._key_ignorecase,
            ordereddict=self._ordereddict,
            default_factory=self._default_factory,
        )

    def nth_ancestor(self, n: int):
        ancestor = self
        for i in range(n):
            ancestor = ancestor.parent
        return ancestor

    def pop(self, key, *args):
        try:
            value = self._getitem(key, disable_default_factory=True)
            if isinstance(value, SuperDict):
                value._parent = None
            del self[key]
            return value
        except KeyError as e:
            if args:
                return args[0]
            else:
                raise KeyError(key)

    def pop_key_truecase(self, key, *args):
        try:
            value = self._getitem(key, disable_default_factory=True)
            if self._key_ignorecase:
                key_truecase, value = value
                if not key == key_truecase:
                    raise KeyError(key)
            if isinstance(value, SuperDict):
                value._parent = None
            del self[key]
            return value
        except KeyError as e:
            if args:
                return args[0]
            else:
                raise KeyError(key)

    def popitem(self):
        key, value = self._store.popitem()
        if self._key_ignorecase:
            value = value[1]
        if isinstance(value, self.__class__):
            value._parent = None
        return key, value

    def popitem_key_truecase(self):
        key, value = self._store.popitem()
        if self._key_ignorecase:
            key, value = value
        if isinstance(value, self.__class__):
            value._parent = None
        return key, value

    def setdefault(self, key, default=None):
        if not self._contains(key):
            self._setitem(key, default)
        return self._getitem(key)

    # def update(self, *args, **kwargs):
    #     self._store.update(*args, **kwargs)

    def values(self):
        return SuperDictValuesView(self)

    def _contains(self, key):
        return (str_lower(key) if self._key_ignorecase else key) in self._store

    def _getitem(self, key, disable_default_factory: bool = False):
        try:
            return self._store[str_lower(key)][1] if self._key_ignorecase \
                else self._store[key]
        except KeyError as e:
            if disable_default_factory or self._default_factory is None:
                raise e
            else:
                return self.__missing__(key)

    def _iter(self):
        return iter(self._store)

    def _setitem(self, key, value):
        if isinstance(value, Mapping):
            if not isinstance(value, self.__class__):
                value = self.like(value)
            value._parent = self
            value._bound_key = key

        if self._key_ignorecase:
            # Use the lowercased key for lookups, but store the actual key
            # alongside the value
            self._store[str_lower(key)] = (key, value)
        else:
            self._store[key] = value


class SuperDictItemsView:
    def __init__(self, super_dict: SuperDict, keys_truecase: bool = False):
        self._super_dict = super_dict
        self._keys_truecase = keys_truecase

    def __iter__(self):
        for key, value in self._super_dict._store.items():                      # NOQA
            if self._super_dict._key_ignorecase:                                # NOQA
                key_truecase, value = value
                if self._keys_truecase:
                    key = key_truecase
            yield key, value

    def __str__(self):
        return f"{self.__class__.__name__}({[item for item in self]})"


class SuperDictKeysView:
    def __init__(self, super_dict: SuperDict, keys_truecase: bool = False):
        self._super_dict = super_dict
        self._keys_truecase = keys_truecase

    def __iter__(self):
        for key, value in self._super_dict._store.items():                      # NOQA
            if self._super_dict._key_ignorecase and self._keys_truecase:        # NOQA
                key = value[0]
            yield key

    def __str__(self):
        return f"{self.__class__.__name__}({[key for key in self]})"


class SuperDictValuesView:
    def __init__(self, super_dict: SuperDict):
        self._super_dict = super_dict

    def __iter__(self):
        for key in self._super_dict._store.keys():                              # NOQA
            value = self._super_dict._store[key]                                # NOQA
            if self._super_dict._key_ignorecase:                                # NOQA
                value = value[1]
            yield value

    def __str__(self):
        return f"{self.__class__.__name__}({[value for value in self]})"
