from enum import Enum

class TaskStatus(Enum):
    TODO = 0
    IN_PROGRESS = 1
    DONE = 2

class Task:
    _id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    tags: set[str] | None

    def __init__(self, id: int, title: str, description: str | None, status: TaskStatus, priority: int, tags: set[str] | None):
        self._id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.tags = set(tags) if tags is not None else None

    def __repr__(self) -> str:
        return f'Task(id={self.id}, title={self.title!r}, description={self.description!r}, status={self.status}, priority={self.priority}, tags={self.tags!r})'
    
    @property
    def id(self) -> int:
        return self._id
