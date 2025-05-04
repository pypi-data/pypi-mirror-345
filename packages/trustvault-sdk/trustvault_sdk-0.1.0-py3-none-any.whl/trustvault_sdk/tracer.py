"""Tracer and Span implementation for TrustVault SDK"""

import time
import uuid
from contextvars import ContextVar

from .logger import get_logger, safe_log

# Context variables for current trace and span stack
current_trace_id_var = ContextVar("trustvault_trace_id", default=None)
span_stack_var = ContextVar("trustvault_span_stack", default=[])

class Span:
    """A span represents a timed operation within a trace"""
    def __init__(self, name, trace_id=None, parent_id=None):
        self.name = name
        self.trace_id = trace_id or current_trace_id_var.get()
        self.parent_id = parent_id
        self.span_id = uuid.uuid4().hex
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None

    def __enter__(self):
        try:
            self.start_time = time.time()
            # Push to span stack
            stack = span_stack_var.get()
            new_stack = stack + [self]
            span_stack_var.set(new_stack)
        except Exception:
            get_logger().exception("TrustVault SDK error entering span")
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.end_time = time.time()
            duration = (
                self.end_time - self.start_time if self.start_time else None
            )
            # Capture error from exception if present
            if exc is not None:
                try:
                    self.error = str(exc)
                except Exception:
                    get_logger().exception("TrustVault SDK error serializing error in span exit")
            record = {
                "trace_id": self.trace_id,
                "span_id": self.span_id,
                "parent_id": self.parent_id,
                "name": self.name,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration": duration,
                "result": self.result,
                "error": self.error,
            }
            safe_log(record)
            # Pop from span stack
            stack = span_stack_var.get()
            new_stack = stack[:-1]
            span_stack_var.set(new_stack)
            # Clear trace if this was the root span
            if not new_stack:
                current_trace_id_var.set(None)
        except Exception:
            get_logger().exception("TrustVault SDK error exiting span")
        # Do not suppress exceptions from the wrapped function
        return False

    def set_result(self, result):
        """Record the result of the span"""
        try:
            self.result = self._serialize(result)
        except Exception:
            get_logger().exception("TrustVault SDK error serializing result")

    def set_error(self, error):
        """Record the error of the span"""
        try:
            self.error = str(error)
        except Exception:
            get_logger().exception("TrustVault SDK error serializing error")

    def _serialize(self, value):
        """Serialize the span result to JSON, fallback to str()"""
        try:
            import json

            return json.dumps(value, default=str)
        except Exception:
            return str(value)