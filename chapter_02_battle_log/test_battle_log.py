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
def events_valid_6() -> list[BattleEvent]:
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
            event_type=EventType.DAMAGE,
            actor='knight',
            target='Orc',
            value=20,
            tags={'melee'}
        ),
        BattleEvent(
            timestamp=15.0,
            event_type=EventType.HEAL,
            actor='Wizard',
            target='Knight',
            value=20,
            tags={'intellect'}
        ),
        BattleEvent(
            timestamp=25.2,
            event_type=EventType.DEBUFF,
            actor='Jinn',
            target='Troll',
            tags={"poison"}
        ),
        BattleEvent(
            timestamp=31.5,
            event_type=EventType.DAMAGE,
            actor='Wizard',
            target='Shaman',
            value=100,
            tags={'critical', 'range'}
        ),
        BattleEvent(
            timestamp=47.0,
            event_type=EventType.BUFF,
            actor='Shaman',
            target='Orc',
            tags={'invisible'}
        ),
    ]

@pytest.fixture
def log(events_valid: list[BattleEvent]) -> BattleLog:
    return BattleLog(events_valid)

@pytest.fixture
def log6(events_valid_6: list[BattleEvent]) -> BattleLog:
    return BattleLog(events_valid_6)

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

def test_filtration_battle_log(log6: BattleLog, events_valid_6: list[BattleEvent]):
    log_type = log6.by_type(EventType.DAMAGE)
    assert isinstance(log_type, BattleLog)
    assert log_type[0] is events_valid_6[0]
    assert list(log_type) == [events_valid_6[0], events_valid_6[1], events_valid_6[4]]
    log_type2 = log6.by_type(EventType.DEATH)
    assert list(log_type2) == []
    log_type3 = log6.by_type(EventType.HEAL)
    assert list(log_type3) == [events_valid_6[2]]

    log_actor = log6.by_actor('Knight')
    assert isinstance(log_actor, BattleLog)
    assert log_actor[0] is events_valid_6[0]
    assert list(log_actor) == [events_valid_6[0]]
    log_actor2 = log6.by_actor('Unknown')
    assert list(log_actor2) == []

    log_target = log6.by_target('Orc')
    assert isinstance(log_target, BattleLog)
    assert log_target[2] is events_valid_6[5]
    assert list(log_target) == [events_valid_6[0], events_valid_6[1], events_valid_6[5]]
    log_target2 = log6.by_target('Unknown')
    assert list(log_target2) == []

    log_tag = log6.by_tag('critical')
    assert isinstance(log_tag, BattleLog)
    assert list(log_tag) == [events_valid_6[0], events_valid_6[4]]
    assert log_tag[1] is events_valid_6[4]
    log_tag2 = log6.by_tag('Invisible')
    assert list(log_tag2) == []
    log_tag3 = log6.by_tag('invisible')
    assert list(log_tag3) == [events_valid_6[5]]

    empty = BattleLog()
    assert len(empty.by_type(EventType.DAMAGE)) == 0
    assert len(empty.by_actor('Knight')) == 0
    assert len(empty.by_target('Orc')) == 0
    assert len(empty.by_tag('critical')) == 0
    assert len(empty.between(0, 10)) == 0
    assert len(empty.last()) == 0

def test_between_battle_log(log6: BattleLog, events_valid_6: list[BattleEvent]):
    with pytest.raises(ValueError):
        log6.between(-1, 10)
    with pytest.raises(ValueError):
        log6.between(10, -6)
    with pytest.raises(ValueError):
        log6.between(10, 8)
    
    log_between0 = log6.between(0, 1)
    assert isinstance(log_between0, BattleLog)
    assert list(log_between0) == []
    log_between1 = log6.between(0, 10)
    assert log_between1[0] is events_valid_6[0]
    assert list(log_between1) == [events_valid_6[0], events_valid_6[1]]
    log_between2 = log6.between(10.1, 25.0)
    assert list(log_between2) == [events_valid_6[2]]
    log_between3 = log6.between(31.0, 50.0)
    assert list(log_between3) == [events_valid_6[4], events_valid_6[5]]
    log_between4 = log6.between(50, 100)
    assert list(log_between4) == []
    log_between5 = log6.between(15.0, 25.2)
    assert list(log_between5) == events_valid_6[2:4]

def test_last_battle_log(log6: BattleLog, events_valid_6: list[BattleEvent]):
    with pytest.raises(ValueError):
        log6.last(-3)
    log_last0 = log6.last(limit=0)
    assert list(log_last0) == []
    log_last1 = log6.last(limit=10)
    assert isinstance(log_last1, BattleLog)
    assert list(log_last1) == events_valid_6
    log_last2 = log6.last(limit=1)
    assert list(log_last2) == [events_valid_6[-1]]
    assert log_last2[0] is events_valid_6[-1]
    log_last3 = log6.last()
    assert list(log_last3) == events_valid_6[3:]


    
