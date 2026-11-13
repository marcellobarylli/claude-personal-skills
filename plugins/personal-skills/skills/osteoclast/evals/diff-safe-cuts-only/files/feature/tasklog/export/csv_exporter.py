"""CSV exporter."""
import csv
import io

from .base import Exporter
from .retry import with_retry
from .utils import bool_to_str


class CsvExporter(Exporter):
    """Exports tasks as CSV."""

    HEADER = ["id", "title", "done", "due", "tags"]

    @property
    def content_type(self):
        return "text/csv"

    @property
    def file_extension(self):
        return ".csv"

    @with_retry(attempts=3)
    def export(self, tasks):
        # Guard against a missing task list
        if tasks is None:
            tasks = []
        buffer = io.StringIO()
        try:
            writer = csv.writer(
                buffer,
                delimiter=self.config.delimiter,
                lineterminator=self.config.line_terminator,
            )
            if self.config.include_header:
                writer.writerow(self.HEADER)
            for task in tasks:
                title = task.title
                # Make sure the title is a string
                if not isinstance(title, str):
                    title = str(title)
                due = task.due if task.due is not None else self.config.null_value
                tags = task.tags if task.tags is not None else []
                writer.writerow(
                    [
                        task.id,
                        title,
                        bool_to_str(task.done),
                        due,
                        self.config.tag_separator.join(tags),
                    ]
                )
            return buffer.getvalue()
        finally:
            buffer.close()
