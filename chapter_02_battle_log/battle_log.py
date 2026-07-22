from models import BattleEvent, EventType
from collections.abc import Iterable, Iterator
from typing import overload, Union
from dataclasses import dataclass
from bisect import bisect_left, bisect_right
from collections import Counter
from collections import defaultdict

@dataclass(frozen=True)
class BattleLog:
    logs: tuple[BattleEvent, ...] | Iterable[BattleEvent] | None = None

    def __post_init__(self):
        if self.logs is None:
            object.__setattr__(self, 'logs', tuple())
            return

        final_logs = tuple(self.logs)
        if not all(final_logs[i - 1].timestamp <= final_logs[i].timestamp for i in range(1, len(final_logs))):
            raise ValueError('The source must be in chronological order by time.')
        object.__setattr__(self, 'logs', final_logs)

    def __len__(self) -> int:
        return len(self.logs)
    
    @overload
    def __getitem__(self, key: int) -> BattleEvent: ...
    
    @overload
    def __getitem__(self, key: slice) -> 'BattleLog': ...

    def __getitem__(self, key: int | slice) -> Union[BattleEvent, 'BattleLog']:
        if type(key) is int:
            return self.logs[key]
        elif type(key) is slice:
            return BattleLog(self.logs[key])
        else:
            raise TypeError(f'Indices must be integers or slices, not {type(key).__name__}')
    
    def __iter__(self) -> Iterator[BattleEvent]:
        return iter(self.logs)
    
    def __reversed__(self) -> Iterator[BattleEvent]:
        return reversed(self.logs)
    
    def __contains__(self, item: object) -> bool:
        if isinstance(item, BattleEvent):
            return item in self.logs
        return False
    
    def __repr__(self) -> str:
        return f"BattleLog(count={len(self.logs)}, events={self.logs!r})"
    
    def by_type(self, event_type: EventType) -> 'BattleLog':
        return BattleLog(event for event in self.logs if event.event_type == event_type)
    
    def by_actor(self, actor: str) -> 'BattleLog':
        return BattleLog(event for event in self.logs if event.actor == actor)
    
    def by_target(self, target: str) -> 'BattleLog':
        return BattleLog(event for event in self.logs if event.target == target)
    
    def by_tag(self, tag: str) -> 'BattleLog':
        return BattleLog(event for event in self.logs if tag in event.tags)
    
    def between(self, start: float, end: float) -> 'BattleLog':
        if start < 0:
            raise ValueError(f"The parameter 'start' must be non-negative: {start}")
        if end < 0:
            raise ValueError(f"The parameter 'end' must be non-negative: {end}")
        if start > end:
            raise ValueError(f"The parameter 'start' cannot be larger than 'end': {start} > {end}")
        left = bisect_left(self.logs, start, key=lambda log: log.timestamp)
        right = bisect_right(self.logs, end, key=lambda log: log.timestamp)
        return BattleLog(self.logs[left:right])

    def last(self, limit: int = 3) -> 'BattleLog':
        if limit < 0:
            raise ValueError(f"The parameter 'limit' must be non-negative: {limit}")
        if limit == 0:
            return BattleLog()
        return BattleLog(self.logs[-limit:])
    
    def count_by_type(self) -> Counter[EventType]:
        return Counter(event.event_type for event in self.logs)
    
    def total_value(self, event_type: EventType) -> int:
        return sum(0 if event.value is None else event.value for event in self.logs if event.event_type == event_type)
    
    def participants(self) -> frozenset[str]:
        actors = frozenset(event.actor for event in self.logs)
        return actors.union(event.target for event in self.logs)
    
    def group_by_actor(self) -> dict[str, 'BattleLog']:
        groups: defaultdict[str, list[BattleEvent]] = defaultdict(list)
        for event in self.logs:
            groups[event.actor].append(event)
        result: dict[str, BattleLog] = {}
        for key, value in groups.items():
            result[key] = BattleLog(value)
        return result


    



        
    
        
        
        