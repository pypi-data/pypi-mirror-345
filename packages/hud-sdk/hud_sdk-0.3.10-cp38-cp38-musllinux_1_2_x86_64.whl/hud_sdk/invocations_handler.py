import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from .native import check_linked_code, get_and_swap_aggregations, get_function_id
from .process_utils import get_current_pid


class InvocationsHandler:
    def __init__(self) -> None:
        self.last_invocations_dump = time.perf_counter()

    def get_and_clear_invocations(self) -> List[Dict[str, Any]]:
        current_time = time.perf_counter()
        timeslice = int(current_time - self.last_invocations_dump)
        self.last_invocations_dump = current_time
        invocations_c = get_and_swap_aggregations()
        if not invocations_c:
            return []
        pid = get_current_pid()
        timestamp = datetime.now(timezone.utc).isoformat()
        invocations = [
            dict(
                count=invocation.total_calls,
                function_id=invocation.function_id,
                sampled_count=invocation.total_calls,
                sum_duration=invocation.total_time,
                sum_squared_duration=invocation.total_squared_time,
                timeslice=timeslice,
                timestamp=timestamp,
                callers=[
                    dict(
                        name=c.co_name,
                        file_name=c.co_filename,
                        start_line=c.co_firstlineno,
                        function_id=get_function_id(c),
                    )
                    for c in invocation.callers
                    if c
                ],
                wrapped_flow_id=invocation.flow_id,
                exceptions=invocation.exceptions,
                sketch=(
                    dict(
                        bin_width=invocation.sketch_data.bin_width,
                        index_shift=invocation.sketch_data.index_shift,
                        data=invocation.sketch_data.data,
                    )
                    if invocation.sketch_data
                    else dict(bin_width=0, index_shift=0, data=[])
                ),
                is_linked_function=check_linked_code(invocation.code_obj),
                pid=pid,
            )
            for invocation in invocations_c.values()
        ]
        invocations_c.clear()
        return invocations
