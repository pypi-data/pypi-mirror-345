import json
from typing import Any


class ImmutableBunchException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ImmutableBunch:
    def __init__(self, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, dict):
                kwargs[arg] = None
        self.__dict__.update(kwargs)

    def __getitem__(self, key: Any) -> Any or None:
        return self.__dict__.get(key, None)

    def __setitem__(self, key: Any, value: Any) -> None:
        raise ImmutableBunchException('ImmutableBunch does not support item assignment')

    def __delitem__(self, key: Any) -> None:
        raise ImmutableBunchException('ImmutableBunch does not support item deletion')

    def __contains__(self, key: Any) -> bool:
        return key in self.__dict__

    def __str__(self) -> str:
        return json.dumps(self.__dict__, sort_keys=False)

    def __repr__(self) -> str:
        return self.__str__()

    def __getattr__(self, key: Any) -> Any or None:
        if key in self.__dict__:
            return self.__dict__[key]
        return None

    def __setattr__(self, name: str, value: Any) -> None:
        raise ImmutableBunchException('ImmutableBunch does not support attribute assignment')

    def __delattr__(self, name) -> None:
        raise ImmutableBunchException('ImmutableBunch does not support attribute deletion')

    def contains_value(self, value: Any) -> bool:
        return value in self.__dict__.values()

    def clear(self) -> None:
        raise ImmutableBunchException('ImmutableBunch does not support clearing')

    def pop(self, key: Any, default: Any = None) -> Any or None:
        raise ImmutableBunchException('ImmutableBunch does not support popping')

    def popitem(self) -> Any or None:
        raise ImmutableBunchException('ImmutableBunch does not support popitem')

    def update(self, other: dict) -> None:
        raise ImmutableBunchException('ImmutableBunch does not support update')

    def setdefault(self, key: Any, default: Any = None) -> Any or None:
        raise ImmutableBunchException('ImmutableBunch does not support setdefault')

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    @staticmethod
    def from_dict(dictionary: dict) -> Any:
        return ImmutableBunch(**dictionary)
