import asyncio
import mmap
import multiprocessing
import os
import queue
import tempfile
import time
import uuid
from functools import wraps
from multiprocessing.managers import BaseManager
from threading import Event, Lock
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Callable,
    Coroutine,
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from ...process_utils import get_current_pid
from .errors import ManagerException

UpdatableConfig = Dict[str, Union[List[str], int]]
if TYPE_CHECKING:
    from typing import TypedDict

    class RemoteConfig(TypedDict):
        config: UpdatableConfig
        id: str


SessionKeyType = Tuple[str, str, FrozenSet[Tuple[str, str]]]
ProcessInfo = Dict[int, SessionKeyType]
SessionInfo = Dict[SessionKeyType, str]
MethodType = TypeVar("MethodType", bound=Callable[..., Any])
SessionRemoteConfig = Dict[SessionKeyType, UpdatableConfig]


class QueueRequest:
    def __init__(self, owner_id: int, queue_name: Optional[str] = None) -> None:
        self.owner_id = owner_id
        self.queue_name = queue_name
        self.result_event = Event()
        self.timeout_event = Event()
        self.result_lock = Lock()
        self.result = None  # type: Optional[str]

    def get_queue(self, timeout: float) -> Optional[str]:
        got_it = self.result_event.wait(timeout if timeout > 0 else None)
        with self.result_lock:
            if not got_it:
                self.timeout_event.set()
                # We need to check again after the timeout event is set, as the request might have been fulfilled
                got_it = self.result_event.is_set()
                if not got_it:
                    return None
            return self.result

    def fulfill(self, queue_name: str) -> bool:
        with self.result_lock:
            if not self.timeout_event.is_set():
                self.result = queue_name
                self.result_event.set()
                return True
            return False


class Broker:
    def __init__(self) -> None:
        self._available_queues = []  # type: List[str]
        self._requests = queue.Queue()  # type: queue.Queue[QueueRequest]
        # Missed requests are requests for specific queues that were not available when requested.
        # They will be prioritized over general requests when a queue is released.
        self._missed_requests = queue.Queue()  # type: queue.Queue[QueueRequest]
        self._lock = Lock()
        self._owned_queues = {}  # type: Dict[str, Tuple[int, float]]

    def register_queue(self, queue_name: str) -> None:
        with self._lock:
            self._available_queues.append(queue_name)

    def deregister_queue(self, queue_name: str) -> None:
        with self._lock:
            if queue_name in self._owned_queues:
                del self._owned_queues[queue_name]
            if queue_name in self._available_queues:
                self._available_queues.remove(queue_name)

    def request_queue(
        self,
        owner_id: int,
        queue_name: Optional[str] = None,
        timeout: float = 0.0,
    ) -> Optional[str]:
        with self._lock:
            if queue_name:
                if queue_name in self._available_queues:
                    self._owned_queues[queue_name] = (owner_id, time.time())
                    self._available_queues.remove(queue_name)
                    return queue_name
            else:
                if self._available_queues:
                    queue_name = self._available_queues.pop(0)
                    self._owned_queues[queue_name] = (owner_id, time.time())
                    return queue_name
            queue_request = QueueRequest(owner_id, queue_name)
            self._requests.put(queue_request)

        return queue_request.get_queue(timeout)

    def release_queue(self, qname: str) -> None:
        with self._lock:
            if qname not in self._owned_queues:
                return
            del self._owned_queues[qname]

            tmp_requests = queue.Queue()  # type: queue.Queue[QueueRequest]
            while not self._missed_requests.empty():
                queue_request = self._missed_requests.get_nowait()
                if queue_request.queue_name == qname:
                    if queue_request.fulfill(qname):
                        self._owned_queues[qname] = (
                            queue_request.owner_id,
                            time.time(),
                        )
                        return
                    continue
                tmp_requests.put(queue_request)

            self._missed_requests = tmp_requests

            while not self._requests.empty():
                queue_request = self._requests.get_nowait()
                if queue_request.queue_name is None:
                    if queue_request.fulfill(qname):
                        self._owned_queues[qname] = (
                            queue_request.owner_id,
                            time.time(),
                        )
                        return
                    continue
                if queue_request.queue_name == qname:
                    if queue_request.fulfill(qname):
                        self._owned_queues[qname] = (
                            queue_request.owner_id,
                            time.time(),
                        )
                        return
                    continue
                else:
                    self._missed_requests.put(queue_request)
                    continue

            self._available_queues.append(qname)
            return

    def get_owned_queues(self) -> Dict[str, Tuple[int, float]]:
        with self._lock:
            return self._owned_queues


