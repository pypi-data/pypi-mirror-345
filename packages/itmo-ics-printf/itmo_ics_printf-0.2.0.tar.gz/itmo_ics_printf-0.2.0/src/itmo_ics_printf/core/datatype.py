import struct
import sys
from typing import Optional, Dict

try:
    from icecream import ic
except ImportError:

    def ic(*args):
        print(*args)


TASK_CREATE = 0
TASK_SWITCHED_IN = 1
TASK_SWITCHED_OUT = 2
TASK_SCANF_CONFIG = 3

EVENT_TYPE_NAMES: Dict[int, str] = {
    TASK_CREATE: "TASK_CREATE",
    TASK_SWITCHED_IN: "TASK_SWITCHED_IN",
    TASK_SWITCHED_OUT: "TASK_SWITCHED_OUT",
    TASK_SCANF_CONFIG: "TASK_SCANF_CONFIG",
}


def _warning(message: str) -> None:
    print(f"{"-" * 20}\nWarning:\n{message}\n{"-" * 20}\n", file=sys.stderr, end="")


class TraceEvent:
    @classmethod
    def from_bytes(
        cls, buf: bytes, max_task_name_len: Optional[int] = None
    ) -> "TraceEvent":
        raise NotImplementedError("Subclasses should implement this method")


class TaskScanfConfig(TraceEvent):
    class ScanfVersion:
        major = 0
        minor = 1
        patch = 0

        def __init__(self, major: int, minor: int, patch: int):
            self.major = major
            self.minor = minor
            self.patch = patch

        def __repr__(self) -> str:
            return f"{self.major}.{self.minor}.{self.patch}"

    STRUCT_FORMAT = f"<B B B B B"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, version: ScanfVersion, max_task_name_len: int):
        self.version = version
        self.max_task_name_len = max_task_name_len

    def __repr__(self) -> str:
        return f"TaskScanfConfig(version={self.version}, max_task_name_len={self.max_task_name_len})"

    @classmethod
    def from_bytes(
        cls,
        buf: bytes,
    ) -> "TaskScanfConfig":
        _, major, minor, patch, max_task_name_len = struct.unpack(
            cls.STRUCT_FORMAT, buf[: cls.SIZE]
        )
        version = cls.ScanfVersion(major, minor, patch)
        return cls(version, max_task_name_len)


class TaskCreate(TraceEvent):
    STRUCT_FORMAT = f"<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, timestamp: int, task_number: int, task_name: str):
        self.timestamp = timestamp
        self.task_number = task_number
        self.task_name = task_name

    def __repr__(self) -> str:
        return (
            f"TaskCreate(timestamp={self.timestamp}, task_number={self.task_number},"
            f" task_name={self.task_name})"
        )

    @classmethod
    def from_bytes(
        cls, buf: bytes, max_task_name_len: Optional[int] = None
    ) -> "TaskCreate":
        if max_task_name_len is None:
            max_task_name_len = 64
            _warning(
                f"max_task_name_len is None, using default value: {max_task_name_len}"
            )

        full_format = f"{cls.STRUCT_FORMAT} {max_task_name_len}s"
        full_size = struct.calcsize(full_format)

        if len(buf) < full_size:
            raise ValueError(
                f"Buffer too small: {len(buf)} bytes, expected at least {full_size} bytes for "
                f"TaskCreate event."
            )

        _, timestamp, task_number, raw_task_name = struct.unpack(
            full_format, buf[:full_size]
        )
        task_name = raw_task_name.split(b"\0")[0].decode("utf-8")
        return cls(timestamp, task_number, task_name)


class TaskSwitched(TraceEvent):
    STRUCT_FORMAT = "<B I I"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, event_type: int, timestamp: int, task_number: int):
        self.event_type = event_type
        self.timestamp = timestamp
        self.task_number = task_number

    def __repr__(self) -> str:
        type_str = (
            "TASK_SWITCHED_IN"
            if self.event_type == TASK_SWITCHED_IN
            else "TASK_SWITCHED_OUT"
        )
        return f"TaskSwitched({type_str}, timestamp={self.timestamp}, task_number={self.task_number})"

    @classmethod
    def from_bytes(cls, buf: bytes) -> "TaskSwitched":
        event_type, timestamp, task_number = struct.unpack(
            cls.STRUCT_FORMAT, buf[: cls.SIZE]
        )
        return cls(event_type, timestamp, task_number)


class TraceLog:
    def __init__(self):
        self.events = []
        self.max_task_name_len: Optional[int] = 64
        self.scanf_version: Optional[TaskScanfConfig.ScanfVersion] = None

    def _configure(
        self, version: TaskScanfConfig.ScanfVersion, max_task_name_len: int
    ) -> None:
        self.max_task_name_len = max_task_name_len

        self.scanf_version = version
        print(
            f"Configured TraceLog: version={self.scanf_version}, "
            f"max_task_name_len={self.max_task_name_len}"
        )

    def load(self, filename: str) -> "TraceLog":
        with open(filename, "rb") as f:
            content = f.read()

        offset = 0
        while offset < len(content):
            event_type = content[offset]
            if event_type == TASK_SCANF_CONFIG:
                event = TaskScanfConfig.from_bytes(
                    content[offset : offset + TaskScanfConfig.SIZE]
                )
                offset += TaskScanfConfig.SIZE
                self.events.append(event)
                self._configure(event.version, event.max_task_name_len)

                break
            _warning(
                f"Missed event: {EVENT_TYPE_NAMES[event_type]}({event_type}) at offset {offset} "
                f"instead of TASK_SCANF_CONFIG({TASK_SCANF_CONFIG.__repr__()}).\n"
                f"Possibly different Scanf-writer version or corrupted traceLog file."
            )
            break

        while offset < len(content):
            event_type = content[offset]

            if event_type == TASK_CREATE:
                event = TaskCreate.from_bytes(
                    content[offset : offset + TaskCreate.SIZE + self.max_task_name_len],
                    self.max_task_name_len,
                )
                offset += TaskCreate.SIZE + self.max_task_name_len
            elif event_type in (TASK_SWITCHED_IN, TASK_SWITCHED_OUT):
                event = TaskSwitched.from_bytes(
                    content[offset : offset + TaskSwitched.SIZE]
                )
                offset += TaskSwitched.SIZE
            else:
                raise ValueError(f"Unknown event type: {event_type} at offset {offset}")
            self.events.append(event)

        return self
