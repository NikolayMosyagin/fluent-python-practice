import pytest
from game_config import ConfigLayer, GameConfig
from dataclasses import FrozenInstanceError

@pytest.fixture
def layer1() -> ConfigLayer:
    return ConfigLayer("layer1", {'difficulty': 'normal', 'level': 15, 'pairs': None})

@pytest.fixture
def layer2() -> ConfigLayer:
    return ConfigLayer("layer2", {'game': 'knights', 'mission': 10, 'units': 10})

@pytest.fixture
def layer3() -> ConfigLayer:
    return ConfigLayer('layer3', {'volume': 10, 'music': 'trash_01'})

@pytest.fixture
def layer5() -> ConfigLayer:
    return ConfigLayer('layer5', {'difficulty': 'normal', 'level': 20, 'mission': 10.0})

@pytest.fixture
def layer6() -> ConfigLayer:
    return ConfigLayer('layer6', {'difficulty': 'hard', 'fullscreen': True, 'language': 'en', 'Unknown': None})


def test_config_layer():
    source = {'difficulty': 'normal', 'level': 15}
    with pytest.raises(TypeError):
        ConfigLayer(5, values=source)
    with pytest.raises(ValueError):
        ConfigLayer('', values=source)
    with pytest.raises(TypeError):
        ConfigLayer('test', values=['10', '20'])
    with pytest.raises(TypeError):
        ConfigLayer('test', values=5)
    error_source1 = {5: 'normal', None: 'test'}
    with pytest.raises(TypeError):
        ConfigLayer('test', values=error_source1)
    error_source2 = {'': 'test2'}
    with pytest.raises(ValueError):
        ConfigLayer('test2', values=error_source2)

    config = ConfigLayer('User', values=source)
    assert config.name == 'User'
    assert dict(config.values) == source
    source['difficulty'] = 'expert'
    assert dict(config.values) != source
    with pytest.raises(FrozenInstanceError):
        config.name = 'Default'
    with pytest.raises(FrozenInstanceError):
        config.values = {'10', 12, '14', 14}
    with pytest.raises(TypeError):
        config.values['difficulty'] = None


def test_empty_game_config():
    config = GameConfig()
    assert len(config) == 0
    assert dict(config) == {}

def test_parameter_game_config(layer1: ConfigLayer):
    with pytest.raises(TypeError):
        GameConfig(10)
    with pytest.raises(TypeError):
        GameConfig((layer1, [1, 2, 3], None))

def test_one_layer_game_config(layer1: ConfigLayer):
    config = GameConfig((layer1, ))
    assert dict(config) == layer1.values

def test_frozen_game_config(layer1: ConfigLayer):
    config = GameConfig((layer1, ))
    with pytest.raises(FrozenInstanceError):
        config.data = {"test", 5}
    with pytest.raises(TypeError):
        config.data['difficulty'] = 10

def test_non_intersecting_layers_game_config(layer1: ConfigLayer, layer2: ConfigLayer, layer3: ConfigLayer):
    config = GameConfig((layer1, layer2, layer3))
    assert len(config.data) == len(layer1.values) + len(layer2.values) + len(layer3.values)
    assert dict(config) == layer1.values | layer2.values | layer3.values

def test_intersecting_layers_game_config(layer1: ConfigLayer, layer2: ConfigLayer):
    test_layer = ConfigLayer('test_layer', {'level': 10, 'units': 30})
    config = GameConfig((layer1, layer2, test_layer))
    data = layer1.values | layer2.values
    data['level'] = 10
    data['units'] = 30
    assert len(config.data) == len(layer1.values) + len(layer2.values)
    assert dict(config) == data

def test_keys_order_game_config(layer1: ConfigLayer):
    other_layer = ConfigLayer('other_layer', {'difficulty': 'high', 'volume': 20})
    config = GameConfig((layer1, other_layer))
    assert list(config.keys()) == ['difficulty', 'level', 'pairs', 'volume']
    assert config['difficulty'] == 'high'


def test_independence_layers_game_config(layer1: ConfigLayer, layer2: ConfigLayer):
    layers = [layer1, layer2]
    config = GameConfig(layers)
    layers.clear()
    assert dict(config) == layer1.values | layer2.values