def exposer(state: List[str]) -> Callable[[MethodType], MethodType]:
    def decorator(func: MethodType) -> MethodType:
        state.append(func.__name__)
        return func

    return decorator


class ManagerState:
    exposed_methods: List[str] = []

    expose = exposer(exposed_methods)

    def __init__(self) -> None:
        self._pid = os.getpid()

        self._exporter_pid = 0
        self._shared_memory_size = 0
        self._connected_processes: ProcessInfo = {}
        self._disconnected_processes: ProcessInfo = {}
        self._sessions: SessionInfo = {}
        self._throttled_pids: Set[int] = set()
        self._remote_config: Dict[SessionKeyType, RemoteConfig] = {}

        # Shared memory queues
        self._broker = Broker()
        self._shared_memory_names: List[str] = []

    # Exposed broker methods
    @expose
    def request_queue(
        self, owner_id: int, queue_name: Optional[str] = None, timeout: float = 0.0
    ) -> Optional[str]:
        return self._broker.request_queue(owner_id, queue_name, timeout)

    @expose
    def release_queue(self, qname: str) -> None:
        return self._broker.release_queue(qname)

    @expose
    def register_queue(self, queue_name: str) -> None:
        return self._broker.register_queue(queue_name)

    @expose
    def get_owned_queues(self) -> Dict[str, Tuple[int, float]]:
        return self._broker.get_owned_queues()

    @expose
    def deregister_queue(self, queue_name: str) -> None:
        return self._broker.deregister_queue(queue_name)

    # Exposed shared memory methods
    @expose
    def append_shared_memory_name(self, name: str) -> None:
        self._shared_memory_names.append(name)

    @expose
    def remove_shared_memory_name(self, name: str) -> bool:
        try:
            self._shared_memory_names.remove(name)
            return True
        except ValueError:
            return False

    @expose
    def get_shared_memory_names(self) -> List[str]:
        return self._shared_memory_names

    @expose
    def get_shared_memory_size(self) -> int:
        return self._shared_memory_size

    @expose
    def set_shared_memory_size(self, size: int) -> None:
        self._shared_memory_size = size

    # Exposed manager methods
    @expose
    def get_manager_pid(self) -> int:
        return self._pid

    @expose
    def get_exporter_pid(self) -> int:
        return self._exporter_pid

    @expose
    def set_exporter_pid(self, pid: int) -> None:
        self._exporter_pid = pid

    @expose
    def get_remote_config(
        self, session_key: SessionKeyType
    ) -> Optional["RemoteConfig"]:
        return self._remote_config.get(session_key)

    @expose
    def set_remote_config(
        self, session_key: SessionKeyType, config: "RemoteConfig"
    ) -> None:
        self._remote_config[session_key] = config

    # Exposed process and session management methods
    @expose
    def get_connected_processes(self) -> ProcessInfo:
        return self._connected_processes

    @expose
    def set_connected_process(self, pid: int, session_key: SessionKeyType) -> None:
        self._connected_processes[pid] = session_key

    @expose
    def get_disconnected_process(self) -> ProcessInfo:
        return self._disconnected_processes

    @expose
    def set_disconnected_process(self, pid: int) -> None:
        self._disconnected_processes[pid] = self._connected_processes[pid]

    @expose
    def get_sessions(self) -> SessionInfo:
        return self._sessions

    @expose
    def set_session(self, session_key: SessionKeyType, session_id: str) -> None:
        self._sessions[session_key] = session_id

    @expose
    def del_session(self, session_key: SessionKeyType) -> None:
        try:
            del self._sessions[session_key]
        except KeyError:
            pass

    @expose
    def get_session_id(self, pid: int) -> Optional[str]:
        session_key = self._connected_processes.get(pid)
        if session_key is None:
            return None
        return self._sessions.get(session_key)

    @expose
    def set_throttled(self, pid: int) -> None:
        self._throttled_pids.add(pid)

    @expose
    def is_throttled(self, pid: int) -> bool:
        return pid in self._throttled_pids


T = TypeVar("T")
G = TypeVar("G")

