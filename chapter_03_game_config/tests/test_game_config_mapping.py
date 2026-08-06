import pytest
from game_config import ConfigLayer, GameConfig
from dataclasses import FrozenInstanceError

def test_rejects_invalid_layers(simple_layer: ConfigLayer):
    with pytest.raises(TypeError):
        GameConfig(10)
    with pytest.raises(TypeError):
        GameConfig('test_value')
    with pytest.raises(TypeError):
        GameConfig([1, 2, 3])
    with pytest.raises(TypeError):
        GameConfig((simple_layer, None))

def test_is_immutable(simple_config: GameConfig):
    with pytest.raises(FrozenInstanceError):
        simple_config.data = {"test", 5}
    with pytest.raises(FrozenInstanceError):
        simple_config.layers = tuple()
    with pytest.raises(TypeError):
        simple_config.data['difficulty'] = 10

def test_rejects_missing_key(simple_config: GameConfig):
    with pytest.raises(KeyError):
        simple_config['mission_key']

def test_rejects_same_layer_name(simple_layer: ConfigLayer):
    other_layer1 = ConfigLayer('other_layer', {'other_key': 'other_value2'})
    other_layer2 = ConfigLayer('Test_Layer', {'other_key': 'other_value'})
    with pytest.raises(ValueError):
        GameConfig((simple_layer, other_layer1, other_layer2))

def test_create_empty():
    config = GameConfig()
    assert len(config) == 0
    assert config.layers == tuple()
    assert dict(config) == {}

def test_create_with_one_layer(simple_config: GameConfig, simple_layer: ConfigLayer):
    assert dict(simple_config) == simple_layer.values
    assert len(simple_config.layers) == 1
    assert simple_config.layers[0] is simple_layer

def test_create_using_generator():
    config = GameConfig(ConfigLayer(f'Layer_{i}', {str(i): i}) for i in range(10))
    assert len(config) == 10
    assert dict(config) == {str(i): i for i in range(10)}
    assert len(config.layers) == 10
    assert list(layer.name for layer in config.layers) == list(f'Layer_{i}' for i in range(10))

def test_repr(simple_config: GameConfig):
    res = repr(simple_config)
    assert 'GameConfig' in res 
    assert 'data=' in res
    assert "'test_key': 'test_value'" in res

def test_dict_methods(simple_config: GameConfig, simple_layer: ConfigLayer):
    assert dict(simple_config) == simple_layer.values
    assert simple_config.keys() == simple_layer.values.keys()
    assert list(simple_config.values()) == list(simple_layer.values.values())
    assert simple_config.items() == simple_layer.values.items()
    assert simple_config.get('test_key') == 'test_value'
    assert simple_config.get('knight') is None
    assert simple_config.get('knight', 'test') == 'test'

def test_keys_order():
    first_layer = ConfigLayer('first_layer', {'difficulty': 'easy', 'mask': 20})
    second_layer = ConfigLayer('second_layer', {'difficulty': 'high', 'volume': 20})
    config = GameConfig((first_layer, second_layer))
    assert list(config.keys()) == ['difficulty', 'mask', 'volume']
    assert config['difficulty'] == 'high'

def test_copies_source_layers_iterable():
    first_layer = ConfigLayer('first_layer', {'difficulty': 'easy', 'mask': 20})
    second_layer = ConfigLayer('second_layer', {'difficulty': 'high', 'volume': 20})
    layers = [first_layer, second_layer]
    config = GameConfig(layers)
    layers.clear()
    assert dict(config) == first_layer.values | second_layer.values
    assert config.layers == (first_layer, second_layer)
    assert config.layers[0] is first_layer
    assert config.layers[1] is second_layer

def test_create_with_non_intersecting_layers():
    first_layer = ConfigLayer('first_layer', {'test_key1': None})
    second_layer = ConfigLayer('second_layer', {'test_key2': 1})
    third_layer = ConfigLayer('third_layer', {'test_key3': [1, 2]})
    config = GameConfig((first_layer, second_layer, third_layer))
    assert len(config.data) == len(first_layer.values) + len(second_layer.values) + len(third_layer.values)
    assert dict(config) == first_layer.values | second_layer.values | third_layer.values

def test_create_intersecting_layers():
    first_layer = ConfigLayer('first_layer', {'test_key1': None, 'test_key2': 100})
    second_layer = ConfigLayer('second_layer', {'test_key2': 1})
    third_layer = ConfigLayer('third_layer', {'test_key1': 'test_value1', 'test_key3': [1, 2]})
    config = GameConfig((first_layer, second_layer, third_layer))
    assert len(config.data) == 3
    assert dict(config) == {'test_key1':'test_value1', 'test_key2': 1, 'test_key3': [1, 2]}