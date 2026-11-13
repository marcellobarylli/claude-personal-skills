"""Abstract base class for exporters."""
from abc import ABC, abstractmethod


class Exporter(ABC):
    """Base class every exporter must inherit from."""

    def __init__(self, config):
        self.config = config

    @property
    @abstractmethod
    def content_type(self):
        """MIME type of the produced output."""

    @property
    @abstractmethod
    def file_extension(self):
        """Suggested file extension for the produced output."""

    @abstractmethod
    def export(self, tasks):
        """Return the exported text."""

    def describe(self):
        return f"{type(self).__name__}({self.content_type})"
