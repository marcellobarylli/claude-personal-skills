"""JSON exporter."""
import json
from dataclasses import asdict

from .base import Exporter
from .retry import with_retry


class JsonExporter(Exporter):
    """Exports tasks as a JSON list sorted by id."""

    @property
    def content_type(self):
        return "application/json"

    @property
    def file_extension(self):
        return ".json"

    @with_retry(attempts=3)
    def export(self, tasks):
        # Guard against a missing task list
        if tasks is None:
            tasks = []
        ordered = sorted(tasks, key=lambda task: task.id)
        payload = [asdict(task) for task in ordered]
        return json.dumps(payload, indent=self.config.indent, sort_keys=self.config.sort_keys)
