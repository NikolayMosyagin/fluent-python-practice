from models import BattleEvent, EventType
import pytest
from dataclasses import FrozenInstanceError



def test_create_battle_event():
    BattleEvent(
        20.0,
        EventType.DAMAGE,
        "Knight",
        "Orc",
        20,
        {"critical", "range"}
    )

    BattleEvent(
        35.0,
        EventType.BUFF,
        "Orc",
        "Knight"
    )

def test_tags_battle_event():
    st = {"critical", "range"}
    be = BattleEvent(
        20.0,
        EventType.DAMAGE,
        "Knight",
        "Orc",
        20,
        st
    )

    be2 = BattleEvent(
        35.0,
        EventType.BUFF,
        "Orc",
        "Knight"
    )

    assert type(be2.tags) is frozenset
    assert be2.tags != None and len(be2.tags) == 0

    st.add("poison effect")
    assert type(be.tags) is frozenset
    assert be.tags == frozenset(("critical", "range"))
    assert "poison effect" not in be.tags

def test_frozen_battle_event_fields():
    be = BattleEvent(
        20.0,
        EventType.DAMAGE,
        "Knight",
        "Orc",
        20,
        {"critical", "range"}
    )
    with pytest.raises(FrozenInstanceError):
        be.timestamp = 35.0
    with pytest.raises(FrozenInstanceError):
        be.event_type = EventType.BUFF
    with pytest.raises(FrozenInstanceError):
        be.actor = 'Unknown'
    with pytest.raises(FrozenInstanceError):
        be.target = 'Unknown'
    with pytest.raises(FrozenInstanceError):
        be.value = None
    with pytest.raises(FrozenInstanceError):
        be.tags = {"abc", "cdb"}

def test_equals_battle_event():
    be1 = BattleEvent(
        20.0,
        EventType.DAMAGE,
        "Knight",
        "Orc",
        20,
        {"critical", "range"}
    )

    be2 = BattleEvent(
        20.0,
        EventType.DAMAGE,
        "Knight",
        "Orc",
        20,
        {"critical", "range"}
    )

    be3 = BattleEvent(
        20.0,
        EventType.DAMAGE,
        "Unknown",
        "Orc",
        20,
        {"critical", "range"}
    )

    assert be1 == be2
    assert be1 != be3

def test_incorrect_fields_battle_event():
    with pytest.raises(ValueError):
        BattleEvent(-10.0, EventType.DAMAGE, "Unknown", "Orc")
    with pytest.raises(ValueError):
        BattleEvent(10.0, EventType.DAMAGE, '', "Orc")
    with pytest.raises(ValueError):
        BattleEvent(10.0, EventType.DAMAGE, "Unknown", None)
    with pytest.raises(ValueError):
        BattleEvent(10.0, EventType.DAMAGE, "Unknown", "Orc", -10)
    with pytest.raises(TypeError):
        BattleEvent(10.0, EventType.DAMAGE, "Unknown", "Orc", tags=['buff'])
    with pytest.raises(TypeError):
        BattleEvent(10.0, EventType.DAMAGE, "Unknown", "Orc", tags='buff') 

def test_repr_battle_event():
    be = BattleEvent(20.0, EventType.DAMAGE, "Knight", "Orc", 20, {"critical", "range"})     
    result = repr(be)
    
    assert "BattleEvent(" in result
    assert "timestamp=20.0" in result
    assert "event_type=EventType.DAMAGE" in result
    assert "actor='Knight'" in result
    assert "target='Orc'" in result
    assert "value=20" in result
    assert "'critical'" in result
    assert "'range'" in result
    
