import asyncio
import re
from collections import deque
from datetime import datetime
from uuid import UUID


class LogBuffer:
    def __init__(self, maxlen: int = 500):
        self._buf: deque[str] = deque(maxlen=maxlen)

    def append(self, line: str) -> None:
        self._buf.append(line)

    def tail(self, n: int) -> list[str]:
        lines = list(self._buf)
        return lines[-n:] if n < len(lines) else lines


class LogParser:
    # Patterns that indicate the tunnel is established
    ACTIVE_PATTERNS = [
        re.compile(r"Established DTLS connection", re.IGNORECASE),
        re.compile(r"tunnel (is )?established", re.IGNORECASE),
        re.compile(r"connection established", re.IGNORECASE),
        re.compile(r"listening on", re.IGNORECASE),
    ]
    FAIL_PATTERNS = [
        re.compile(r"fatal error", re.IGNORECASE),
        re.compile(r"failed to connect", re.IGNORECASE),
        re.compile(r"connection refused", re.IGNORECASE),
        re.compile(r"no such file", re.IGNORECASE),
    ]

    def classify(self, line: str) -> str:
        """Returns 'active', 'failed', or 'normal'."""
        for p in self.ACTIVE_PATTERNS:
            if p.search(line):
                return "active"
        for p in self.FAIL_PATTERNS:
            if p.search(line):
                return "failed"
        return "normal"


async def stream_output(
    stream: asyncio.StreamReader,
    buffer: LogBuffer,
    parser: LogParser,
    on_active,
    on_failed,
    on_line,
) -> None:
    """Read lines from stream, classify, fire callbacks."""
    while True:
        try:
            raw = await stream.readline()
        except Exception:
            break
        if not raw:
            break
        line = raw.decode(errors="replace").rstrip()
        buffer.append(f"[{datetime.utcnow().isoformat()}] {line}")
        kind = parser.classify(line)
        await on_line()
        if kind == "active":
            await on_active()
        elif kind == "failed":
            await on_failed()
