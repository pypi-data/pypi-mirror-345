from collections.abc import Mapping
from functools import reduce
from typing import Any, Hashable, Iterable, Self, TypeAlias
from .super_dict import SuperDict
from .utils import str_lower
_NestedDictInit: TypeAlias = Mapping | Iterable[tuple[Hashable, Any]]


class NestedDict(SuperDict):
    def __init__(self,
                 data: _NestedDictInit = {},                                    # NOQA
                 *,
                 nest_keys: str | list | tuple | None,
                 nested_readable_keys_incl: bool | str | list | tuple = True,
                 nested_readable_keys_excl: bool | str | list | tuple = False,
                 nested_removable_keys_incl: bool | str | list | tuple = False,
                 nested_removable_keys_excl: bool | str | list | tuple = False,
                 hide_nested_keys_in_iter: bool = True,
                 **kwargs):
        self._nest_keys = [nest_keys] if isinstance(nest_keys, str) \
            else sorted(list(nest_keys)) if isinstance(nest_keys, Iterable) \
            else [] if nest_keys is None \
            else nest_keys
        if isinstance(self._nest_keys, list):
            self._nest_keys = tuple(self._nest_keys)
        else:
            raise ValueError("Invalid nested_keys datatype")

        self._nested_readable_keys_incl = \
            _ancestry_keys(nested_readable_keys_incl)
        self._nested_readable_keys_incl_lower = \
            _ancestry_keys(nested_readable_keys_incl, True)
        self._nested_readable_keys_excl = \
            _ancestry_keys(nested_readable_keys_excl)
        self._nested_readable_keys_excl_lower = \
            _ancestry_keys(nested_readable_keys_excl, True)

        self._nested_removable_keys_incl = \
            _ancestry_keys(nested_removable_keys_incl)
        self._nested_removable_keys_incl_lower = \
            _ancestry_keys(nested_removable_keys_incl, True)
        self._nested_removable_keys_excl = \
            _ancestry_keys(nested_removable_keys_excl)
        self._nested_removable_keys_excl_lower = \
            _ancestry_keys(nested_removable_keys_excl, True)

        self._hide_nested_keys_in_iter = hide_nested_keys_in_iter

        self._kwargs = kwargs

        self._ancestry_lookup_enabled = True

        super().__init__(data, **kwargs)

    def __contains__(self, key):
        if super().__contains__(key):
            return True
        elif not self._readable_from_ancestry(key):
            return False

        nest_key_chain = self.nest_key_chain
        if nest_key_chain is not None:
            ancestry_chain = self.ancestry_chain
            nest_key_chain = self.nest_key_chain + [key]

            key_found = False
            for _, ancestor in ancestry_chain[len(nest_key_chain):]:
                node = ancestor
                nest_key_chain_matched = True
                for nested_key in nest_key_chain:
                    if nested_key in node:
                        node = node[nested_key]
                    else:
                        nest_key_chain_matched = False
                        break
                if nest_key_chain_matched:
                    key_found = True
                    break
            if key_found:
                return True

        return False

    # def __cmp__(self, other):
    #     __le__, __lt__, __ge__, __gt__
    #     raise AttributeError("")

    def __delitem__(self, key):
        if super().__contains__(key):
            super().__delitem__(key)
        elif self._removable_from_ancestry(key) and key in self._parent:
            del self._parent[key]
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        if super().__contains__(key):
            return super().__getitem__(key)
        elif not self._readable_from_ancestry(key):
            return self.__missing__(key)

        nest_key_chain = self.nest_key_chain
        if nest_key_chain is not None:
            ancestry_chain = self.ancestry_chain
            nest_key_chain = self.nest_key_chain + [key]

            key_found = False
            node = None
            for _, ancestor in ancestry_chain[len(nest_key_chain):]:
                node = ancestor
                nest_key_chain_matched = True
                for nested_key in nest_key_chain:
                    if nested_key in node:
                        node = node[nested_key]
                    else:
                        nest_key_chain_matched = False
                        break
                if nest_key_chain_matched:
                    key_found = True
                    break
            if key_found:
                return node

        return self.__missing__(key)

    def __iter__(self):
        iter_seen_keys = []
        for self_key in super()._iter():                                        # NOQA
            if self._hide_nested_keys_in_iter and self_key in self._nest_keys:
                continue
            iter_seen_keys.append(self_key)
            yield self_key

        if not self._ancestry_lookup_enabled:
            return

        nest_key_chain = self.nest_key_chain
        if nest_key_chain is not None:
            ancestry_chain = self.ancestry_chain

            for _, ancestor in ancestry_chain[len(nest_key_chain)+1:]:
                node = ancestor
                key_found = bool(nest_key_chain)
                for nested_key in nest_key_chain:
                    if nested_key in node:
                        node = node[nested_key]
                    else:
                        key_found = False
                        break
                if key_found:
                    for ancestor_key in node._iter():                           # NOQA
                        if ancestor_key in iter_seen_keys:
                            continue
                        iter_seen_keys.append(ancestor_key)
                        yield ancestor_key

    # TODO Test
    def __len__(self):
        return len([key for key in self])

    # def __or__(self, other):
    #     self_ignorecase_flipped = False
    #     if self.key_ignorecase:
    #         self.key_ignorecase = False
    #         self_ignorecase_flipped = True
    #
    #     other_ignorecase_flipped = False
    #     if isinstance(other, self.__class__):
    #         if other.key_ignorecase:
    #             other.key_ignorecase = False
    #             other_ignorecase_flipped = True
    #
    #     orred = self._store | other
    #
    #     if self_ignorecase_flipped:
    #         self.key_ignorecase = True
    #
    #     if other_ignorecase_flipped:
    #         other.key_ignorecase = True
    #
    #     return other.like(orred) if isinstance(other, self.__class__) \
    #         else orred

    def __repr__(self):
        kwargs_repr = reduce(
            lambda x, y: f"{x}, {y[0]}={y[1]}", self._kwargs.items(), ""
        )
        return (
            f"{self.__class__.__name__}({dict(self.items_keys_truecase())},"
            f" nest_keys={self._nest_keys},"
            f" nested_readable_keys_incl={self._nested_readable_keys_incl},"
            f" nested_readable_keys_excl={self._nested_readable_keys_excl},"
            f" nested_removable_keys_incl={self._nested_removable_keys_incl},"
            f" nested_removable_keys_excl={self._nested_removable_keys_excl},"
            f" {kwargs_repr})"
        )

    @property
    def nest_key_chain(self) -> list:
        nest_key_chain = []
        nest_key_located = False
        ancestor = self
        while ancestor.parent is not None:
            nest_key_chain.append(ancestor.bound_key)
            if ancestor.bound_key in self._nest_keys:
                nest_key_located = True
                break
            ancestor = ancestor.parent
        if nest_key_located:
            nest_key_chain = nest_key_chain[::-1]
        else:
            nest_key_chain = None
        return nest_key_chain

    def as_dict(self):
        as_dict = {}
        for key, value in self.items():
            as_dict[key] = value.as_dict() \
                if isinstance(value, self.__class__) \
                else value
        return as_dict

    def copy(self):
        return self.like(self._store.values() if self.key_ignorecase
                         else dict(self))

    def disable_ancestry_lookup(self):
        self._ancestry_lookup_enabled = False

    def enable_ancestry_lookup(self):
        self._ancestry_lookup_enabled = True

    def items(self):
        return NestedDictItemsView(self)

    # TODO Test
    def items_keys_truecase(self):
        return NestedDictItemsView(self, keys_truecase=True)

    def keys(self):
        return NestedDictKeysView(self)

    # TODO Test
    def keys_truecase(self):
        return NestedDictKeysView(self, keys_truecase=True)

    def like(self, data: _NestedDictInit) -> Self:
        return self.__class__(
            data,
            nest_keys=self._nest_keys,
            nested_readable_keys_incl=self._nested_readable_keys_incl,
            nested_readable_keys_excl=self._nested_readable_keys_excl,
            nested_removable_keys_incl=self._nested_removable_keys_incl,
            nested_removable_keys_excl=self._nested_removable_keys_excl,
            **self._kwargs,
        )

    def pop(self, key, *args):
        try:
            return super().pop(key)
        except KeyError as e:
            if (self._removable_from_ancestry(key)
                    and key in self._parent):
                return self._parent.pop(key)
            else:
                if args:
                    return args[0]
                else:
                    raise e

    def pop_truecase(self, key, *args):
        try:
            return super().pop_key_truecase(key)
        except KeyError as e:
            if (self._removable_from_ancestry(key)
                    and key in self._parent):
                return self._parent.pop_key_truecase(key)
            else:
                if args:
                    return args[0]
                else:
                    raise e

    def values(self):
        return NestedDictValuesView(self)

    def _actionable_from_ancestry(
            self,
            key: str,
            nested_actionable_keys_incl: list | tuple,
            nested_actionable_keys_incl_lower: list | tuple,
            nested_actionable_keys_excl: list | tuple,
            nested_actionable_keys_excl_lower: list | tuple,

    ) -> bool:
        if (not self._ancestry_lookup_enabled
                or self._parent is None
                or nested_actionable_keys_incl is False
                or nested_actionable_keys_excl is True):
            return False

        key_in_nest = False
        for nest_key in self._nest_keys:
            if nest_key in self.ancestry_bound_key_chain:
                key_in_nest = True
                break
        if not key_in_nest:
            return False

        key_lower = str_lower(key)
        return ((nested_actionable_keys_incl is True
                 or key in nested_actionable_keys_incl
                 or (self.key_ignorecase
                     and key_lower in nested_actionable_keys_incl_lower))
                and
                (nested_actionable_keys_excl is False
                 or key not in nested_actionable_keys_excl
                 or (self.key_ignorecase
                     and key_lower
                     not in nested_actionable_keys_excl_lower)))

    def _readable_from_ancestry(self, key) -> bool:
        return self._actionable_from_ancestry(
            key,
            self._nested_readable_keys_incl,
            self._nested_readable_keys_incl_lower,
            self._nested_readable_keys_excl,
            self._nested_readable_keys_excl_lower,
        )

    def _removable_from_ancestry(self, key) -> bool:
        return self._actionable_from_ancestry(
            key,
            self._nested_removable_keys_incl,
            self._nested_removable_keys_incl_lower,
            self._nested_removable_keys_excl,
            self._nested_removable_keys_excl_lower,
        )


