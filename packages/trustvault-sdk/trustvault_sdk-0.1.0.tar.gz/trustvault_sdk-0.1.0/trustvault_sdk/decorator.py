"""vault_it decorator for automatic tracing"""

import functools
import uuid

from .tracer import Span, current_trace_id_var, span_stack_var
from .logger import get_logger

def vault_it(func=None, *, name=None):
    """
    Decorator to automatically create spans around function calls,
    capturing inputs, outputs, errors, and timing information.
    Usage:
        @vault_it
        def func(...):
            pass
    """
    if func is None:
        return lambda f: vault_it(f, name=name)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            trace_id = current_trace_id_var.get()
            if trace_id is None:
                trace_id = uuid.uuid4().hex
                current_trace_id_var.set(trace_id)
            stack = span_stack_var.get()
            parent_id = stack[-1].span_id if stack else None
            span_name = name or func.__name__
            span = Span(name=span_name, trace_id=trace_id, parent_id=parent_id)
        except Exception:
            get_logger().exception("TrustVault SDK error initializing span")
            return func(*args, **kwargs)

        try:
            with span:
                result = func(*args, **kwargs)
                try:
                    span.set_result(result)
                except Exception:
                    get_logger().exception("TrustVault SDK error setting span result")
                return result
        except Exception as e:
            try:
                span.set_error(e)
            except Exception:
                get_logger().exception("TrustVault SDK error setting span error")
            raise

    return wrapper