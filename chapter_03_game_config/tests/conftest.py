import pytest
from game_config import ConfigLayer, GameConfig

@pytest.fixture
def simple_layer() -> ConfigLayer:
    return ConfigLayer('Test_Layer', {'test_key': 'test_value'})

@pytest.fixture
def first_layer() -> ConfigLayer:
    return ConfigLayer('First Layer', {'first_key': 100, 'second_key': 'second_value1'})

@pytest.fixture
def second_layer() -> ConfigLayer:
    return ConfigLayer('Second Layer', {'second_key': 'second_value2', 'third_key': 'third_value1'})

@pytest.fixture
def third_layer() -> ConfigLayer:
    return ConfigLayer('Third Layer', {'third_key': None, 'fourth_key': 'fourth_value1', 'new_key': 10})

@pytest.fixture
def simple_config(simple_layer: ConfigLayer) -> GameConfig:
    return GameConfig((simple_layer, ))

@pytest.fixture
def first_config(first_layer: ConfigLayer) -> GameConfig:
    return GameConfig((first_layer, ))

@pytest.fixture
def second_config(second_layer: ConfigLayer) -> GameConfig:
    return GameConfig((second_layer, ))