from models import Task, TaskStatus
from collections.abc import Iterable, Iterator
from typing import overload, Union

class TaskBoard:
    _tasks: list[Task]

    def __init__(self, tasks: Iterable[Task] | None = None):
        self._tasks = []
        if tasks is None:
            return

        for task in tasks:
            self._add_internal(task)

    def __len__(self) -> int:
        return len(self._tasks)
    
    @overload
    def __getitem__(self, key: int) -> Task: ...
    
    @overload
    def __getitem__(self, key: slice) -> 'TaskBoard': ...

    def __getitem__(self, key: int | slice) -> Union[Task, 'TaskBoard']:
        # bool is a subclass of int, so check the exact type.
        if type(key) is int:
            return self._tasks[key]
        elif type(key) is slice:
            return TaskBoard(self._tasks[i] for i in range(*key.indices(len(self._tasks))))
        raise TypeError(f'Indices must be integers or slices, not {type(key).__name__}')
    
    def __contains__(self, item: object) -> bool:
        # bool is a subclass of int, so check the exact type.
        if type(item) is int:
            return any(task.id == item for task in self._tasks)
        return False
    
    def __iter__(self) -> Iterator[Task]:
        return iter(self._tasks)
    
    def __reversed__(self) -> Iterator[Task]:
        return reversed(self._tasks)
    
    def _add_internal(self, task: Task) -> None:
        if any(task.id == s.id for s in self._tasks):
            raise ValueError(f'Duplicate task id: {task.id}')
        self._tasks.append(task)
    
    def add(self, task: Task) -> None:
        self._add_internal(task)
    
    def remove(self, task_id: int) -> Task:
        remove_task = self.get(task_id)
        self._tasks.remove(remove_task)
        return remove_task
    
    def get(self, task_id: int) -> Task:
        f_task = next((task for task in self._tasks if task.id == task_id), None)
        if f_task is None:
            raise ValueError(f'Task not found: id={task_id}')
        return f_task
    
    def has_tag(self, tag: str) -> bool:
        return any(task.tags is not None and (tag in task.tags) for task in self._tasks)
    
    def top_priority(self, limit: int = 3) -> list[Task]:
        if limit < 0:
            raise ValueError(f'Limit must be non-negative, got {limit}')
        if limit == 0:
            return []
        return sorted(self._tasks, key=lambda x: x.priority, reverse=True)[:limit]

    def done_count(self) -> int:
        return sum(1 if task.status == TaskStatus.DONE else 0 for task in self._tasks)
    
    def progress(self) -> float:
        n = len(self._tasks)
        if n == 0:
            return 0.0
        return self.done_count() / n * 100
    
    def filter_by_status(self, status: TaskStatus) -> 'TaskBoard':
        return TaskBoard(task for task in self._tasks if task.status == status)
    
    def filter_by_tag(self, tag: str) -> 'TaskBoard':
        return TaskBoard(task for task in self._tasks if task.tags is not None and tag in task.tags)
    
    def sorted_by_priority(self, reverse: bool = True) -> 'TaskBoard':
        return TaskBoard(sorted(self._tasks, key=lambda x: x.priority, reverse=reverse))


