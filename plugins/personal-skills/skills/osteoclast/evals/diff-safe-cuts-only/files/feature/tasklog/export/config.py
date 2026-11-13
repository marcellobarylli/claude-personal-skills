"""Export configuration."""
from dataclasses import dataclass


@dataclass
class ExportConfig:
    """All tunable knobs for exporters."""

    delimiter: str = ","
    include_header: bool = True
    line_terminator: str = "\n"
    null_value: str = ""
    tag_separator: str = ";"
    indent: int = 2
    sort_keys: bool = False
    encoding: str = "utf-8"
    xml_root: str = "tasks"

    def validate(self):
        if len(self.delimiter) != 1:
            raise ValueError("delimiter must be a single character")
        if self.indent < 0:
            raise ValueError("indent must be non-negative")
        return self
