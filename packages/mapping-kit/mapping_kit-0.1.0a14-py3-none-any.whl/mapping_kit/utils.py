"""
General helper functions.
"""

from collections.abc import Mapping, MutableMapping
from typing import Any

__all__ = [
    "dict_deepupdate",
    "str_lower",
]


def dict_deepupdate(
        upd_mapping: MutableMapping,
        with_mapping: Mapping | None = None,
        **kwargs
) -> None:
    for _with_mapping in [with_mapping, kwargs]:
        if _with_mapping:
            for k, v in _with_mapping.items():
                if (isinstance(v, Mapping)
                        or isinstance(v, MutableMapping)):
                    dict_deepupdate(upd_mapping.setdefault(k, v.__class__()), v)
                elif (isinstance(v, list)
                      and isinstance(upd_mapping.get(k, []), list)):
                    upd_mapping[k] = upd_mapping.get(k, []) + v
                else:
                    upd_mapping[k] = v


def str_lower(text: Any) -> Any:
    return text.lower() if isinstance(text, str) else text
