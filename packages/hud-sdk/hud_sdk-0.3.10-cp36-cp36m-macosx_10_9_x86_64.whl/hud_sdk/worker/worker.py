import contextlib
import json
import os
import random
import signal
import subprocess
import threading
import time
import uuid
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from .. import globals, standby_mode
from .._internal import worker_queue
from ..collectors import PerformanceMonitor, get_loaded_modules, runtime_info
from ..collectors.modules import get_installed_packages
from ..config import config
from ..declarations import FilesAggregator, FileToParse
from ..endpoint_manager import EndpointsDeclarationsAggregator
from ..exporter.manager.errors import ManagerException
from ..exporter.manager.manager import Manager, SharedMemory, get_manager
from ..exporter.queue import BaseInfoStructure, BufferBackedCyclicQueue
from ..exporter.status import get_exporter_status, is_exporter_alive, wait_for_exporter
from ..forkable import ForksafeSequence, after_fork_in_child
from ..hook import set_hook
from ..invocations_handler import InvocationsHandler
from ..kafka_declaration_manager import KafkaDeclarationsAggregator
from ..logging import internal_logger, send_logs_handler, user_logger
from ..native import get_hud_running_mode
from ..process_utils import get_current_pid, is_alive
from ..run_mode import (
    HudRunningMode,
    disable_hud,
    get_hud_enable,
    should_run_hud,
    valid_hud_enable,
)
from ..schemas.events import (
    EndpointDeclaration,
    KafkaDeclaration,
    PreInitLoadedModules,
)
from ..user_options import UserOptions, init_user_options
from ..users_logs import UsersLogs
from ..utils import (
    dump_logs_sync,
    find_python_binary,
    suppress_exceptions_sync,
)
from ..workload_metadata import get_cpu_limit

worker_thread: Optional[threading.Thread] = None
standby_thread: Optional[threading.Thread] = None


def should_run_worker() -> bool:
    return bool(
        get_hud_running_mode() == HudRunningMode.ENABLED
        and worker_thread
        and not should_finalize_worker(worker_thread)
    )


def should_finalize_worker(worker_thread: threading.Thread) -> bool:
    for thread in threading.enumerate():
        if thread == worker_thread:
            continue
        if (
            not thread.daemon
            and thread.is_alive()
            and thread.name != "pydevd.CheckAliveThread"
        ):
            return False
    internal_logger.info("All threads are done, finalizing worker")
    return True


T = TypeVar("T")


def disable_on_manager_exception(func: Callable[..., T]) -> Callable[..., T]:

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except ManagerException:
            internal_logger.critical(
                "Disabling Hud due to exception in manager function",
                exc_info=True,
                data={"function": getattr(func, "__name__", None)},
            )
            user_logger.log(*UsersLogs.HUD_FAILED_TO_COMMUNICATE_WITH_MANAGER)
            disable_hud(
                should_dump_logs=False,
                should_clear=False,
            )
            raise

    return sync_wrapper


class QueueInfo:
    def __init__(
        self,
        shared_memory: SharedMemory,
        queue: BufferBackedCyclicQueue[BaseInfoStructure],
    ) -> None:
        self.shared_memory = shared_memory
        self.queue = queue


class Task:
    def __init__(
        self,
        func: Callable[[], None],
        interval_factory: Callable[[], float],
        initial_time: float,
        first_run_delay: Optional[float] = None,
    ) -> None:
        self.interval_factory = interval_factory
        interval = interval_factory()
        self.func = func
        self.last_run = initial_time
        self.already_ran = False
        first_run_delay = first_run_delay if first_run_delay is not None else interval
        self.first_run_delay = (
            initial_time + random.randint(0, int(first_run_delay)) - first_run_delay
        )

    def run(self, time: float) -> bool:
        interval = self.interval_factory()
        if not self.already_ran:
            if time - self.last_run >= self.first_run_delay:
                self.already_ran = True
                self.last_run = time
                suppress_exceptions_sync(lambda: None)(
                    disable_on_manager_exception(self.func)
                )()
                return True
        elif time - self.last_run >= interval:
            self.last_run = time
            suppress_exceptions_sync(lambda: None)(
                disable_on_manager_exception(self.func)
            )()
            return True
        return False


