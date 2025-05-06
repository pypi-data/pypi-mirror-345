import base64
from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Dict, FrozenSet, List, Set, Tuple, TypeVar, Union, cast, overload
from uuid import UUID

JSON = Union[
    str, int, float, bool, Dict["JSON", "JSON"], List["JSON"], "Schema", Enum, None
]

JSONType = TypeVar("JSONType", bound=JSON)
JSONTypeKey = TypeVar("JSONTypeKey", bound=JSON)
JSONTypeValue = TypeVar("JSONTypeValue", bound=JSON)


class Schema(ABC):
    def to_json_data(self) -> Dict[JSON, JSON]:
        res = self._to_json_data(cast(Dict[JSON, JSON], self.__dict__))
        return res

    @overload
    @staticmethod
    def _to_json_data(data: None) -> None: ...

    @overload
    @staticmethod
    def _to_json_data(data: bool) -> bool: ...

    @overload
    @staticmethod
    def _to_json_data(data: int) -> int: ...

    @overload
    @staticmethod
    def _to_json_data(data: float) -> float: ...

    @overload
    @staticmethod
    def _to_json_data(data: str) -> str: ...

    @overload
    @staticmethod
    def _to_json_data(data: bytes) -> str: ...

    @overload
    @staticmethod
    def _to_json_data(data: UUID) -> str: ...

    @overload
    @staticmethod
    def _to_json_data(data: datetime) -> str: ...

    @overload
    @staticmethod
    def _to_json_data(data: List[JSONType]) -> List[JSON]: ...

    @overload
    @staticmethod
    def _to_json_data(data: Tuple[JSONType]) -> List[JSON]: ...

    @overload
    @staticmethod
    def _to_json_data(data: Set[JSONType]) -> List[JSON]: ...

    @overload
    @staticmethod
    def _to_json_data(data: FrozenSet[JSONType]) -> List[JSON]: ...

    @overload
    @staticmethod
    def _to_json_data(data: Dict[JSONTypeKey, JSONTypeValue]) -> Dict[JSON, JSON]: ...

    @overload
    @staticmethod
    def _to_json_data(data: Enum) -> JSON: ...

    @overload
    @staticmethod
    def _to_json_data(data: "Schema") -> Dict[JSON, JSON]: ...

    @staticmethod
    def _to_json_data(data: JSON) -> JSON:
        if data is None or isinstance(data, (bool, int, float, str)):
            return data
        if isinstance(data, datetime):
            return data.isoformat()
        if isinstance(data, (list, tuple, set, frozenset)):
            return [Schema._to_json_data(d) for d in data]
        if isinstance(data, dict):
            return {
                Schema._to_json_data(k): Schema._to_json_data(v)
                for k, v in data.items()
            }
        if isinstance(data, Enum):
            value = data.value  # type: JSON
            return Schema._to_json_data(value)
        if isinstance(data, UUID):
            return str(data)
        if isinstance(data, bytes):
            return base64.b64encode(data).decode("utf-8")
        return data.to_json_data()

    @staticmethod
    def from_json_data(data: JSON) -> "Schema":
        raise NotImplementedError
