from collections import OrderedDict
from collections.abc import Mapping
from typing import Any, Iterable, Hashable, MutableMapping, Self, TypeAlias

_CaseInsensitiveDictInit: TypeAlias = Mapping | Iterable[tuple[Hashable, Any]]


class CaseInsensitiveDict(MutableMapping, dict):
    """Deprecated. Please use super_dict.SuperDict.

    A case-insensitive ``dict``-like object.

    Copied from requests.structures
    Implements all methods and operations of
    ``MutableMapping`` as well as dict's ``copy``. Also
    provides ``items_lower``.

    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case-insensitive::

        cid = CaseInsensitiveDict()
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
                 data: _CaseInsensitiveDictInit = {},
                 *,
                 recursive: bool = False,
                 ordered: bool = False,
                 **kwargs):
        self._recursive = recursive
        self._ordered = ordered

        self._store = OrderedDict() if self._ordered else dict()
        self.update(dict(data, **kwargs))

    def __delitem__(self, key):
        del self._store[_str_lower(key)]

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = self.__class__(other)
            return dict(self.items_lower()) == dict(other.items_lower())
        else:
            return NotImplemented

    def __getitem__(self, key):
        return self._store[_str_lower(key)][1]

    def __iter__(self):
        return (key_lower for key_lower, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return (f"{self.__class__.__name}({dict(self.items())},"
                f" recursive={self._recursive},"
                f" ordered={self._ordered})")

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value
        if self._recursive and isinstance(value, Mapping):
            value = self._new_like_self(value)
        self._store[_str_lower(key)] = (key, value)

    def items_lower(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1])
                for (lowerkey, keyval) in self._store.items())

    # Copy is required
    def copy(self):
        return self.__class__(self._store.values())

    def _new_like_self(self, data: _CaseInsensitiveDictInit) -> Self:
        return self.__class__(data,
                              recursive=self._recursive,
                              ordered=self._ordered)


def _str_lower(text: Any) -> Any:
    return text.lower() if isinstance(text, str) else text
