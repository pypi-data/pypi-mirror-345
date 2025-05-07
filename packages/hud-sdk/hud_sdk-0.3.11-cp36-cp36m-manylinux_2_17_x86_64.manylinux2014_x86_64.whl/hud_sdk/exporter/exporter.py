import asyncio
import contextlib
import json
import os
import signal
import time
import uuid
from collections import defaultdict
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import psutil

from ..client import (
    AsyncHandlerReturnType,
    Client,
    HudThrottledException,
    SyncHandlerReturnType,
    get_client,
)
from ..collectors.performance import PerformanceMonitor
from ..config import Config, config
from ..declarations import (
    FileToParse,
)
from ..logging import internal_logger, send_logs_handler
from ..native import get_hud_running_mode
from ..process_utils import is_alive
from ..run_mode import HudRunningMode
from ..schemas.events import WorkloadData
from ..schemas.requests import SessionlessLogs
from ..user_options import UserOptions
from ..utils import (
    suppress_exceptions_async,
    suppress_exceptions_sync,
)
from ..version import version
from ..workload_metadata import get_cpu_limit, get_workload_metadata
from .declaration_protocol_handler import process_file_declarations
from .loop_utils import ReturnType, run_in_thread
from .manager.manager import (
    Manager,
    ProcessInfo,
    SessionKeyType,
    SharedMemory,
    get_manager,
)
from .queue import BaseInfoStructure, BufferBackedCyclicQueue
from .status import (
    ExporterStatus,
    get_status_file_path,
    synchronised_write,
    write_initial_status,
)
from .task_manager import TaskManager


class QueueInfo:
    def __init__(
        self,
        queue: BufferBackedCyclicQueue[BaseInfoStructure],
        shared_memory: SharedMemory,
    ):
        self.queue = queue
        self.shared_memory = shared_memory
        self._process_task = None  # type: Optional[asyncio.Task[None]]

    @property
    def process_task(self) -> Optional["asyncio.Task[None]"]:
        return self._process_task

    @process_task.setter
    def process_task(self, task: Optional["asyncio.Task[None]"]) -> None:
        self._process_task = task


ClientRegistry = Dict[SessionKeyType, Client[AsyncHandlerReturnType]]
ConfigRegistry = Dict[SessionKeyType, Config]


