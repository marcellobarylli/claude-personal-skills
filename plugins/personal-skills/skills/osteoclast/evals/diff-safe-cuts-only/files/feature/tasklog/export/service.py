"""High-level export service."""
from .config import ExportConfig
from .registry import default_registry
from .validators import validate_tasks


def export_tasks(tasks, fmt="csv", config=None):
    """Export ``tasks`` in the given format and return the text."""
    # Fall back to the default configuration when none is supplied
    if config is None:
        config = ExportConfig()
    # Validate the tasks before exporting them
    validate_tasks(tasks)
    # Look up the exporter class for the requested format
    exporter_cls = default_registry.get(fmt)
    # Instantiate the exporter
    exporter = exporter_cls(config)
    # Run the export
    return exporter.export(tasks)