class Worker:

    def __init__(
        self,
        user_options: UserOptions,
    ) -> None:
        self.user_options = user_options
        self.files = FilesAggregator()
        self.endpoints_declarations = EndpointsDeclarationsAggregator()
        self.kafka_declarations = KafkaDeclarationsAggregator()
        self.invocations_handler = InvocationsHandler()
        self.performance_monitor = PerformanceMonitor("worker", get_cpu_limit())
        self.manager: Optional[Manager] = None
        self.tasks: List[Task] = []
        self.manager_pid: Optional[int] = None
        self.session_id: Optional[str] = None
        self.session_id_timeout = config.worker_session_id_timeout
        self.did_dump_metrics = False
        self._queues: Dict[str, QueueInfo] = {}
        self.remote_config_id: Optional[str] = None
        self.exporter_info = get_exporter_status(unique_id=config.exporter_unique_id)
        self.worker_pid = os.getpid()

    def cleanup(self) -> None:
        with contextlib.suppress(Exception):
            self.close_shared_memories(should_delete=False)

    def _start_exporter(self) -> bool:
        # Make sure to log to the user every False flow!
        if not is_exporter_alive(self.exporter_info):
            executable = find_python_binary()
            if not executable:
                internal_logger.critical("Python executable not found")
                if is_main_process:
                    user_logger.log(*UsersLogs.HUD_PYTHON_EXECUTABLE_NOT_FOUND)
                return False
            if not self.run_exporter(executable):
                if is_main_process:
                    user_logger.log(*UsersLogs.HUD_RUN_EXPORTER_FAILED)
                return False
        return True

    def _open_shared_memories(self) -> None:
        if not self.manager:
            internal_logger.critical("Manager is not set")
            return

        for name, shared_memory in self.manager.get_shared_memories().items():
            shared_memory.open()
            queue = BufferBackedCyclicQueue(
                shared_memory.mmap_obj,
                BaseInfoStructure,
                shared_memory.mmap_obj.size(),
            )
            self._queues[name] = QueueInfo(shared_memory, queue)

    def _setup(self) -> bool:
        # Make sure to log to the user every False flow!
        internal_logger.info("Starting worker")
        try:
            if not self._start_exporter():
                # All the False flows are logged in the function
                internal_logger.critical("Failed to start exporter")
                return False
        except Exception:
            user_logger.log(*UsersLogs.HUD_RUN_EXPORTER_FAILED)
            internal_logger.critical("Failed to start exporter", exc_info=True)
            return False

        try:
            if not self.connect():
                internal_logger.critical("Failed to connect to manager")
                user_logger.log(*UsersLogs.HUD_FAILED_TO_CONNECT_TO_MANAGER)
                return False
        except Exception:
            internal_logger.critical("Failed to connect to manager", exc_info=True)
            user_logger.log(*UsersLogs.HUD_FAILED_TO_CONNECT_TO_MANAGER)
            return False

        try:
            if not self.manager:
                internal_logger.critical("Manager is not set")
                user_logger.log(*UsersLogs.HUD_NO_MANAGER)
                return False
        except Exception:
            internal_logger.critical("Manager is not set", exc_info=True)
            user_logger.log(*UsersLogs.HUD_NO_MANAGER)
            return False

        try:
            self.manager.register_process(
                os.getpid(),
                (
                    self.user_options.key,
                    self.user_options.service,
                    frozenset(self.user_options.tags.items()),
                ),
            )
            self.manager_pid = self.manager.manager_pid
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_REGISTER_PROCESSES)
            internal_logger.critical("Failed to register process", exc_info=True)
            return False

        if self.manager.is_throttled():
            internal_logger.info("HUD is throttled, shutting down")
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_THROTTLED)
            disable_hud(False, should_clear=False)
            return False

        self.session_id = self.manager.session_id

        if not standby_mode.is_first_active_session_id_set():
            standby_mode.set_first_active_session_id(self.session_id)

        if self.session_id and is_main_process:
            user_logger.log(*UsersLogs.HUD_INITIALIZED_SUCCESSFULLY)

        try:
            self._open_shared_memories()
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_OPEN_SHARED_MEMORIES)
            internal_logger.critical("Failed to open shared memories", exc_info=True)
            return False

        try:
            self.register_tasks()
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_REGISTER_TASKS)
            internal_logger.critical("Failed to register tasks", exc_info=True)
            return False

        try:
            self._send_installed_packages()
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_COMMUNICATE_WITH_MANAGER)
            internal_logger.exception("Failed to send installed packages")

        internal_logger.info("Worker started")
        try:
            self._send_runtime()  # We need to send the runtime only once
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_COMMUNICATE_WITH_MANAGER)
            internal_logger.exception("Failed to send runtime")

        return True

    def run(self) -> None:
        with internal_logger.stage_context("setup"):
            setup_success = self._setup()

        if not setup_success:
            return

        with internal_logger.stage_context("loop"):
            while True:
                if not should_run_worker():
                    with internal_logger.stage_context("finalize"):
                        self._finalize()
                        break
                waketime = time.time()
                for task in self.tasks:
                    if not get_hud_running_mode() == HudRunningMode.ENABLED:
                        break
                    if task.run(waketime):
                        time.sleep(0.01)
                time.sleep(1)

    def run_exporter(self, executable: str) -> bool:
        try:
            env = os.environ.copy()
            python_path = env.get("PYTHONPATH", "")
            if "ddtrace" in python_path or config.sdk_name in python_path:
                # When running with ddtrace-run, gevent is imported in the exporter process, which causes it to never exit
                python_path_parts = python_path.split(os.path.pathsep)
                python_path_parts = [
                    part
                    for part in python_path_parts
                    if "ddtrace" not in part and config.sdk_name not in part
                ]
                env["PYTHONPATH"] = os.path.pathsep.join(python_path_parts)
            env["HUD_EXPORTER"] = "1"
            networkprocess = subprocess.Popen(
                [
                    executable,
                    "-m",
                    "{}.exporter".format(config.sdk_name),
                    str(uuid.uuid4()),
                ],
                start_new_session=True,
                env=env,
            )
            time.sleep(0.4)
            if (
                networkprocess.poll() is not None
                and networkprocess.returncode
                != config.exporter_already_running_status_code
            ):
                internal_logger.error("Failed to run exporter, process exited")
                return False
        except Exception:
            internal_logger.exception("Failed to run exporter")
            return False

        status = wait_for_exporter(
            unique_id=config.exporter_unique_id,
            early_stop_predicate=lambda t: (
                not should_run_worker()
                if t > config.exporter_minimum_start_timeout
                else False
            ),
        )
        if not status:
            internal_logger.error("Timed out waiting for exporter to start")
            return False
        self.exporter_info = status
        return True

    def connect(self) -> bool:
        manager_port = self.get_manager_port()
        if not manager_port:
            internal_logger.error("Manager port not found")
            return False
        self.manager = get_manager(("localhost", manager_port), config.manager_password)
        self.manager.connect()
        internal_logger.info("Connected to manager")
        return True

    def get_manager_port(self) -> Optional[int]:
        cur_time = start_time = time.time()
        while cur_time - start_time < config.wait_for_manager_port_timeout:
            if not get_hud_running_mode() == HudRunningMode.ENABLED:
                internal_logger.warning("HUD is not enabled, stopping worker")
                return None
            if (
                not should_run_worker()
                and cur_time - start_time > config.min_time_for_manager_port
            ):
                # We want to give grace period to the exporter to start if the main thread has finished
                internal_logger.warning(
                    "Worker stopped before getting manager port",
                    data={"seconds": cur_time - start_time},
                )
                return None
            if not is_exporter_alive(self.exporter_info):
                internal_logger.error(
                    "Exporter process is not running while getting manager port"
                )
                return None
            port = self.exporter_info.manager_port
            if port:
                return port
            time.sleep(0.3)
            cur_time = time.time()
            self.exporter_info = get_exporter_status()
        return None

    def _check_queues(self) -> None:
        if not self.manager:
            internal_logger.error("Manager is not set")
            return

        current_shared_memories = list(self._queues.keys())
        shared_memories = []
        try:
            shared_memories = list(self.manager.get_shared_memory_names())
        except Exception:
            internal_logger.exception("Failed to get shared memories")
            pass

        for shared_memory_name in shared_memories:
            if shared_memory_name not in current_shared_memories:
                self._register_new_queue(shared_memory_name)

        for shared_memory_name in current_shared_memories:
            if shared_memory_name not in shared_memories:
                internal_logger.info(
                    "Removing shared memory", data={"name": shared_memory_name}
                )
                queue_info = self._queues.pop(shared_memory_name, None)
                if queue_info is not None:
                    queue_info.shared_memory.close()

    def _register_new_queue(self, queue_name: str) -> None:
        if not self.manager:
            internal_logger.error("Manager is not set")
            return
        shared_memory = self.manager.get_shared_memory(queue_name)
        if not shared_memory:
            internal_logger.error(
                "Failed to get shared memory", data={"queue": queue_name}
            )
            return
        shared_memory.open()
        queue = BufferBackedCyclicQueue(
            shared_memory.mmap_obj,
            BaseInfoStructure,
            shared_memory.mmap_obj.size(),
        )
        self._queues[queue_name] = QueueInfo(shared_memory, queue)

    def write(self, events: Union[Dict[Any, Any], List[Any]], event_type: str) -> None:
        try:
            if event_type != "Logs":
                internal_logger.debug(
                    "Writing events to queue", data={"type": event_type}
                )
            if not self.manager:
                internal_logger.error("Manager is not set")
                return

            data = json.dumps([events, event_type, self.worker_pid]).encode()
            queue_name = self.manager.request_queue(get_current_pid(), timeout=8)
            if not queue_name:
                internal_logger.error("Failed to get queue name")
                return

            if queue_name not in self._queues:
                internal_logger.info("Registering new queue", data={"name": queue_name})
                self._register_new_queue(queue_name)

            try:
                self._queues[queue_name].queue.push(data)
            finally:
                self.manager.release_queue(queue_name)
        except Exception:
            internal_logger.exception("Failed to write events to queue")
            raise

    def register_tasks(self) -> None:
        current_time = time.time()
        self.tasks.append(
            Task(
                lambda: self.process_queue(worker_queue),
                lambda: config.process_queue_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._set_session_id,
                lambda: config.session_id_refresh_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_files,
                lambda: config.declarations_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_endpoint_declarations,
                lambda: config.declarations_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_kafka_declarations,
                lambda: config.declarations_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_invocations,
                lambda: config.invocations_flush_interval,
                current_time,
                first_run_delay=config.invocations_first_send_delay,
            )
        )
        self.tasks.append(
            Task(
                self._dump_flow_metrics,
                lambda: config.flow_metrics_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(self._dump_logs, lambda: config.logs_flush_interval, current_time)
        )
        self.tasks.append(
            Task(
                self._send_performance,
                lambda: config.performance_report_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._send_loaded_modules,
                lambda: config.modules_report_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._check_exporter,
                lambda: config.exporter_is_up_check_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._check_queues,
                lambda: config.worker_check_queues_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._update_configuration,
                lambda: config.worker_configuration_update_check_interval,
                current_time,
            )
        )

    def _update_configuration(self) -> None:
        if not self.manager:
            internal_logger.error("Manager is not set")
            return
        configuration = self.manager.updated_config
        if not configuration:
            return

        if configuration["id"] == self.remote_config_id:
            return
        internal_logger.info("Updating configuration", data=configuration)
        self.remote_config_id = configuration["id"]
        config._update_updatable_keys(configuration["config"])

    def process_queue(self, queue: ForksafeSequence[Sequence[Any]]) -> None:
        qsize = len(queue)
        if not qsize:
            return
        if hasattr(queue, "maxlen") and queue.maxlen == qsize:
            internal_logger.error("Event queue is full")
        try:
            for item in iter(queue.popleft, None):
                if isinstance(item, FileToParse):
                    self.files.add_file(item)
                elif isinstance(item, EndpointDeclaration):
                    self.endpoints_declarations.add_declaration(item)
                elif isinstance(item, KafkaDeclaration):
                    self.kafka_declarations.add_declaration(item)
                elif isinstance(item, PreInitLoadedModules):
                    self.write(item.to_json_data(), item.get_type())
                else:
                    internal_logger.error(
                        "Invalid item type", data={"type": type(item)}
                    )
                qsize -= 1
                if qsize == 0:
                    break
        except IndexError:
            pass

    def _set_session_id(self) -> None:
        if self.session_id:
            return
        if not self.manager:
            internal_logger.error("Manager is not set")
            return
        try:
            session_id = self.session_id = self.manager.session_id
        except Exception:
            internal_logger.exception("Failed to get session id")
            raise
        if self.manager.is_throttled():
            internal_logger.info("HUD is throttled, shutting down")
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_THROTTLED)
            disable_hud(False, should_clear=False)
            return
        if session_id:
            internal_logger.info("Session id set", data={"session_id": self.session_id})

            if not standby_mode.is_first_active_session_id_set():
                standby_mode.set_first_active_session_id(self.session_id)

            if is_main_process and get_hud_running_mode() == HudRunningMode.ENABLED:
                # We don't want to log success if we got disabled
                user_logger.log(*UsersLogs.HUD_INITIALIZED_SUCCESSFULLY)

    def _finalize(self) -> None:
        if get_hud_running_mode() == HudRunningMode.DISABLED:
            internal_logger.info("HUD has been disabled, skipping finalization")
            return
        internal_logger.info("Finalizing worker")
        cleanup_tasks: List[Callable[[], None]] = [
            lambda: self.process_queue(worker_queue),
            lambda: self._dump_files(),
            lambda: self._dump_endpoint_declarations(),
            lambda: self._dump_kafka_declarations(),
            lambda: self._dump_invocations(),
            lambda: self._dump_flow_metrics(),
            lambda: dump_logs_sync(self.session_id),
        ]

        for cleanup_task in cleanup_tasks:
            try:
                cleanup_task()
            except Exception:
                internal_logger.exception(
                    "Failed to run cleanup task", data={"task": cleanup_task.__name__}
                )

    def _dump_files(self) -> None:
        latest_files = self.files.get_and_clear_files()
        if latest_files:
            files = [file.to_json_data() for file in latest_files]
            self.write(files, type(latest_files[0]).__name__)

    def _dump_endpoint_declarations(self) -> None:
        latest_declarations = self.endpoints_declarations.get_and_clear_declarations()
        if latest_declarations:
            declarations = [
                declaration.to_json_data() for declaration in latest_declarations
            ]
            self.write(declarations, latest_declarations[0].get_type())

    def _dump_kafka_declarations(self) -> None:
        latest_declarations = self.kafka_declarations.get_and_clear_declarations()
        if latest_declarations:
            declarations = [
                declaration.to_json_data() for declaration in latest_declarations
            ]
            self.write(declarations, latest_declarations[0].get_type())

    def _dump_invocations(self) -> None:
        invocations = self.invocations_handler.get_and_clear_invocations()
        if invocations:
            self.write(invocations, "Invocations")
            if not self.did_dump_metrics and self.session_id and is_main_process:
                user_logger.log(*UsersLogs.HUD_FIRST_METRICS_COLLECTED)
                self.did_dump_metrics = True

    def _dump_flow_metrics(self) -> None:
        if not globals.metrics_aggregator:
            internal_logger.error("Metrics aggregator is not initialized")
            return
        metrics_by_type = globals.metrics_aggregator.get_and_clear_metrics()
        for metrics in metrics_by_type.values():
            if metrics:
                self.write(
                    [metric.to_json_data() for metric in metrics], metrics[0].get_type()
                )

    def _dump_logs(self) -> None:
        logs = send_logs_handler.get_and_clear_logs()
        if logs.logs:
            try:
                self.write(logs.to_json_data(), "Logs")
            except Exception:
                internal_logger.exception(
                    "Failed to write logs to the queue, will try to dump them"
                )
                new_logs = (
                    send_logs_handler.get_and_clear_logs()
                )  # For getting the logs of the exception, and not making it in the next run
                logs.logs.extend(new_logs.logs)
                dump_logs_sync(self.session_id)
                raise

    def _send_loaded_modules(self) -> None:
        modules = get_loaded_modules()
        self.write(modules.to_json_data(), modules.get_type())

    def _send_installed_packages(self) -> None:
        installed_packages = get_installed_packages()
        self.write(installed_packages.to_json_data(), installed_packages.get_type())

    def _send_performance(self) -> None:
        performance = self.performance_monitor.monitor_process()
        if config.log_performance:
            internal_logger.info("performance data", data=performance.to_json_data())
        self.write(performance.to_json_data(), performance.get_type())

    def _send_runtime(self) -> None:
        runtime = runtime_info()
        self.write(runtime.to_json_data(), runtime.get_type())

    def _check_exporter(self) -> None:
        if not self.exporter_info or not is_exporter_alive(self.exporter_info):
            internal_logger.critical("Exporter is not running, shutting down")
            self.close_shared_memories(should_delete=True)
            self.kill_manager_gracefully()

            disable_hud(
                should_dump_logs=True,
                session_id=self.session_id,
            )

    def kill_manager_gracefully(self) -> None:
        if self.manager and self.manager_pid and is_alive(self.manager_pid):
            try:
                internal_logger.info("Sending SIGTERM to manager process")
                os.kill(self.manager_pid, signal.SIGTERM)

                timeout = 5
                poll_interval = 0.5

                start_time = time.time()
                while time.time() - start_time < timeout:
                    if not is_alive(self.manager_pid):
                        internal_logger.info("Manager process exited")
                        return
                    time.sleep(poll_interval)

                internal_logger.warning(
                    "Manager process did not exit, sending SIGKILL."
                )
                os.kill(self.manager_pid, signal.SIGKILL)

            except Exception:
                internal_logger.exception("Error terminating manager process")

    def close_shared_memories(self, should_delete: bool) -> None:
        for queue_info in self._queues.values():
            try:
                queue_info.shared_memory.close()
                if should_delete:
                    if os.path.exists(queue_info.shared_memory.file_name):
                        os.remove(queue_info.shared_memory.file_name)
            except Exception:
                if os.path.exists(queue_info.shared_memory.file_name):
                    internal_logger.exception("Failed to close shared memory")
        self._queues.clear()


