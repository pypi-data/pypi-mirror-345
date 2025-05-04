import json
from typing import Any


class Bunch:
    def __init__(self, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, dict):
                kwargs[arg] = None
        self.__dict__.update(kwargs)

    def __getitem__(self, key: Any) -> Any or None:
        return self.__dict__.get(key, None)

    def __setitem__(self, key: Any, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: Any) -> None:
        del self.__dict__[key]

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
        self.__dict__[name] = value

    def __delattr__(self, name) -> None:
        del self.__dict__[name]

    def contains_value(self, value: Any) -> bool:
        return value in self.__dict__.values()

    def clear(self) -> None:
        self.__dict__.clear()

    def pop(self, key: Any, default: Any = None) -> Any or None:
        return self.__dict__.pop(key, default)

    def popitem(self) -> Any or None:
        return self.__dict__.popitem()

    def update(self, other: dict) -> None:
        self.__dict__.update(other)

    def setdefault(self, key: Any, default: Any = None) -> Any or None:
        return self.__dict__.setdefault(key, default)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    @staticmethod
    def from_dict(dictionary: dict) -> Any:
        return Bunch(**dictionary)