AsyncFuncType = TypeVar("AsyncFuncType", bound=Callable[..., Coroutine[Any, Any, T]])
FuncType = TypeVar("FuncType", bound=Callable[..., Any])


@overload
def wrap_in_manager_exception(
    func: AsyncFuncType,
) -> AsyncFuncType: ...


@overload
def wrap_in_manager_exception(func: FuncType) -> FuncType: ...


def wrap_in_manager_exception(
    func: Union[FuncType, Callable[..., Coroutine[Any, Any, T]], Callable[..., T]],
) -> Callable[..., Any]:
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)  # type: ignore[no-any-return]
            except AttributeError:
                # Used for hasattr checks
                raise
            except Exception as e:
                raise ManagerException("Exception in manager call") from e

    else:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)  # type: ignore[return-value]
            except AttributeError:
                # Used for hasattr checks
                raise
            except Exception as e:
                raise ManagerException("Exception in manager call") from e

    return wrapper


class SharedMemory:
    def __init__(self, mmap_obj: mmap.mmap, file_obj: BinaryIO, file_name: str) -> None:
        self.mmap_obj = mmap_obj
        self.file_obj = file_obj
        self.file_name = file_name

    def close(self) -> None:
        self.mmap_obj.close()
        self.file_obj.close()

    def open(self) -> str:
        return self.file_name


