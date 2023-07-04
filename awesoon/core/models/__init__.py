
from typing import Any, Dict, Type, TypeVar
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class BaseDataClass:
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
