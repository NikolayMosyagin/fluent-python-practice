import pytest
from battle_log import BattleLog
from models import BattleEvent, EventType
from dataclasses import FrozenInstanceError

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

    with pytest.raises(ValueError):
        BattleLog(events_valid[::-1])
    log3 = BattleLog(events_valid[:2])
    assert len(log3) == 2

def test_frozen_battle_log(log: BattleLog):
    with pytest.raises(FrozenInstanceError):
        log.logs = tuple()

def test_indices_battle_log(log: BattleLog, events_valid: list[BattleEvent]):
    assert log[0] is events_valid[0]
    assert log[2] is events_valid[2]
    assert isinstance(log[0], BattleEvent)
    with pytest.raises(IndexError):
        log[3]
    assert log[-1] == events_valid[-1]
    assert log[-2] == events_valid[-2]
    with pytest.raises(IndexError):
        log[-4]

def test_slice_battle_log(log: BattleLog, events_valid: list[BattleEvent]):
    log2 = log[:2]
    assert isinstance(log2, BattleLog)
    assert list(log2) == events_valid[:2]
    log3 = log[1::-1]
    assert events_valid[1::-1] == list(log3)
    with pytest.raises(ValueError):
        log[::-1]

def test_iter_battle_log(log: BattleLog, events_valid: list[BattleEvent]):
    assert list(log) == events_valid
    assert list(reversed(log)) == list(reversed(events_valid))

def test_contains_battle_log(log: BattleLog, events_valid: list[BattleEvent]):
    assert events_valid[1] in log
    e1 = BattleEvent(
        timestamp=25.0,
        event_type=EventType.DEATH,
        actor="Knight",
        target="Orc"
    )
    assert e1 not in log
    e2 = BattleEvent(
        timestamp=10.0,
        event_type=EventType.BUFF,
        actor='Knight',
        target='Orc',
        tags={'stun'}
    )
    assert e2 in log
    assert 10 not in log
    assert 'Knight' not in log

def test_independent_battle_log(events_valid: list[BattleEvent]):
    log = BattleLog(events_valid)
    events_valid.clear()
    assert len(log) == 3

def test_repr_battle_log(log: BattleLog, events_valid: list[BattleEvent]):
    result = repr(log)
    assert 'BattleLog' in result
    assert 'count=3' in result
    assert repr(events_valid[0]) in result

    
