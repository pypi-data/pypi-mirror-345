"""
TrustVault SDK for application observability.

Provides:
    - vault_it: Decorator for automatic tracing and latency tracking.

Usage:
    from trustvault_sdk import vault_it

    @vault_it
    def foo(...):
        ...
"""

__version__ = "0.1.0"

from .decorator import vault_it