def start_worker_thread(user_options: UserOptions) -> None:
    global worker_thread

    def target() -> None:
        worker = Worker(user_options)
        try:
            worker.run()
        except Exception:
            user_logger.log(
                *UsersLogs.HUD_EXCEPTION_IN_WORKER,
            )
            internal_logger.exception("Exception in worker thread target")
        finally:
            with internal_logger.stage_context("cleanup"):
                worker.cleanup()
                with contextlib.suppress(Exception):
                    if (
                        worker.manager
                        and not get_hud_running_mode() == HudRunningMode.ENABLED
                    ):
                        worker.manager.deregister_process(os.getpid())
                if not get_hud_running_mode() == HudRunningMode.STANDBY:
                    disable_hud(
                        should_dump_logs=True,
                        session_id=worker.session_id,
                    )

    worker_thread = threading.Thread(target=target)
    worker_thread.start()


registered_after_fork = False
is_main_process = True


def init_hud_thread_in_fork(
    key: Optional[str] = None,
    service: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    standby_callback: Optional[Callable[[], bool]] = None,
    standby_check_interval: Optional[float] = None,
) -> None:
    global is_main_process
    is_main_process = False
    global worker_thread
    worker_thread = None
    global standby_thread
    standby_thread = None
    init_hud_thread(
        key,
        service,
        tags,
        standby_callback=standby_callback,
        standby_check_interval=standby_check_interval,
    )


