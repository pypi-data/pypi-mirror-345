import ctypes
import mmap
import struct
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

if TYPE_CHECKING:
    from typing import Protocol

    class Lockable(Protocol):
        def acquire(self, blocking: bool = True, timeout: int = -1) -> bool: ...
        async def async_acquire(
            self, blocking: bool = True, timeout: int = -1
        ) -> bool: ...

        def release(self) -> None: ...
        async def async_release(self) -> None: ...

        def __enter__(self) -> bool: ...
        async def __aenter__(self) -> bool: ...

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
        def get_owner_and_locktime(
            self,
        ) -> Optional[Tuple[Union[int, Tuple[int, int]], float]]: ...

else:
    Lockable = Any


class BaseInfoStructure(ctypes.Structure):
    head = 0  # type: int
    tail = 0  # type: int
    available = 0  # type: int
    _fields_ = [
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
        ("available", ctypes.c_uint32),
    ]


InfoStructType = TypeVar("InfoStructType", bound=BaseInfoStructure)
T = TypeVar("T")


class CyclicBufferView:
    def __init__(self, buffer: mmap.mmap, buffer_size: int):
        self.buffer_size = buffer_size
        self.buffer = buffer

    @overload
    def __getitem__(self, key: int) -> int: ...
    @overload
    def __getitem__(self, key: slice) -> bytes: ...

    def __getitem__(self, key: Union[slice, int]) -> Union[bytes, int]:
        if isinstance(key, int):
            if key > 0:
                key = key % self.buffer_size
            return self.buffer[key]
        length = key.stop - key.start
        if self.buffer_size - key.start < length:
            return bytes(self.buffer[key.start : self.buffer_size]) + bytes(
                self.buffer[: length - (self.buffer_size - key.start)]
            )
        else:
            return bytes(self.buffer[key])

    def __setitem__(self, key: slice, value: bytes) -> None:
        if isinstance(key, int):
            if key > 0:
                key = key % self.buffer_size
            self.buffer[key] = value
            return
        length = key.stop - key.start
        if self.buffer_size - key.start < length:
            self.buffer[key.start : self.buffer_size] = value[
                : self.buffer_size - key.start
            ]
            self.buffer[: length - (self.buffer_size - key.start)] = value[
                self.buffer_size - key.start :
            ]
        else:
            self.buffer[key] = value


class BufferBackedCyclicQueue(Generic[InfoStructType]):
    def __init__(
        self,
        buffer: mmap.mmap,
        info_struct_type: Type[InfoStructType],
        size: int,
    ):
        self._in_sync_context = False
        self.buffer = buffer
        self.info_struct_type = info_struct_type
        self._timeout = 8
        self._buffer_size = size - ctypes.sizeof(info_struct_type)
        if self.available == 0:
            self.available = self._buffer_size

        self.buffer_view = CyclicBufferView(buffer, self._buffer_size)

    # This should only be used directly in a synchronized context
    @property
    def _info(self) -> InfoStructType:
        return self.info_struct_type.from_buffer(self.buffer, self._buffer_size)

    @property
    def available(self) -> int:
        return self._info.available

    @available.setter
    def available(self, value: int) -> None:
        self._info.available = value

    def push(self, data: bytes) -> bool:
        data_to_write = struct.pack("I", len(data)) + data
        if len(data_to_write) > self._info.available:
            return False

        address = self._info.tail
        self._info.available -= len(data_to_write)

        self.buffer_view[address : address + len(data_to_write)] = data_to_write

        self._info.tail = (address + len(data_to_write)) % self._buffer_size
        return True

    def get_utilization(self) -> float:
        return ((self._buffer_size - self.available) / self._buffer_size) * 100

    def popleft(self) -> Optional[bytes]:
        if self._info.head == self._info.tail and self._info.available > 0:
            return None

        len_address = self._info.head
        data_address = len_address + 4
        length = struct.unpack(
            "I", bytearray(self.buffer_view[self._info.head : self._info.head + 4])
        )[0]
        data = self.buffer_view[data_address : data_address + length]
        self._info.head = (data_address + length) % self._buffer_size
        self._info.available += length + 4
        return data
