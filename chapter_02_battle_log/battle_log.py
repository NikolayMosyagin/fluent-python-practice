from models import BattleEvent
from collections.abc import Iterable, Iterator
from typing import overload, Union
from dataclasses import dataclass

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
        
    
        
        
        