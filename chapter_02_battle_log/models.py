from enum import Enum
from dataclasses import dataclass

class EventType(Enum):
    DAMAGE = 0
    HEAL = 1
    BUFF = 2
    DEBUFF = 3
    DEATH = 4

@dataclass(frozen=True, repr=False)
class BattleEvent:
    timestamp: float
    event_type: EventType
    actor: str
    target: str
    value: int | None = None
    tags: frozenset[str] | set[str] | None = None

    def __post_init__(self):
        if self.timestamp < 0:
            raise ValueError(f"timestamp can't be negative: {self.timestamp}")
        if self.actor is None or len(self.actor) == 0:
            raise ValueError("actor can't be empty")
        if self.target is None or len(self.target) == 0:
            raise ValueError("target can't be empty")
        if self.value is not None and self.value < 0:
            raise ValueError(f"value can't be negative: {self.value}")
        if self.tags is not None and not isinstance(self.tags, (frozenset, set)):
            raise TypeError('tags must be a set or frozenset')
        final_value = frozenset() if self.tags is None else frozenset(self.tags)
        object.__setattr__(self, 'tags', final_value)

    def __repr__(self):
        return f"BattleEvent(timestamp={self.timestamp!r}, event_type={self.event_type}" \
            f", actor={self.actor!r}, target={self.target!r}, value={self.value!r}, tags={self.tags!r})"
