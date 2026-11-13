from dataclasses import dataclass, field


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    due: str | None = None
    tags: list[str] = field(default_factory=list)
