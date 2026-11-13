"""Task export subsystem.

Provides a pluggable, registry-driven exporter architecture so that new output
formats can be added without touching the core service.
"""
from .service import export_tasks

__all__ = ["export_tasks"]
