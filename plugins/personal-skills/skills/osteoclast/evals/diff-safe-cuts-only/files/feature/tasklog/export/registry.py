"""Exporter registry with optional plugin discovery."""
from importlib import metadata

from .csv_exporter import CsvExporter
from .json_exporter import JsonExporter
from .xml_exporter import XmlExporter


class ExporterRegistry:
    """Maps format names to exporter classes."""

    def __init__(self):
        self._exporters = {}

    def register(self, name, exporter_cls):
        if not name:
            raise ValueError("exporter name must not be empty")
        self._exporters[name] = exporter_cls

    def unregister(self, name):
        self._exporters.pop(name, None)

    def get(self, name):
        try:
            return self._exporters[name]
        except KeyError:
            raise ValueError(f"unknown format: {name}") from None

    def names(self):
        return sorted(self._exporters)

    def load_plugins(self, group="tasklog.exporters"):
        """Discover third-party exporters advertised via entry points."""
        loaded = []
        for entry_point in metadata.entry_points(group=group):
            try:
                self.register(entry_point.name, entry_point.load())
                loaded.append(entry_point.name)
            except Exception:
                continue
        return loaded


default_registry = ExporterRegistry()
default_registry.register("csv", CsvExporter)
default_registry.register("json", JsonExporter)
default_registry.register("xml", XmlExporter)