def test_missing_key_game_config(layer1: ConfigLayer, layer2: ConfigLayer):
    config = GameConfig((layer1, layer2))
    with pytest.raises(KeyError):
        config['mission_key']

def test_duplicate_name_layers_game_config(layer1: ConfigLayer):
    d_layer = ConfigLayer('layer1', {'test': 10, 'robot': 'a'})
    with pytest.raises(ValueError):
        GameConfig((layer1, d_layer))

def test_generator_game_config():
    config = GameConfig(ConfigLayer(f'Layer_{i}', {str(i): i}) for i in range(10))
    assert len(config) == 10
    assert dict(config) == {str(i): i for i in range(10)}
    assert len(config.layers) == 10
    assert config.layer_names() == tuple(f'Layer_{i}' for i in range(10))

def test_dict_methods_game_config(layer1: ConfigLayer):
    config = GameConfig((layer1, ))
    assert dict(config) == layer1.values
    assert config.keys() == layer1.values.keys()
    assert list(config.values()) == list(layer1.values.values())
    assert config.items() == layer1.values.items()
    assert config.get('difficulty') == 'normal'
    assert config.get('knight') == None
    assert config.get('knight', 'test') == 'test'

def test_repr_game_config(layer1: ConfigLayer):
    config = GameConfig((layer1, ))
    res = repr(config)
    assert 'GameConfig' in res 
    assert 'data=' in res
    assert "'difficulty': 'normal'" in res

def test_operation_empty_game_config():
    config1 = GameConfig()
    config2 = GameConfig()
    empty_result = frozenset()
    assert config1.added_keys(config2) == empty_result
    assert config2.removed_keys(config1) == empty_result
    assert config1.changed_keys(config2) == empty_result
    assert config2.unchanged_keys(config1) == empty_result

def test_operation_result_type_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((layer5, ))
    res_added_keys = config1.added_keys(config2)
    res_removed_keys = config2.removed_keys(config1)
    res_changed_keys = config1.changed_keys(config2)
    res_unchanged_keys = config1.unchanged_keys(config2)
    assert isinstance(res_added_keys, frozenset)
    assert isinstance(res_removed_keys, frozenset)
    assert isinstance(res_changed_keys, frozenset)
    assert isinstance(res_unchanged_keys, frozenset)
    assert all(isinstance(key, str) for key in res_added_keys)
    assert all(isinstance(key, str) for key in res_removed_keys)
    assert all(isinstance(key, str) for key in res_changed_keys)
    assert all(isinstance(key, str) for key in res_unchanged_keys)

def test_operation_parameter_type_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config = GameConfig((layer1, layer5))
    with pytest.raises(TypeError):
        config.added_keys(5)
    with pytest.raises(TypeError):
        config.removed_keys(None)
    with pytest.raises(TypeError):
        config.changed_keys('changed keys')
    with pytest.raises(TypeError):
        config.unchanged_keys([])

def test_operation_unchanged_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((layer5, ))
    config1.added_keys(config2)
    assert dict(config1) == dict(layer1.values) and dict(config2) == dict(layer5.values)
    config2.removed_keys(config1)
    assert dict(config1) == dict(layer1.values) and dict(config2) == dict(layer5.values)
    config2.changed_keys(config1)
    assert dict(config1) == dict(layer1.values) and dict(config2) == dict(layer5.values)
    config1.unchanged_keys(config2)
    assert dict(config1) == dict(layer1.values) and dict(config2) == dict(layer5.values)

def test_operation_with_empty_game_config(layer1: ConfigLayer):
    config = GameConfig((layer1, ))
    empty_config = GameConfig()
    r = config.added_keys(empty_config)
    assert r == frozenset()
    r = empty_config.added_keys(config)
    assert r == frozenset(config.keys())

    r = config.removed_keys(empty_config)
    assert r == frozenset(config.keys())
    r = empty_config.removed_keys(config)
    assert r == frozenset()

    r = config.changed_keys(empty_config)
    assert r == frozenset()
    r = empty_config.changed_keys(config)
    assert r == frozenset()

    r = config.unchanged_keys(empty_config)
    assert r == frozenset()
    r = empty_config.unchanged_keys(config)
    assert r == frozenset()