class Manager(BaseManager):
    _cached_shared_memory_size: int
    _cached_exporter_pid: int
    _cached_manager_pid: int
    _cached_config: SessionRemoteConfig
    _cached_state: ManagerState
    _cached_session_key: SessionKeyType

    def __init__(
        self, address: Tuple[str, int], authkey: bytes, *args: Any, **kargs: Any
    ) -> None:
        super().__init__(address, authkey, *args, **kargs)

    @wrap_in_manager_exception
    def init_manager(self, exporter_pid: int, shared_memory_size: int) -> None:
        self.state_proxy.set_exporter_pid(exporter_pid)
        self.state_proxy.set_shared_memory_size(shared_memory_size)

    @property
    @wrap_in_manager_exception
    def shared_memory_size(self) -> int:
        if not hasattr(self, "_cached_shared_memory_size"):
            self._cached_shared_memory_size = self.state_proxy.get_shared_memory_size()
        return self._cached_shared_memory_size

    @shared_memory_size.setter
    @wrap_in_manager_exception
    def shared_memory_size(self, size: int) -> None:
        self._cached_shared_memory_size = size
        self.state_proxy.set_shared_memory_size(size)

    @wrap_in_manager_exception
    def create_shared_memory(self, name: str) -> SharedMemory:
        filename = os.path.join(tempfile.gettempdir(), "hud_{}".format(name))
        with open(filename, "wb") as file:
            file.truncate(self.shared_memory_size)
            file.flush()
        shared_memory_file = open(filename, "r+b")  # type: BinaryIO
        mm = mmap.mmap(shared_memory_file.fileno(), self.shared_memory_size)
        self.state_proxy.append_shared_memory_name(filename)
        self.state_proxy.register_queue(filename)
        return SharedMemory(mm, shared_memory_file, filename)

    @wrap_in_manager_exception
    def delete_shared_memory(self, name: str) -> None:
        removed = self.state_proxy.remove_shared_memory_name(name)
        if removed:
            self.state_proxy.deregister_queue(name)
            if os.path.exists(name):
                os.remove(name)

    @wrap_in_manager_exception
    def get_shared_memories(self) -> Dict[str, SharedMemory]:
        shared_memory_names = self.state_proxy.get_shared_memory_names()
        shared_memory_files = {}
        for name in shared_memory_names:
            try:
                shared_memory_file = open(name, "r+b")
                mm = mmap.mmap(shared_memory_file.fileno(), self.shared_memory_size)
                shared_memory_files[name] = SharedMemory(mm, shared_memory_file, name)
            except FileNotFoundError:
                pass
        return shared_memory_files

    @wrap_in_manager_exception
    def get_shared_memory(self, name: str) -> Optional[SharedMemory]:
        try:
            shared_memory_file = open(name, "r+b")
            mm = mmap.mmap(shared_memory_file.fileno(), self.shared_memory_size)
            return SharedMemory(mm, shared_memory_file, name)
        except FileNotFoundError:
            return None

    @wrap_in_manager_exception
    def get_shared_memory_names(self) -> List[str]:
        return self.state_proxy.get_shared_memory_names()

    @wrap_in_manager_exception
    def get_connected_processes(self) -> ProcessInfo:
        return self.state_proxy.get_connected_processes()

    @property
    @wrap_in_manager_exception
    def exporter_pid(self) -> int:
        if not hasattr(self, "_cached_exporter_pid"):
            self._cached_exporter_pid = self.state_proxy.get_exporter_pid()
        return self._cached_exporter_pid

    @exporter_pid.setter
    @wrap_in_manager_exception
    def exporter_pid(self, pid: int) -> None:
        self._cached_exporter_pid = pid
        self.state_proxy.set_exporter_pid(pid)

    @wrap_in_manager_exception
    def register_process(self, pid: int, session_key: SessionKeyType) -> None:
        self._cached_session_key = session_key
        self.state_proxy.set_connected_process(pid, session_key)

    @wrap_in_manager_exception
    def deregister_process(self, pid: int) -> None:
        self.state_proxy.set_disconnected_process(pid)

    @wrap_in_manager_exception
    def get_deregistered_processes(self) -> ProcessInfo:
        return self.state_proxy.get_disconnected_process()

    @wrap_in_manager_exception
    def register_session(self, session_key: SessionKeyType, session_id: str) -> None:
        self.state_proxy.set_session(session_key, session_id)

    @wrap_in_manager_exception
    def deregister_session(self, session_key: SessionKeyType) -> None:
        self.state_proxy.del_session(session_key)

    @property
    @wrap_in_manager_exception
    def manager_pid(self) -> int:
        if not hasattr(self, "_cached_manager_pid"):
            self._cached_manager_pid = self.state_proxy.get_manager_pid()
        return self._cached_manager_pid

    @property
    @wrap_in_manager_exception
    def session_id(self) -> Optional[str]:
        return self.state_proxy.get_session_id(get_current_pid())

    @property
    @wrap_in_manager_exception
    def updated_config(self) -> "Optional[RemoteConfig]":
        return self.state_proxy.get_remote_config(self._cached_session_key)

    @wrap_in_manager_exception
    def set_updated_config(
        self, session_key: SessionKeyType, config: "dict[str, Union[List[str], int]]"
    ) -> None:
        if not hasattr(self, "_cached_config"):
            self._cached_config = {}
        cached_config = self._cached_config.get(session_key, {})
        if config != cached_config:
            self.state_proxy.set_remote_config(
                session_key, {"config": config, "id": str(uuid.uuid4())}
            )
            self._cached_config[session_key] = config

    @property
    @wrap_in_manager_exception
    def state_proxy(self) -> ManagerState:
        if not hasattr(self, "_cached_state"):
            self._cached_state = self._get_state()
        return self._cached_state

    # Safe broker methods
    @wrap_in_manager_exception
    def request_queue(
        self, owner_id: int, queue_name: Optional[str] = None, timeout: float = 0.0
    ) -> Optional[str]:
        return self.state_proxy.request_queue(owner_id, queue_name, timeout)

    @wrap_in_manager_exception
    def release_queue(self, qname: str) -> None:
        return self.state_proxy.release_queue(qname)

    @wrap_in_manager_exception
    def register_queue(self, queue_name: str) -> None:
        return self.state_proxy.register_queue(queue_name)

    @wrap_in_manager_exception
    def get_owned_queues(self) -> Dict[str, Tuple[int, float]]:
        return self.state_proxy.get_owned_queues()

    @wrap_in_manager_exception
    def deregister_queue(self, queue_name: str) -> None:
        return self.state_proxy.deregister_queue(queue_name)

    @wrap_in_manager_exception
    def set_throttled(self, pid: int) -> None:
        self.state_proxy.set_throttled(pid)

    @wrap_in_manager_exception
    def is_throttled(self) -> bool:
        return self.state_proxy.is_throttled(os.getpid())

    def _get_state(self) -> ManagerState:
        raise NotImplementedError()


_state: Optional[ManagerState] = None


def _get_state() -> ManagerState:
    global _state
    if _state is None:
        _state = ManagerState()
    return _state


Manager.register(
    "_get_state", callable=_get_state, exposed=ManagerState.exposed_methods
)


def get_manager(address: Tuple[str, int], authkey: Any = None) -> Manager:
    return Manager(address, authkey, ctx=multiprocessing.get_context("spawn"))
