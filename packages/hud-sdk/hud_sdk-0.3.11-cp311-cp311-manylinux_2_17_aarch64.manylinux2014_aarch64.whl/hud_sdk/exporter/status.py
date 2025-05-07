import errno
import fcntl
import json
import os
import sys
import time
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

import psutil

from ..config import config
from ..forkable import ScopedForksafeResource
from ..logging import internal_logger
from ..version import version

if TYPE_CHECKING:
    from typing import Literal


def get_status_file_path(unique_id: Optional[str] = None) -> str:
    if unique_id is None:
        unique_id = config.exporter_unique_id
    return "{}-{}-{}-{}".format(
        config.hud_exporter_status_file, version, sys.version_info.minor, unique_id
    )


def lock_fd(fd: int, lock_type: int, timeout: int) -> None:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            fcntl.flock(fd, lock_type | fcntl.LOCK_NB)
            return
        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK, errno.EINTR):
                time.sleep(0.05)
                continue
            raise

    raise TimeoutError("Could not acquire lock within {} seconds".format(timeout))


def synchronised_write(filename: str, data: bytes, timeout: int) -> None:
    # We open with 'ab' because we only lock the file after opening it. Opening with 'wb' will truncate the file.
    with ScopedForksafeResource(open(filename, "ab")) as f:
        lock_fd(f.fileno(), fcntl.LOCK_EX, timeout)
        f.seek(0)
        f.truncate(0)
        f.write(data)


def synchronised_read(filename: str, timeout: int) -> bytes:
    with ScopedForksafeResource(open(filename, "rb")) as f:
        lock_fd(f.fileno(), fcntl.LOCK_SH, timeout)
        return f.read()


class ExporterStatus:
    def __init__(self, **kwargs: Any) -> None:
        self.status = {**kwargs}

    @property
    def pid(self) -> Optional[int]:
        return cast(Optional[int], self.status.get("pid", None))

    @pid.setter
    def pid(self, value: int) -> None:
        self.status["pid"] = value

    @property
    def manager_port(self) -> Optional[int]:
        return cast(Optional[int], self.status.get("manager_port", None))

    @manager_port.setter
    def manager_port(self, value: int) -> None:
        self.status["manager_port"] = value

    @property
    def creation_id(self) -> Optional[str]:
        return cast(Optional[str], self.status.get("creation_id", None))

    @creation_id.setter
    def creation_id(self, value: str) -> None:
        self.status["creation_id"] = value

    def dump_json(self) -> bytes:
        return json.dumps(self.status).encode()


def write_initial_status(filename: str, data: bytes, timeout: int) -> bool:
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    with ScopedForksafeResource(open(filename, "a+b")) as f:
        lock_fd(f.fileno(), fcntl.LOCK_EX, timeout)
        f.seek(0)
        content = f.read()
        try:
            status = ExporterStatus(**json.loads(content.decode()))
        except json.JSONDecodeError:
            status = ExporterStatus()

        if is_exporter_alive(status):
            return False

        f.seek(0)
        f.truncate(0)
        f.write(data)
        return True


def get_exporter_status(
    timeout: int = config.exporter_status_lock_acquisition_timeout,
    unique_id: Optional[str] = None,
) -> ExporterStatus:
    status_content = b"{}"
    file_path = get_status_file_path(unique_id)
    try:
        status_content = synchronised_read(file_path, timeout)
    except TimeoutError:
        raise
    except Exception:
        return ExporterStatus()

    if status_content == b"":
        return ExporterStatus()

    return ExporterStatus(**json.loads(status_content.decode()))


def is_exporter_alive(status: ExporterStatus) -> bool:
    if status.pid is None or status.creation_id is None:
        return False
    try:
        ps = psutil.Process(status.pid)
        hud_exporter_module_name = "{}.exporter".format(config.sdk_name)
        if not ps.is_running():
            return False
        if not any(hud_exporter_module_name in seg for seg in ps.cmdline()):
            return False
        if not any(status.creation_id in seg for seg in ps.cmdline()):
            return False
        return True

    except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
        return False


def wait_for_exporter(
    timeout: int = config.exporter_start_timeout,
    wait_condition: "Union[Literal['alive'], Literal['dead']]" = "alive",
    unique_id: Optional[str] = None,
    early_stop_predicate: Optional[Callable[[float], bool]] = None,
) -> Optional[ExporterStatus]:
    if wait_condition == "alive":
        condition = True
    elif wait_condition == "dead":
        condition = False
    current_time = start_time = time.time()
    while current_time - start_time < timeout:
        if early_stop_predicate is not None and early_stop_predicate(
            current_time - start_time
        ):
            internal_logger.warning(
                "Waiting for the exporter stopped due to early stop predicate"
            )
            return None
        status = get_exporter_status(unique_id=unique_id)
        if is_exporter_alive(status) == condition:
            return status
        time.sleep(0.4)
        current_time = time.time()
    return None
