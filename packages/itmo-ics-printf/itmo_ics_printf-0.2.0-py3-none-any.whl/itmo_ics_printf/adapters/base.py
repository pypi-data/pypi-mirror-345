from abc import ABC, abstractmethod
from itmo_ics_printf.core.datatype import TraceLog


class TraceLogAdapter(ABC):
    @abstractmethod
    def convert(self, trace_log: TraceLog):
        """
        Convert a TraceLog object to a specific format.
        """
        pass