class NestedDictItemsView:
    def __init__(self, nested_dict: NestedDict, keys_truecase: bool = False):
        self._nested_dict = nested_dict
        self._keys_truecase = keys_truecase

    def __iter__(self):
        for key in self._nested_dict:
            yield key, self._nested_dict[key]

    def __str__(self):
        return f"{self.__class__.__name__}({[item for item in self]})"


class NestedDictKeysView:
    def __init__(self, nested_dict: NestedDict, keys_truecase: bool = False):
        self._nested_dict = nested_dict
        self._keys_truecase = keys_truecase

    def __iter__(self):
        yield from self._nested_dict

    def __str__(self):
        return f"{self.__class__.__name__}({[key for key in self]})"


class NestedDictValuesView:
    def __init__(self, nested_dict: NestedDict):
        self._nested_dict = nested_dict

    def __iter__(self):
        for key in self._nested_dict:
            yield self._nested_dict[key]

    def __str__(self):
        return f"{self.__class__.__name__}({[value for value in self]})"


def _ancestry_keys(keys: bool | str | list | tuple, make_lower: bool = False):
    keys = [keys] if isinstance(keys, str) else keys
    if isinstance(keys, (list, tuple)):
        if make_lower:
            keys = [str_lower(key) for key in keys]
        keys = tuple(sorted(keys))
    return keys
