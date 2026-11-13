"""XML exporter."""
from xml.etree import ElementTree

from .base import Exporter
from .retry import with_retry
from .utils import bool_to_str


class XmlExporter(Exporter):
    """Exports tasks as an XML document."""

    @property
    def content_type(self):
        return "application/xml"

    @property
    def file_extension(self):
        return ".xml"

    @with_retry(attempts=3)
    def export(self, tasks):
        root = ElementTree.Element(self.config.xml_root)
        for task in sorted(tasks or [], key=lambda task: task.id):
            node = ElementTree.SubElement(root, "task", id=str(task.id), done=bool_to_str(task.done))
            ElementTree.SubElement(node, "title").text = task.title
            if task.due is not None:
                ElementTree.SubElement(node, "due").text = task.due
            for tag in task.tags:
                ElementTree.SubElement(node, "tag").text = tag
        return ElementTree.tostring(root, encoding="unicode")
