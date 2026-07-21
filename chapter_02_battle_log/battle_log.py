from models import BattleEvent
from collections.abc import Iterable, Iterator
from typing import overload, Union

class BattleLog:
    logs: tuple[BattleEvent, ...]

    def __init__(self, source: Iterable[BattleEvent] | None = None):
        if source is None:
            self.logs = tuple()
            return
        
        self.logs = tuple(source)
        if not all(self.logs[i - 1].timestamp <= self.logs[i].timestamp for i in range(1, len(self.logs))):
            raise ValueError('The source must be in chronological order by time.')
    
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
    
    def __contains__(self, item: BattleEvent) -> bool:
        if isinstance(item, BattleEvent):
            return item in self.logs
        return False
    
    def __repr__(self) -> str:
        content = ", ".join((repr(item) for item in self.logs))
        return f"BattleLog(({content}))"
        
    
        
        
        