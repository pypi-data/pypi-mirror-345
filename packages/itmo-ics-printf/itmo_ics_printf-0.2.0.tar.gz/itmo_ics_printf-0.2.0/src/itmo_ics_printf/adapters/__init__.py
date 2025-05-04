from .plotly import PlotlyAdapter
from .base import TraceLogAdapter


def create_adapter(adapter_type: str) -> TraceLogAdapter:
    """
    Factory function to create an adapter based on the specified type.
    """
    if adapter_type == "plotly":
        return PlotlyAdapter()
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