class Exporter:
    def __init__(
        self,
        unique_id: Optional[str],
        loop: asyncio.AbstractEventLoop,
        creation_id: str,
    ):
        self.pid = os.getpid()
        self.run_id = str(uuid.uuid4())
        self.creation_id = creation_id
        self.unique_exporter_id = unique_id
        if self.unique_exporter_id:
            internal_logger.info(
                "Exporter started with unique id",
                data={"unique_id": self.unique_exporter_id},
            )
        self.shared_memory_size = config.exporter_shared_memory_size
        self.customer_key: Optional[str] = None
        self.sessions: ClientRegistry = {}
        self.sessions_config: ConfigRegistry = {}
        self.throttled_sessions: Set[SessionKeyType] = set()
        self.sessionless_messages: List[Tuple[Any, str]] = []
        self.messages_for_session: Dict[SessionKeyType, List[Tuple[Any, str]]] = (
            defaultdict(list)
        )
        self.messages_for_pid: Dict[int, List[Tuple[Any, str]]] = defaultdict(list)
        self.task_manager = TaskManager()
        self.status = ExporterStatus(pid=self.pid, creation_id=self.creation_id)
        self.pod_cpu_limit = get_cpu_limit()
        self.perf_monitor = PerformanceMonitor("exporter", self.pod_cpu_limit)
        self.files_to_parse: Dict[SessionKeyType, Set[FileToParse]] = defaultdict(set)
        self.manager: Optional[Manager] = None
        self._queues: Dict[str, QueueInfo] = {}
        self._connected_processes: ProcessInfo = {}
        self._disconnected_processes: List[int] = []
        self._exporter_client: Optional[
            Client[AsyncHandlerReturnType] | Client[SyncHandlerReturnType]
        ] = None
        self._manager_pid: Optional[int] = None
        self.loop = loop

        loop.set_exception_handler(exception_handler)
        loop.add_signal_handler(
            signal.SIGTERM, lambda: asyncio.create_task(self.handle_exit())
        )
        loop.add_signal_handler(
            signal.SIGINT, lambda: asyncio.create_task(self.handle_exit())
        )

    async def run_in_thread(
        self, fn: Callable[..., ReturnType], *args: Any
    ) -> ReturnType:
        return await run_in_thread(self.loop, fn, *args)

    async def handle_exit(self) -> None:
        internal_logger.info("Received termination signal, stopping exporter")
        self.stop_tasks()

    async def _update_config_from_remote(self) -> None:
        for session, client in self.sessions.items():
            await self._update_config_from_remote_for_session(session, client)

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _update_config_from_remote_for_session(
        self, session_key: SessionKeyType, client: Client[AsyncHandlerReturnType]
    ) -> None:
        remote_config = await client.get_remote_config()

        internal_logger.debug("Received remote configuration", data=remote_config)
        if not self.sessions_config.get(session_key):
            self.sessions_config[session_key] = deepcopy(config)
        self.sessions_config[session_key]._update_updatable_keys(remote_config)

        if self.manager:
            await self.run_in_thread(
                self.manager.set_updated_config,
                session_key,
                remote_config,
            )

    def enrich_data(self, data: Any, request_type: str) -> Any:
        if request_type == "Logs" and isinstance(data, dict):
            data["exporter_run_id"] = self.run_id
        return data

    async def send_json_for_session(
        self, data: Any, request_type: str, session_key: SessionKeyType
    ) -> None:
        session_config = self.sessions_config[session_key]
        if request_type in session_config.suppressed_event_types:
            internal_logger.debug(
                "Event type is suppressed, skipping sending request",
                data=dict(event_type=request_type),
            )
            return

        client = self.sessions[session_key]

        if request_type == "Logs":
            await client.send_logs_json(data, request_type)
        elif request_type == "FileToParse":
            # This is later processed in handle_file_declarations
            self.files_to_parse[session_key].update(
                set([FileToParse(**d) for d in data])
            )
        elif isinstance(data, list):
            await client.send_batch_json(data, request_type)
        elif isinstance(data, dict):
            await client.send_single_json(data, request_type)
        else:
            internal_logger.error(
                "Unsupported data type",
                data={"type": request_type},
            )

    async def handle_file_declarations(self) -> None:
        for session_key in list(self.files_to_parse.keys()):
            client = self.sessions.get(session_key)
            if client is None:
                continue
            if not self.files_to_parse[session_key]:
                continue
            files_to_parse = self.files_to_parse[session_key]
            await process_file_declarations(files_to_parse, client, self.loop)
            self.files_to_parse[session_key] = (
                self.files_to_parse[session_key] - files_to_parse
            )

    async def send_json_for_pid(self, data: Any, request_type: str, pid: int) -> None:
        session_key = self._connected_processes.get(pid)
        if session_key is None:
            self.messages_for_pid[pid].append((data, request_type))
            return
        else:
            self.messages_for_session[session_key].append((data, request_type))
            await self.send_all_json_for_session(session_key)

    async def send_all_json_for_session(self, session_key: SessionKeyType) -> None:
        client = self.sessions.get(session_key)
        if client is None:
            return

        while self.messages_for_session[session_key]:
            data, request_type = self.messages_for_session[session_key].pop()
            await self.send_json_for_session(data, request_type, session_key)

    async def send_json_for_all_sessions(self, data: Any, request_type: str) -> None:
        for session_key in self.sessions.keys():
            await self.send_json_for_session(data, request_type, session_key)

    async def _send_workload_data(self, workload_metadata: WorkloadData) -> None:
        await self.send_json_for_all_sessions(
            workload_metadata.to_json_data(), workload_metadata.get_type()
        )

    async def _handle_new_processes(self) -> None:
        if not self.manager:
            return

        processes: ProcessInfo = await self.run_in_thread(
            self.manager.get_connected_processes
        )

        new_processes = [
            (pid, session_key)
            for pid, session_key in processes.items()
            if pid not in self._connected_processes
        ]
        for pid, session_key in new_processes:
            if self.customer_key is None:
                self.customer_key = session_key[0]
                self._exporter_client = get_client(True, self.customer_key)
            elif self.customer_key != session_key[0]:
                internal_logger.error(
                    "Exporter received data from different customers",
                    data={
                        "customer_key": self.customer_key,
                        "new_customer_key": session_key[0],
                    },
                )
                continue
            self._connected_processes[pid] = session_key
            self.messages_for_session[session_key].extend(self.messages_for_pid[pid])
            self.messages_for_pid[pid] = []
            internal_logger.info(
                "New process connected",
                data={"pid": pid, "session_key": session_key},
            )
            if session_key in self.throttled_sessions:
                await self.run_in_thread(self.manager.set_throttled, pid)
                continue
            elif session_key not in self.sessions:
                await self._initialize_new_session(pid, session_key)
            await self.send_all_json_for_session(session_key)

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _initialize_new_session(
        self, pid: int, session_key: SessionKeyType
    ) -> None:
        if not self.manager:
            return
        user_options = UserOptions(
            session_key[0],
            session_key[1],
            {k: v for k, v in session_key[2]},
            is_main_process=False,
        )
        client = get_client(True, user_options)
        try:
            await client.init_session(self.run_id)
        except HudThrottledException:
            internal_logger.info(
                "Session initialization is throttled", data={"key": session_key}
            )
            await client.close()
            await self.run_in_thread(self.manager.set_throttled, pid)
            self.throttled_sessions.add(session_key)
            return
        if not client.session_id:
            internal_logger.error(
                "Failed to initialize session", data={"session_key": session_key}
            )
            return

        await self._update_config_from_remote_for_session(session_key, client)
        # We want to set the client after the config is updated
        self.sessions[session_key] = client
        await self.run_in_thread(
            self.manager.register_session,
            session_key,
            client.session_id,
        )

    async def _process_housekeeping(self) -> None:
        if not self.manager:
            return

        manager_connected_processes = await self.run_in_thread(
            self.manager.get_connected_processes
        )
        manager_deregistered_processes = await self.run_in_thread(
            self.manager.get_deregistered_processes
        )
        for pid in self._connected_processes:
            if (
                pid in manager_deregistered_processes
                and pid not in self._disconnected_processes
            ):
                internal_logger.info(
                    "Process {} has disconnected".format(pid),
                )
                self._disconnected_processes.append(pid)
            elif not is_alive(pid) and pid not in manager_deregistered_processes:
                internal_logger.info(
                    "Process {} has exited, Deregistering".format(pid),
                )
                self._disconnected_processes.append(pid)
                await self.run_in_thread(self.manager.deregister_process, pid)

        if not manager_connected_processes:
            internal_logger.error("Manager never got any connected processes")
            self.stop_tasks()

        if not (set(manager_connected_processes) - set(manager_deregistered_processes)):
            internal_logger.info("No connected processes, Shutting down")
            self.stop_tasks()

    async def _create_queue(self) -> str:
        if not self.manager:
            raise RuntimeError("Manager is not initialized")

        name = str(uuid.uuid4())
        shared_memory = await self.run_in_thread(
            self.manager.create_shared_memory, name
        )
        shared_memory.open()

        queue = BufferBackedCyclicQueue(
            shared_memory.mmap_obj,
            BaseInfoStructure,
            shared_memory.mmap_obj.size(),
        )

        self._queues[shared_memory.file_name] = QueueInfo(queue, shared_memory)
        internal_logger.debug(
            "Created new queue",
            data={"queue_name": name, "shared_memory_name": shared_memory.file_name},
        )

        return shared_memory.file_name

    async def _remove_queue(self, queue_name: str) -> None:
        queue_info = self._queues.get(queue_name)
        if not queue_info:
            internal_logger.warning(
                "Attempted to remove non-existent queue",
                data={"queue_name": queue_name},
            )
            return

        if not self.manager:
            internal_logger.error("Manager is not initialized")
            return

        try:
            await self.run_in_thread(
                self.manager.delete_shared_memory,
                queue_name,
            )
            queue_info.shared_memory.close()

            internal_logger.info(
                "Removed queue and its shared memory",
                data={
                    "queue_name": queue_name,
                    "shared_memory_name": queue_info.shared_memory.file_name,
                },
            )
        except Exception as e:
            internal_logger.warning(
                "Failed to remove queue resources",
                data={"queue_name": queue_name, "error": str(e)},
            )

        if queue_info.process_task:
            queue_info.process_task.cancel()

        del self._queues[queue_name]

    async def _check_leaked_queues(self) -> None:
        if not self.manager:
            return
        owned_queues = await self.run_in_thread(self.manager.get_owned_queues)
        for queue_name, data in owned_queues.items():
            owner, lock_time = data
            current_time = time.time()
            elapsed_time = current_time - lock_time

            if not is_alive(owner):
                internal_logger.warning(
                    "Queue has been held by process which has exited",
                    data={"queue_name": queue_name, "owner": owner},
                )
                try:
                    await self.handle_leaked_queue(queue_name)
                except Exception:
                    internal_logger.exception(
                        "Failed to handle leaked queue", data={"queue_name": queue_name}
                    )

            elif elapsed_time > config.manager_lock_critical_threshold:
                internal_logger.warning(
                    "Queue has been held by process longer than critical threshold",
                    data={
                        "queue_name": queue_name,
                        "owner": owner,
                        "critical_threshold": config.manager_lock_critical_threshold,
                    },
                )
                try:
                    await self.handle_leaked_queue(queue_name)
                except Exception:
                    internal_logger.exception(
                        "Failed to handle leaked queue", data={"queue_name": queue_name}
                    )
            elif elapsed_time > config.manager_lock_warning_threshold:
                internal_logger.warning(
                    "Queue has been held by process longer than warning threshold",
                    data={
                        "queue_name": queue_name,
                        "owner": owner,
                        "warning_threshold": config.manager_lock_warning_threshold,
                    },
                )

    async def handle_leaked_queue(self, queue_name: str) -> None:
        internal_logger.info(
            "Handling leaked queue",
            data={"queue_name": queue_name},
        )

        await self._remove_queue(queue_name)

        new_queue_name = await self._create_queue()

        task = self.task_manager.register_periodic_task(
            self.queue_processor,
            config.exporter_queue_process_interval,
            new_queue_name,
            callback=self.queue_processor,
        )
        self._queues[new_queue_name].process_task = task

        internal_logger.info(
            "Replaced corrupted queue with new queue",
            data={"old_queue": queue_name, "new_queue": new_queue_name},
        )

    def _check_exporter_disabled(self) -> None:
        if get_hud_running_mode() == HudRunningMode.DISABLED:
            internal_logger.critical("HUD is disabled, stopping exporter")
            self.stop_tasks()

    async def queue_processor(self, queue_name: str) -> None:
        if not self.manager:
            return

        result_queue_name = await self.run_in_thread(
            self.manager.request_queue,
            os.getpid(),
            queue_name,
            8,
        )
        if not result_queue_name:
            return

        try:
            utilization = self._queues[result_queue_name].queue.get_utilization()
            if utilization > config.shared_memory_utilization_warning_threshold:
                internal_logger.warning(
                    "Queue utilization is", data={"utilization": utilization}
                )
            if utilization > config.shared_memory_utilization_critical_threshold:
                internal_logger.error(
                    "Queue utilization is", data={"utilization": utilization}
                )

            while True:
                data = self._queues[result_queue_name].queue.popleft()
                if not data:
                    break
                else:
                    try:
                        data, request_type, worker_pid = json.loads(data)
                    except Exception:
                        internal_logger.exception(
                            "Failed to load data from queue. Queue state may be corrupted"
                        )
                        self.task_manager.register_task(
                            self.handle_leaked_queue, result_queue_name
                        )
                        return
                    self.enrich_data(data, request_type)
                    self.task_manager.register_task(
                        self.send_json_for_pid, data, request_type, worker_pid
                    )
        finally:
            await self.run_in_thread(
                self.manager.release_queue,
                result_queue_name,
            )

    async def _check_manager(self) -> None:
        if not self._manager_pid:
            internal_logger.critical("Manager pid is not initialized")
            self.stop_tasks()
            return
        if not is_alive(self._manager_pid):
            internal_logger.critical("Manager process has exited")
            self.stop_tasks()

    async def _dump_logs(self) -> None:
        if not self.customer_key:
            return
        logs = send_logs_handler.get_and_clear_logs()
        if not logs:
            return

        sessionless_logs = SessionlessLogs(
            logs, self.customer_key, None, {}, version, self.run_id
        )
        if not self._exporter_client:
            self.sessionless_messages.append((sessionless_logs, "SessionlessLogs"))
            return

        for data, request_type in self.sessionless_messages:
            await self._exporter_client.send_sessionless_logs_json(data, request_type)
        self.sessionless_messages.clear()
        await self._exporter_client.send_sessionless_logs_json(
            sessionless_logs.to_json_data(), "SessionlessLogs"
        )

    async def _send_performance(self) -> None:
        performance = self.perf_monitor.monitor_process()
        if config.log_performance:
            internal_logger.info("performance data", data=performance.to_json_data())
        await self.send_json_for_all_sessions(
            performance.to_json_data(), performance.get_type()
        )

    def stop_tasks(self) -> None:
        self.task_manager.stop_running_tasks()

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    def _check_existence_of_multiple_exporters(self) -> None:
        for ps in psutil.process_iter():
            try:
                if (
                    "{}.exporter".format(config.sdk_name) in ps.cmdline()
                    and ps.pid != os.getpid()
                ):
                    internal_logger.warning(
                        "Multiple exporters detected. Another exporter found",
                        data={"pid": ps.pid},
                    )
            except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
                pass

    async def _initialize_workload_metadata(self) -> None:
        workload_metadata = await get_workload_metadata(self.pod_cpu_limit)
        try:
            await self._send_workload_data(workload_metadata)
        except Exception:
            internal_logger.exception("Failed to send workload data at init")

        self.task_manager.register_periodic_task(
            self._send_workload_data,
            config.workload_data_flush_interval,
            workload_metadata,
        )

    async def _keepalive(self) -> None:
        for client in self.sessions.values():
            await client.keepalive()

    async def cleanup(self) -> None:
        with internal_logger.stage_context("cleanup"):
            internal_logger.info("Cleaning up exporter")

            for queue_name in list(self._queues.keys()):
                await self._remove_queue(queue_name)
            self._queues.clear()

            try:
                await self._dump_logs()
                # Logs after this point will not be sent to the server
            except Exception:
                internal_logger.debug(
                    "Failed to dump logs during cleanup", exc_info=True
                )

            for client in self.sessions.values():
                await client.close()
            if self._exporter_client:
                if self._exporter_client.is_async:
                    await self._exporter_client.close()
                else:
                    self._exporter_client.close()
                self._exporter_client = None

            if self.manager:
                with contextlib.suppress(Exception):
                    self.manager.shutdown()
                self.manager = None

    async def run(self) -> int:
        exporter_status_path = get_status_file_path()
        with contextlib.ExitStack() as stack:
            status = self.status
            if not write_initial_status(
                exporter_status_path,
                status.dump_json(),
                config.exporter_status_lock_acquisition_timeout,
            ):
                internal_logger.info(
                    "Exporter is already running",
                )
                return config.exporter_already_running_status_code
            manager = stack.enter_context(
                get_manager(("localhost", 0), config.manager_password)
            )
            stack.enter_context(internal_logger.stage_context("setup"))

            self.manager = manager
            manager.init_manager(self.pid, self.shared_memory_size)
            self._manager_pid = manager.manager_pid

            await self._create_queue()
            if manager.address is None:
                internal_logger.critical("Manager failed to start")
                await self.cleanup()
                return 1

            status.manager_port = manager.address[1]  # type: ignore[assignment]
            synchronised_write(
                exporter_status_path,
                status.dump_json(),
                config.exporter_status_lock_acquisition_timeout,
            )

            for _ in range(config.num_of_worker_exporter_queues - 1):
                await self._create_queue()

            internal_logger.info("Manager process fully initialized")

            self.task_manager.register_periodic_task(
                self._check_manager,
                config.exporter_manager_check_interval,
            )
            for queue_name in self._queues.keys():
                task = self.task_manager.register_periodic_task(
                    self.queue_processor,
                    config.exporter_queue_process_interval,
                    queue_name,
                    callback=self.queue_processor,
                )
                self._queues[queue_name].process_task = task

            self._check_existence_of_multiple_exporters()
            self.task_manager.register_periodic_task(
                self._check_leaked_queues,
                config.manager_leaked_queue_check_interval,
            )
            task_manager = self.task_manager
            self.loop.call_later(
                config.exporter_process_registry_warmup_period,
                lambda: task_manager.register_periodic_task(
                    self._process_housekeeping,
                    config.exporter_process_registry_update_interval,
                ),
            )
            self.task_manager.register_periodic_task(
                self._handle_new_processes,
                config.exporter_process_registry_update_interval,
            )
            self.task_manager.register_task(self._initialize_workload_metadata)

            self.task_manager.register_periodic_task(
                self._check_exporter_disabled, config.exporter_disabled_check_interval
            )
            self.task_manager.register_periodic_task(
                self._dump_logs, config.logs_flush_interval
            )
            self.task_manager.register_periodic_task(
                self._send_performance, config.performance_report_interval
            )
            self.task_manager.register_periodic_task(
                self._update_config_from_remote,
                config.exporter_configuration_update_check_interval,
            )
            self.task_manager.register_periodic_task(
                self._keepalive,
                config.exporter_configuration_update_check_interval,
            )
            self.task_manager.register_periodic_task(
                self.handle_file_declarations,
                lambda: config.declarations_flush_interval,
                callback=self.handle_file_declarations,
            )

            try:
                with internal_logger.stage_context("loop"):
                    await self.task_manager.wait_for_tasks()
                    internal_logger.info("Loop has exited gracefully")
            except Exception:
                internal_logger.exception("Exception in worker loop")
            finally:
                try:
                    await self.cleanup()
                except Exception:
                    pass
        return 0


def exception_handler(loop: asyncio.AbstractEventLoop, context: Dict[str, Any]) -> None:
    exc = context.get("exception")  # This could be None
    message = context.get("message", "No error message")

    if exc:
        internal_logger.error(
            "Exception in exporter loop",
            data={"message": message},
            exc_info=(type(exc), exc, exc.__traceback__),
        )
    else:
        internal_logger.error(
            "Exception in exporter loop with no exception object",
            data={"message": message},
        )