def test_operation_equal_game_config(layer1: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((layer1, ))

    r = config1.added_keys(config2)
    assert r == frozenset()

    r = config2.removed_keys(config1)
    assert r == frozenset()

    r = config1.changed_keys(config2)
    assert r == frozenset()

    r = config2.unchanged_keys(config1)
    assert r == frozenset(config1.keys())

def test_operation_common_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((layer5, ))

    assert config1.added_keys(config2) == frozenset(('mission', ))
    assert config1.removed_keys(config2) == frozenset(('pairs', ))
    assert config1.unchanged_keys(config2) == frozenset(('difficulty', ))
    assert config1.changed_keys(config2) == frozenset(('level', ))

def test_layers_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config = GameConfig((layer1, layer5))
    assert isinstance(config.layers, tuple)
    assert all(isinstance(layer, ConfigLayer) for layer in config.layers)
    assert config.layers == (layer1, layer5)
    empty_config = GameConfig()
    assert len(empty_config.layers) == 0

def test_layer_names_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config = GameConfig((layer1, layer5))
    res = config.layer_names()
    assert isinstance(res, tuple)
    assert all(isinstance(value, str) for value in res)
    assert config.layer_names() == (layer1.name, layer5.name)
    empty_config = GameConfig()
    assert len(empty_config.layer_names()) == 0

def test_get_layer_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config = GameConfig((layer1, layer5))
    with pytest.raises(TypeError):
        config.get_layer(5)
    with pytest.raises(KeyError):
        config.get_layer('layer2')
    res = config.get_layer('layer5')
    assert isinstance(res, ConfigLayer)
    assert res is layer5
    assert res == layer5

def test_with_overrides_game_config(layer1: ConfigLayer):
    config = GameConfig((layer1, ))
    empty_config = GameConfig()
    override_data = {'pairs': 'Source', 'new_key': 'test'}
    with pytest.raises(TypeError):
        config.with_overrides(5, override_data)
    with pytest.raises(TypeError):
        config.with_overrides('new_layer', ['test', None])
    with pytest.raises(TypeError):
        config.with_overrides('new_layer', {5:'test'})
    with pytest.raises(ValueError):
        config.with_overrides('layer1', override_data)
    updated = config.with_overrides('new_layer', override_data)
    assert isinstance(updated, GameConfig)
    assert dict(config) == dict(layer1.values)
    assert dict(config) != dict(updated)
    assert updated['pairs'] == 'Source' and config['pairs'] == None
    assert list(updated.keys()) == ['difficulty', 'level', 'pairs', 'new_key']
    override_data['new_key'] = 'updated_test'
    assert updated['new_key'] == 'test'
    assert updated.layer_names() == ('layer1', 'new_layer')
    assert updated is not config
    assert updated.get_layer('new_layer').values == {
        "pairs": "Source",
        "new_key": "test",
    }

    updated = empty_config.with_overrides('layer1', override_data)
    assert updated is not empty_config
    assert dict(updated) == override_data

    override_data2 = {'new_key1': 5, 'new_key2': 'key'}
    updated = config.with_overrides('layer2', override_data2)
    assert dict(updated) == layer1.values | override_data2


def test_merge_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config1 = GameConfig((layer1, ))
    with pytest.raises(TypeError):
        config1.merge([1, 2, 3])
    config2 = GameConfig((ConfigLayer('layer1', {}), ))
    with pytest.raises(ValueError):
        config1.merge(config2)

    empty_config1 = GameConfig()
    empty_config2 = GameConfig()
    res = empty_config1.merge(empty_config2)
    assert dict(res) == {}
    assert len(res.layers) == 0
    assert res is not empty_config1 and res is not empty_config2

    res = config1.merge(empty_config1)
    assert dict(res) == dict(layer1.values)
    assert len(res.layers) == 1
    assert res.layer_names() == tuple((layer1.name, ))
    assert res is not config1 and res is not empty_config1

    res = empty_config1.merge(config1)
    assert dict(res) == dict(layer1.values)
    assert len(res.layers) == 1
    assert res.layer_names() == tuple((layer1.name, ))
    assert res is not config1 and res is not empty_config1

    config5 = GameConfig((layer5, ))
    res = config1.merge(config5)
    assert len(res.layers) == 2
    assert res.layer_names() == tuple((layer1.name, layer5.name))
    assert res.get_layer('layer5') is layer5
    assert res.get_layer('layer1') is layer1
    assert res is not config1 and res is not config5
    assert list(res.data.keys()) == ['difficulty', 'level', 'pairs', 'mission']
    assert res['level'] == 20 and res['pairs'] == None
    assert dict(config1.data) == dict(layer1.values)
    assert dict(config5.data) == dict(layer5.values)
    res2 = config5.merge(config1)
    assert dict(res.data) != dict(res2.data)

    other_layer = ConfigLayer('other_layer', {'fullscreen': True, 'language': 'en'})
    other_config = GameConfig((other_layer, ))
    res = config1.merge(other_config)
    assert len(res.layers) == 2
    assert res.layer_names() == tuple((layer1.name, other_layer.name))
    assert res.get_layer('layer1') is layer1
    assert res.get_layer('other_layer') is other_layer
    assert res is not config1 and res is not other_config
    assert list(res.data.keys()) == ['difficulty', 'level', 'pairs', 'fullscreen', 'language']

def test_operator_or_game_config(layer1: ConfigLayer, layer5: ConfigLayer):
    config1 = GameConfig((layer1, ))
    with pytest.raises(TypeError):
        config1 | 10
    config2 = GameConfig((ConfigLayer('layer1', {}), ))
    with pytest.raises(ValueError):
        config1 | config2

    empty_config1 = GameConfig()
    empty_config2 = GameConfig()
    res = empty_config1 | empty_config2
    assert dict(res) == {}
    assert len(res.layers) == 0
    assert res is not empty_config1 and res is not empty_config2

    res = config1 | empty_config1
    assert dict(res) == dict(layer1.values)
    assert len(res.layers) == 1
    assert res.layer_names() == tuple((layer1.name, ))
    assert res is not config1 and res is not empty_config1

    res = empty_config1 | config1
    assert dict(res) == dict(layer1.values)
    assert len(res.layers) == 1
    assert res.layer_names() == tuple((layer1.name, ))
    assert res is not config1 and res is not empty_config1

    config5 = GameConfig((layer5, ))
    res = config1 | config5
    assert len(res.layers) == 2
    assert res.layer_names() == tuple((layer1.name, layer5.name))
    assert res.get_layer('layer5') is layer5
    assert res.get_layer('layer1') is layer1
    assert res is not config1 and res is not config5
    assert list(res.data.keys()) == ['difficulty', 'level', 'pairs', 'mission']
    assert res['level'] == 20 and res['pairs'] == None
    assert dict(config1.data) == dict(layer1.values)
    assert dict(config5.data) == dict(layer5.values)
    res2 = config5 | config1
    assert dict(res.data) != dict(res2.data)

    res_merge = config1.merge(config5)
    res2_merge = config5.merge(config1)
    assert dict(res.data) == dict(res_merge.data)
    assert dict(res2.data) == dict(res2_merge.data)
    assert res.layers == res_merge.layers
    assert res2.layers == res2_merge.layers
    assert res.layer_names() == res_merge.layer_names()
    assert res2.layer_names() == res2_merge.layer_names()

    other_layer = ConfigLayer('other_layer', {'fullscreen': True, 'language': 'en'})
    other_config = GameConfig((other_layer, ))
    res = config1 | other_config
    assert len(res.layers) == 2
    assert res.layer_names() == tuple((layer1.name, other_layer.name))
    assert res.get_layer('layer1') is layer1
    assert res.get_layer('other_layer') is other_layer
    assert res is not config1 and res is not other_config
    assert list(res.data.keys()) == ['difficulty', 'level', 'pairs', 'fullscreen', 'language']

def test_without_layer_game_config(layer1: ConfigLayer, layer5: ConfigLayer, layer6: ConfigLayer):
    config = GameConfig((layer1, layer5, layer6))
    with pytest.raises(TypeError):
        config.without_layer([1, 2, 3])
    with pytest.raises(KeyError):
        config.without_layer('layer2')

    empty_config = GameConfig()
    with pytest.raises(KeyError):
        empty_config.without_layer('layer1')

    config1 = GameConfig((layer1, ))
    res = config1.without_layer('layer1')
    assert len(res.layers) == 0
    assert res.layer_names() == tuple()
    assert dict(res.data) == {}
    assert res is not config1

    res = config.without_layer('layer1')
    assert len(res.layers) == 2
    assert res.layer_names() == tuple((layer5.name, layer6.name))
    assert dict(res.data) == dict(GameConfig((layer5, layer6)).data)

    res = config.without_layer('layer5')
    assert len(res.layers) == 2
    assert res.layer_names() == tuple((layer1.name, layer6.name))
    assert dict(res.data) == dict(GameConfig((layer1, layer6)).data)

    res = config.without_layer('layer6')
    assert len(res.layers) == 2
    assert res.layer_names() == tuple((layer1.name, layer5.name))
    assert res.get_layer(layer1.name) is layer1 and res.get_layer(layer5.name) is layer5
    assert dict(res.data) == dict(GameConfig((layer1, layer5)).data)
    assert res['difficulty'] == 'normal'
    assert 'language' not in res
    assert res is not config
    assert dict(config.data) == dict(GameConfig((layer1, layer5, layer6)).data)

def test_replace_layer_game_config(layer1: ConfigLayer, layer5: ConfigLayer, layer6: ConfigLayer):
    config = GameConfig((layer1, layer5, layer6))
    with pytest.raises(TypeError):
        config.replace_layer(10, {'difficulty': 'hard'})
    with pytest.raises(KeyError):
        config.replace_layer('layer2', {'difficulty': 'hard'})
    with pytest.raises(TypeError):
        config.replace_layer('layer1', ['difficulty', 'hard'])
    with pytest.raises(TypeError):
        config.replace_layer('layer1', {5: 'test'})

    replace_values = {'language':'ru', 'level': 30, 'difficulty': 'easy'}
    res = config.replace_layer('layer5', replace_values)
    assert isinstance(res, GameConfig)
    assert res.get_layer('layer5') is not layer5
    assert res.get_layer('layer1') is layer1
    assert res.get_layer('layer6') is layer6
    assert res['level'] == 30
    assert res.get_layer('layer5').values['difficulty'] == 'easy'
    assert res['difficulty'] == 'hard'
    assert dict(res.data) == dict(GameConfig((layer1, res.get_layer('layer5'), layer6)).data)
    assert dict(config.data) == dict(GameConfig((layer1, layer5, layer6)))
    assert res.layers == tuple((layer1, res.get_layer('layer5'), layer6))
    replace_values['level'] = 100
    assert res['level'] == 30

    config = GameConfig((layer1, ))
    res = config.replace_layer('layer1', {'update': 10, 'new_game': False})
    assert res['update'] == 10
    assert 'difficulty' not in res


def test_source_of_game_config(layer1: ConfigLayer, layer5: ConfigLayer, layer6: ConfigLayer, layer2: ConfigLayer):
    config = GameConfig((layer1, layer5, layer6))
    with pytest.raises(TypeError):
        config.source_of(5)
    with pytest.raises(KeyError):
        config.source_of('test_key')
    res = config.source_of('mission')
    assert isinstance(res, str)
    assert res == layer5.name
    assert dict(config.data) == dict(GameConfig((layer1, layer5, layer6)).data)
    res = config.source_of('Unknown')
    assert res == layer6.name
    res = config.source_of('pairs')
    assert res == layer1.name
    res = config.source_of('difficulty')
    assert res == layer6.name

    nconfig = config.without_layer('layer5')
    res = nconfig.source_of('level')
    assert res == layer1.name

    nconfig = config.replace_layer('layer5', {'pairs':'update'})
    res = nconfig.source_of('pairs')
    assert res == layer5.name

    nconfig = config.merge(GameConfig((layer2,)))
    res = nconfig.source_of('mission')
    assert res == layer2.name

    nconfig = config.with_overrides('layer2', {'fullscreen': False})
    res = nconfig.source_of('fullscreen')
    assert res == 'layer2'



