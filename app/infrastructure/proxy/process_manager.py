import asyncio
import os
import signal
from datetime import datetime
from typing import Optional
from uuid import UUID

from domain.session import ProxySession, SessionStatus
from infrastructure.proxy.log_parser import LogBuffer, LogParser, stream_output

PROXY_BINARY = os.environ.get("PROXY_BINARY_PATH", "/usr/local/bin/vk-turn-proxy")
PORT_RANGE_START = int(os.environ.get("PORT_RANGE_START", "56000"))
PORT_RANGE_END = int(os.environ.get("PORT_RANGE_END", "56100"))


class ProcessManager:
    def __init__(self):
        # Only ONE global proxy process (vk-turn-proxy is multi-user)
        self._process: Optional[asyncio.subprocess.Process] = None
        self._global_session_id: Optional[UUID] = None
        self._log_buffer: LogBuffer = LogBuffer()
        self._log_parser: LogParser = LogParser()
        self._port_pool: set[int] = set(range(PORT_RANGE_START, PORT_RANGE_END + 1))
        self._used_ports: dict[UUID, int] = {}
        self._session_statuses: dict[UUID, SessionStatus] = {}
        self._monitor_tasks: list[asyncio.Task] = []
        self._lock = asyncio.Lock()

    def allocate_port(self) -> int:
        if not self._port_pool:
            raise RuntimeError("No available ports in pool")
        return self._port_pool.pop()

    def release_port(self, port: int) -> None:
        self._port_pool.add(port)

    async def start(self, session: ProxySession) -> int:
        """Start or reuse global vk-turn-proxy. Returns PID."""
        async with self._lock:
            # If process already running and alive, reuse it
            if self._process and self._process.returncode is None:
                self._session_statuses[session.id] = SessionStatus.ACTIVE
                self._used_ports[session.id] = session.listen_port
                return self._process.pid

            cmd = [
                PROXY_BINARY,
                "-listen", f"0.0.0.0:{session.listen_port}",
                "-connect", session.peer_addr,
            ]

            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self._global_session_id = session.id
            self._session_statuses[session.id] = SessionStatus.PENDING
            self._used_ports[session.id] = session.listen_port

            # Callbacks bound to session
            session_ref = session

            async def on_active():
                self._session_statuses[session_ref.id] = SessionStatus.ACTIVE

            async def on_failed():
                self._session_statuses[session_ref.id] = SessionStatus.FAILED

            async def on_line():
                session_ref.last_seen_at = datetime.utcnow()

            # Stream stdout and stderr
            t1 = asyncio.create_task(
                stream_output(
                    self._process.stdout,
                    self._log_buffer,
                    self._log_parser,
                    on_active,
                    on_failed,
                    on_line,
                )
            )
            t2 = asyncio.create_task(
                stream_output(
                    self._process.stderr,
                    self._log_buffer,
                    self._log_parser,
                    on_active,
                    on_failed,
                    on_line,
                )
            )
            self._monitor_tasks = [t1, t2]
            return self._process.pid

    async def stop(self, session_id: UUID) -> None:
        async with self._lock:
            port = self._used_ports.pop(session_id, None)
            if port is not None:
                self.release_port(port)
            self._session_statuses.pop(session_id, None)

            # Only kill the process if no more sessions using it
            if not self._used_ports and self._process and self._process.returncode is None:
                try:
                    self._process.send_signal(signal.SIGTERM)
                    try:
                        await asyncio.wait_for(self._process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        self._process.kill()
                        await self._process.wait()
                except ProcessLookupError:
                    pass
                finally:
                    self._process = None
                    self._global_session_id = None
                    for t in self._monitor_tasks:
                        t.cancel()
                    self._monitor_tasks = []

    async def is_alive(self, session_id: UUID) -> bool:
        if session_id not in self._used_ports:
            return False
        return self._process is not None and self._process.returncode is None

    async def get_log_tail(self, session_id: UUID, lines: int = 50) -> list[str]:
        return self._log_buffer.tail(lines)

    def get_session_status(self, session_id: UUID) -> Optional[SessionStatus]:
        return self._session_statuses.get(session_id)


# Singleton
process_manager = ProcessManager()