def init_hud_thread(
    key: Optional[str] = None,
    service: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    *,
    standby_callback: Optional[Callable[[], bool]] = None,
    standby_check_interval: Optional[float] = None,
) -> None:
    internal_logger.set_component("main")

    start_time = time.time()

    global registered_after_fork
    if config.run_after_fork and not registered_after_fork:
        registered_after_fork = True
        after_fork_in_child.register_callback(
            lambda: init_hud_thread_in_fork(
                key, service, tags, standby_callback, standby_check_interval
            )
        )

    user_logger.set_is_main_process(is_main_process)

    set_hook()  # Ensure the hook is set before starting the worker thread

    global standby_thread
    global worker_thread
    is_standby_thread_running = standby_thread is not None and standby_thread.is_alive()
    is_worker_thread_running = worker_thread is not None and worker_thread.is_alive()

    if is_standby_thread_running:
        if is_worker_thread_running:
            internal_logger.info("Worker and standby threads are already running")
            return
    else:
        if (
            not standby_callback
            and not standby_check_interval
            and is_worker_thread_running
        ):
            internal_logger.info("Worker thread is already running")
            return

    if not should_run_hud():
        if is_main_process:
            hud_enable = get_hud_enable()
            if not hud_enable:
                user_logger.log(*UsersLogs.HUD_ENABLE_NOT_SET)
            elif not valid_hud_enable(hud_enable):
                user_logger.log(*UsersLogs.HUD_ENABLE_INVALID)
        disable_hud(should_dump_logs=False)
        return

    user_options = init_user_options(key, service, tags, is_main_process)

    if (
        user_options.key is None
        or user_options.service is None
        or user_options.tags is None
    ):
        disable_hud(
            should_dump_logs=False,
            should_clear=True,
        )
        return

    if not standby_mode.validate_standby_arguments(
        standby_callback, standby_check_interval
    ):
        disable_hud(
            should_dump_logs=False,
            should_clear=True,
        )
        return

    threading.Thread(
        target=non_blocking_threads_creation,
        args=(
            start_time,
            user_options,
            is_standby_thread_running,
            standby_callback,
            standby_check_interval,
        ),
    ).start()


def non_blocking_threads_creation(
    start_time: float,
    user_options: UserOptions,
    is_standby_thread_running: bool,
    standby_callback: Union[Callable[[], bool], None],
    standby_check_interval: Union[float, None],
) -> None:
    """
    The starting of both worker and standby threads rely on
    the execution of the user's standby_callback function
    (done in `standby_mode.init_standby_thread`),
    which can be blocking.
    We don't want to block the user's code during hud's initialization,
    so we run the callback in a separate thread, then create the other threads accordingly.
    """
    global standby_thread
    global worker_thread
    if standby_callback and standby_check_interval and not is_standby_thread_running:
        standby_thread = standby_mode.init_standby_thread(
            standby_callback, standby_check_interval, user_options
        )

        if not standby_thread:
            disable_hud(
                should_dump_logs=False,
                should_clear=True,
            )
            return

    if get_hud_running_mode() == HudRunningMode.ENABLED:
        start_worker_thread(user_options)

    internal_logger.info("HUD initialized", data={"duration": time.time() - start_time})
