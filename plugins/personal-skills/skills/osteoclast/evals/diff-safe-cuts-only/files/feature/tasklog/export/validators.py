"""Input validation for the export pipeline."""
from ..models import Task


def validate_tasks(tasks):
    """Ensure tasks is a list of Task objects with unique ids."""
    if tasks is None:
        raise TypeError("tasks must not be None")
    seen = set()
    for task in tasks:
        if not isinstance(task, Task):
            raise TypeError(f"expected Task, got {type(task).__name__}")
        if task.id in seen:
            raise ValueError(f"duplicate task id: {task.id}")
        seen.add(task.id)
    return True
