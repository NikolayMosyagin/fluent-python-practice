import pytest
from task_board import TaskBoard
from models import Task, TaskStatus

@pytest.fixture
def tasks() -> list[Task]:
    return [Task(
        id=1,
        title="Title 1",
        description="Description 1",
        status=TaskStatus.TODO,
        priority=1,
        tags=None
    ),
    Task(
        id=2,
        title="Title 2",
        description="Description 2",
        status=TaskStatus.DONE,
        priority=2,
        tags={"python"}
    ),
    Task(
        id=3,
        title="Title 3",
        description="Description 3",
        status=TaskStatus.TODO,
        priority=3,
        tags=None
    ),
    Task(
        id=4,
        title="Title 4",
        description="Description 4",
        status=TaskStatus.IN_PROGRESS,
        priority=2,
        tags={"python"}
    ),
    Task(
        id=5,
        title="Title 5",
        description=None,
        status=TaskStatus.TODO,
        priority=1,
        tags={"assert"}
    ),
    Task(
        id=6,
        title="Title 6",
        description="Description 6",
        status=TaskStatus.DONE,
        priority=2,
        tags=None
    )]

@pytest.fixture
def board(tasks: list[Task]) -> TaskBoard:
    return TaskBoard(tasks)


def test_empty_board():
    board = TaskBoard()
    assert len(board) == 0


def test_board_created_with_tasks():
    task1 = Task(
        id=1,
        title="Title 1",
        description="Description 1",
        status=TaskStatus.TODO,
        priority=1,
        tags=None
    )
    task2 = Task(
        id=2,
        title="Title 2",
        description="Description 2",
        status=TaskStatus.DONE,
        priority=2,
        tags={"python"}
    )

    board = TaskBoard((task1, task2))
    assert len(board) == 2
    assert board[0] is task1
    assert board[1] is task2


def test_duplicate_id_raises_error():
    task1 = Task(
        id=1,
        title="Title 1",
        description=None,
        status=TaskStatus.IN_PROGRESS,
        priority=1,
        tags=None
    )

    task2 = Task(
        id=1,
        title="Title 2",
        description="Description 2",
        status=TaskStatus.IN_PROGRESS,
        priority=2,
        tags=None
    )

    with pytest.raises(ValueError):
        TaskBoard((task1, task2))


def test_get_returns_task_by_id(board: TaskBoard, tasks: list[Task]):
    assert board.get(2) is tasks[1]


def test_get_id_raises_error(board: TaskBoard):
    with pytest.raises(ValueError, match='Task not found: id=999'):
        board.get(999)


def test_add_task():
    task1 = Task(
        id=1,
        title="Title 1",
        description="Description 1",
        status=TaskStatus.TODO,
        priority=1,
        tags=None
    )
    task2 = Task(
        id=2,
        title="Title 2",
        description="Description 2",
        status=TaskStatus.DONE,
        priority=2,
        tags={"python"}
    )

    board = TaskBoard((task1, ))
    assert len(board) == 1
    board.add(task2)
    assert len(board) == 2
    assert board.get(2) is task2
    task3 = Task(
        id=2,
        title="TItle Unknown",
        description="Description Unknown",
        status=TaskStatus.DONE,
        priority=5,
        tags=None
    )
    with pytest.raises(
        ValueError,
        match="Duplicate task id: 2"
    ):
        board.add(task3)


def test_remove_task():
    task1 = Task(
        id=1,
        title="Title 1",
        description="Description 1",
        status=TaskStatus.TODO,
        priority=1,
        tags=None
    )
    task2 = Task(
        id=2,
        title="Title 2",
        description="Description 2",
        status=TaskStatus.DONE,
        priority=2,
        tags={"python"}
    )

    board = TaskBoard((task1, task2))
    assert board.remove(2) is task2
    assert len(board) == 1
    with pytest.raises(ValueError):
        board.get(2)
    with pytest.raises(ValueError):
        board.remove(10)


def test_contains_tasks(board: TaskBoard):
    assert 2 in board
    assert 999 not in board
    assert True not in board
    assert "python" not in board


def test_slices_task(board: TaskBoard, tasks: list[Task]):
    result = board[1:4]
    assert type(result) is TaskBoard
    assert len(result) == 3
    assert list(result) == [tasks[1], tasks[2], tasks[3]]

    reversed_result = board[::-1]
    assert type(reversed_result) is TaskBoard
    assert len(reversed_result) == 6
    assert list(reversed_result) == list(reversed(tasks))


def test_has_tag_in_board(board: TaskBoard):
    assert board.has_tag("python")
    assert board.has_tag("assert")
    assert not board.has_tag("missing")
    assert not board.has_tag("Unknown")


def test_top_priority_in_board(board: TaskBoard, tasks: list[Task]):
    tops = board.top_priority()
    assert [task.priority for task in tops] == [3, 2, 2]
    assert tops == [tasks[2], tasks[1], tasks[3]]

    tops = board.top_priority(limit=0)
    assert len(tops) == 0
    with pytest.raises(
            ValueError,
            match="Limit must be non-negative, got -1"
    ):
        board.top_priority(limit=-1)
    tops = board.top_priority(limit=100)
    assert tops == sorted(tasks, key=lambda x: x.priority, reverse=True)

def test_task_progress_in_board(board: TaskBoard):
    assert board.done_count() == 2
    assert board.progress() == pytest.approx(2 / 6 * 100)

    board_empty = TaskBoard()
    assert board_empty.done_count() == 0
    assert board_empty.progress() == pytest.approx(0.0)


def test_filter_by_status_in_board(board: TaskBoard, tasks: list[Task]):
    result = board.filter_by_status(TaskStatus.TODO)
    assert type(result) is TaskBoard
    assert list(result) == [tasks[0], tasks[2], tasks[4]]


def test_filter_by_tag_in_board(board: TaskBoard, tasks: list[Task]):
    result = board.filter_by_tag("python")
    assert type(result) is TaskBoard
    assert list(result) == [tasks[1], tasks[3]]

    result = board.filter_by_tag("Unknown")
    assert type(result) is TaskBoard
    assert len(result) == 0


def test_sort_by_priority_in_board(board: TaskBoard, tasks: list[Task]):
    descending  = board.sorted_by_priority()
    ascending = board.sorted_by_priority(reverse=False)

    assert type(descending) is TaskBoard
    assert type(ascending) is TaskBoard
    assert list(descending) == [tasks[2], tasks[1], tasks[3], tasks[5], tasks[0], tasks[4]]
    assert list(ascending) == [tasks[0], tasks[4], tasks[1], tasks[3], tasks[5], tasks[2]]
    assert list(board) == tasks

def test_iter_in_board(board: TaskBoard, tasks: list[Task]):
    assert list(board) == tasks
    assert list(reversed(board)) == list(reversed(tasks))

    
