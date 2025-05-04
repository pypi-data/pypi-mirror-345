from itmo_ics_printf.adapters.base import TraceLogAdapter
from itmo_ics_printf.core.datatype import TraceLog, TaskCreate
from typing import List, Dict, Any, Tuple
import random


class PlotlyAdapter(TraceLogAdapter):
    def convert(self, tracelog: TraceLog) -> Dict[str, Any]:
        """Convert a TraceLog object to a Plotly figure."""

        timestamps, task_numbers, event_types, creation_names = (
            self._extract_tracelog_data(tracelog)
        )

        layout = self._create_layout()

        plot_data = self._create_plot_data(
            timestamps, task_numbers, event_types, creation_names
        )

        return {"data": plot_data, "layout": layout}

    def _extract_tracelog_data(
        self, tracelog: TraceLog
    ) -> Tuple[List[int], List[int], List[str], List[str]]:

        timestamps = [event.timestamp for event in tracelog.events]
        task_numbers = [event.task_number for event in tracelog.events]
        event_types = [type(event).__name__ for event in tracelog.events]

        creation_names = []
        for event in tracelog.events:
            if isinstance(event, TaskCreate):
                creation_names.append(event.task_name)

        return timestamps, task_numbers, event_types, creation_names

    def _create_layout(self) -> Dict[str, Any]:

        return {
            "title": "Task Execution Timeline",
            "xaxis_title": "Timestamp",
            "yaxis_title": "Task Number",
            "yaxis": {"tickmode": "linear", "autorange": "reversed"},
        }

    def _create_plot_data(
        self,
        timestamps: List[int],
        task_numbers: List[int],
        event_types: List[str],
        creation_names: List[str],
    ) -> List[Dict[str, Any]]:

        plot_data = []

        for task_number in sorted(set(task_numbers)):
            task_events = [
                (ts, tn, et)
                for ts, tn, et in zip(timestamps, task_numbers, event_types)
                if tn == task_number
            ]
            if not task_events:
                continue

            color = self._generate_vibrant_color()

            line_trace = self._create_line_trace(
                task_events, task_number, creation_names, color
            )
            if line_trace:
                plot_data.append(line_trace)

            marker_trace = self._create_marker_trace(
                task_events, task_number, creation_names, color
            )
            plot_data.append(marker_trace)

        return plot_data

    def _create_line_trace(
        self,
        task_events: List[Tuple[int, int, str]],
        task_number: int,
        creation_names: List[str],
        color: str,
    ) -> Dict[str, Any]:

        line_x = []
        line_y = []
        last_switch_time = None
        num_switches = 0

        for i in range(len(task_events)):
            if task_events[i][2] == "TaskSwitched":
                if last_switch_time is not None and num_switches % 2 != 0:
                    line_x.extend([last_switch_time, task_events[i][0], None])
                    line_y.extend([task_number, task_number, None])
                last_switch_time = task_events[i][0]
                num_switches += 1

        if not line_x:
            return None

        return {
            "x": line_x,
            "y": line_y,
            "mode": "lines",
            "name": f"Task {{{task_number}}} {creation_names[task_number-1]} working",
            "type": "scatter",
            "line": {"width": 15, "color": color},
        }

    def _create_marker_trace(
        self,
        task_events: List[Tuple[int, int, str]],
        task_number: int,
        creation_names: List[str],
        color: str,
    ) -> Dict[str, Any]:

        xval = [ts for ts, _, _ in task_events]
        yval = [task_number] * len(task_events)
        textval = [et for _, _, et in task_events]

        if textval and task_number <= len(creation_names):
            textval[0] = f"TaskCreate: {creation_names[task_number-1]}"

        return {
            "x": xval,
            "y": yval,
            "mode": "markers",
            "name": f"Task {creation_names[task_number-1] if len(creation_names) >= task_number else task_number} events",
            "text": textval,
            "hoverinfo": "text",
            "type": "scatter",
            "marker": {
                "size": 16,
                "symbol": "circle",
                "color": color,
                "line": {"width": 2, "color": "black"},
            },
        }

    def _generate_vibrant_color(self) -> str:
        r = random.randint(50, 255)
        g = random.randint(50, 255)
        b = random.randint(50, 255)
        while abs(r - g) <= 50 and abs(r - b) <= 50 and abs(g - b) <= 50:
            r = random.randint(50, 255)
            g = random.randint(50, 255)
            b = random.randint(50, 255)
        return f"rgb({r}, {g}, {b})"
