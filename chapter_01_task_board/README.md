# Chapter 1 — Task Board

Учебный проект по первой главе книги Лусиану Рамальо **«Python. К вершинам мастерства»**.

Цель проекта — закрепить работу с моделью данных Python на примере собственной коллекции задач: специальные методы, итерация, индексирование, срезы, типизация и тестирование.

## Возможности

### Модель задачи

Класс `Task` хранит:

- уникальный идентификатор `id`;
- название и необязательное описание;
- статус задачи;
- приоритет;
- необязательный набор тегов.

Идентификатор доступен только для чтения через `@property`. Метод `__repr__` возвращает однозначное и удобное для отладки представление задачи.

### Коллекция задач

Класс `TaskBoard` поддерживает:

- создание из любого `Iterable[Task]`;
- проверку уникальности идентификаторов;
- получение длины через `len(board)`;
- индексирование и срезы;
- прямую и обратную итерацию;
- проверку наличия задачи по идентификатору через `id in board`;
- добавление, получение и удаление задач;
- проверку наличия тега;
- выбор задач с наивысшим приоритетом;
- подсчёт выполненных задач и процента прогресса;
- фильтрацию по статусу и тегу;
- сортировку по приоритету без изменения исходной доски.

## Структура проекта

```text
chapter_01_task_board/
├── models.py
├── task_board.py
├── test_task_board.py
└── README.md
```

- `models.py` — модели `Task` и `TaskStatus`.
- `task_board.py` — реализация коллекции `TaskBoard`.
- `test_task_board.py` — тесты на `pytest`.

## Использованные темы Python

- специальные методы `__len__`, `__getitem__`, `__contains__`, `__iter__`, `__reversed__`, `__repr__`;
- последовательности, индексирование и срезы;
- генераторные выражения;
- `Iterable` и `Iterator`;
- `@property`;
- `@overload` и аннотации типов;
- сортировка с `key`;
- исключения и проверка контрактов;
- fixtures и проверки исключений в `pytest`.

## Требования

- Python 3.10 или новее;
- `pytest`.

Установка зависимости:

```bash
python -m pip install pytest
```

## Запуск тестов

Из папки задания:

```bash
python -m pytest -q
```

Из корня общего репозитория:

```bash
python -m pytest chapter_01_task_board -q
```

## Пример использования

```python
from models import Task, TaskStatus
from task_board import TaskBoard

board = TaskBoard()

board.add(Task(
    id=1,
    title="Read Fluent Python",
    description="Finish the first chapter",
    status=TaskStatus.TODO,
    priority=3,
    tags={"python", "book"},
))

board.add(Task(
    id=2,
    title="Write tests",
    description=None,
    status=TaskStatus.DONE,
    priority=2,
    tags={"python", "pytest"},
))

print(len(board))
print(board.get(1))
print(board.top_priority(1))
print(board.progress())

for task in board.filter_by_tag("python"):
    print(task)
```

## Что было важно в проекте

Основной акцент сделан не только на работающем коде, но и на явных контрактах класса:

- `Task.id` нельзя изменить через публичный интерфейс;
- повторяющийся идентификатор приводит к `ValueError`;
- срез возвращает новый `TaskBoard`, содержащий те же объекты `Task`;
- фильтрация и сортировка не изменяют исходную доску;
- оператор `in` проверяет только наличие идентификатора задачи.