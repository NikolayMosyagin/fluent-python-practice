import pytest
from battle_log import BattleLog
from models import BattleEvent, EventType
from collections.abc import Iterable

@pytest.fixture
def events_valid() -> list[BattleEvent]:
    return [
        BattleEvent(
            timestamp=10.0,
            event_type=EventType.DAMAGE,
            actor='Knight',
            target='Orc',
            value=20,
            tags={'critical'}
        ),
        BattleEvent(
            timestamp=10.0,
            event_type=EventType.BUFF,
            actor='Knight',
            target='Orc',
            tags={'stun'}
        ),
        BattleEvent(
            timestamp=25.2,
            event_type=EventType.DAMAGE,
            actor='Orc',
            target='Knight',
            value=30,
            tags={'melee'}
        )
    ]

@pytest.fixture
def log(events_valid: list[BattleEvent]) -> BattleLog:
    return BattleLog(events_valid)

def test_empty_battle_log():
    log = BattleLog()
    assert len(log) == 0

def test_create_battle_log(events_valid: list[BattleEvent]):
    log = BattleLog(events_valid)
    assert len(log) == len(events_valid)

    log2 = BattleLog((
        BattleEvent(
            timestamp=i*5.0,
            event_type=EventType.DAMAGE,
            actor='Knight',
            target='Orc',
            value=i
        ) for i in range(10)
    ))
    assert len(log2) == 10

def test_indices_battle_log(log: BattleLog, events_valid: list[BattleEvent]):
    assert log[0] is events_valid[0]
    assert log[2] is events_valid[2]
    with pytest.raises(IndexError):
        log[3]
    assert log[-1] == events_valid[-1]
    assert log[-2] == events_valid[-2]
    with pytest.raises(IndexError):
        log[-4]
    
