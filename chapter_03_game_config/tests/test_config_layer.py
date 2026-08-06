import pytest
from game_config import ConfigLayer
from dataclasses import FrozenInstanceError

@pytest.fixture
def source() -> dict[str, object]:
    return  {'difficulty': 'normal', 'level': 15}

@pytest.fixture
def config(source: dict[str, object]) -> ConfigLayer:
    return ConfigLayer('User', values=source)

def test_rejects_invalid_name(source: dict[str, object]):
    with pytest.raises(TypeError):
        ConfigLayer(5, values=source)
    with pytest.raises(ValueError):
        ConfigLayer('', values=source)

def test_rejects_invalid_values():
    with pytest.raises(TypeError):
        ConfigLayer('test', values=['10', '20'])
    with pytest.raises(TypeError):
        ConfigLayer('test', values=5)

    with pytest.raises(TypeError):
        ConfigLayer('test', values={'test': 5, 5: 'normal'})
    with pytest.raises(ValueError):
        ConfigLayer('test2', values={'test': 10, '': 'test2'})

def test_is_immutable(config: ConfigLayer):
    with pytest.raises(FrozenInstanceError):
        config.name = 'Default'
    with pytest.raises(FrozenInstanceError):
        config.values = {'10', 12, '14', 14}
    with pytest.raises(TypeError):
        config.values['difficulty'] = None

def test_copies_source_mapping(source: dict[str, object]):
    config = ConfigLayer('Name', values=source)
    source['difficulty'] = None
    assert config.values['difficulty'] == 'normal'

def test_stores_name_and_values(config: ConfigLayer, source: dict[str, object]):
    assert config.name == 'User'
    assert dict(config.values) == source