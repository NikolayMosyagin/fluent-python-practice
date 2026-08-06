import pytest
from game_config import GameConfig, ConfigLayer

def test_layers_are_stored_as_tuple(first_layer: ConfigLayer, second_layer: ConfigLayer):
    config = GameConfig((first_layer, second_layer))
    assert isinstance(config.layers, tuple)
    assert all(isinstance(layer, ConfigLayer) for layer in config.layers)
    assert len(config.layers) == 2
    assert config.layers[0] is first_layer
    assert config.layers[1] is second_layer
    empty_config = GameConfig()
    assert len(empty_config.layers) == 0

def test_layer_names_returns_names_in_order(first_layer: ConfigLayer, second_layer: ConfigLayer):
    config = GameConfig((first_layer, second_layer))
    res = config.layer_names()
    assert isinstance(res, tuple)
    assert all(isinstance(value, str) for value in res)
    assert config.layer_names() == (first_layer.name, second_layer.name)
    empty_config = GameConfig()
    assert len(empty_config.layer_names()) == 0

def test_get_layer_rejects_invalid_name_type(first_config: GameConfig):
    with pytest.raises(TypeError):
        first_config.get_layer(5)
    with pytest.raises(TypeError):
        first_config.get_layer([1, 2, 3])
    with pytest.raises(TypeError):
        first_config.get_layer(('test', 'test2'))

def test_get_layer_raises_for_missing_layer(first_config: GameConfig):
    with pytest.raises(KeyError):
        first_config.get_layer('layer2')
    with pytest.raises(KeyError):
        first_config.get_layer('first layer')
    with pytest.raises(KeyError):
        first_config.get_layer('First layer')

def test_get_layer_returns_existing_layer(first_layer: ConfigLayer, second_layer: ConfigLayer):
    config = GameConfig((first_layer, second_layer))
    res = config.get_layer('Second Layer')
    assert isinstance(res, ConfigLayer)
    assert res is second_layer
    assert res == second_layer

def test_with_overrides_rejects_invalid_arguments(first_config: GameConfig):
    valid_data = {'first_key': 50}
    with pytest.raises(TypeError):
        first_config.with_overrides(5, valid_data)
    with pytest.raises(TypeError):
        first_config.with_overrides([1, 2, 3], valid_data)
    with pytest.raises(TypeError):
        first_config.with_overrides(('first', 'second'), valid_data)
    with pytest.raises(TypeError):
        first_config.with_overrides('new_layer', ['test', None])
    with pytest.raises(TypeError):
        first_config.with_overrides('new_layer', {5:'test'})

def test_with_overrides_rejects_duplicate_layer_name(first_config: GameConfig):
    with pytest.raises(ValueError):
        first_config.with_overrides('First Layer', {'first_key': 50})


def test_with_overrides_works_with_empty_config():
    empty_config = GameConfig()
    data = {'new_key': 'new_value'}
    updated = empty_config.with_overrides('New Layer', data)
    assert updated is not empty_config
    assert dict(updated) == data
    assert len(empty_config) == 0
    assert len(empty_config.layers) == 0

def test_with_overrides_copies_source_mapping(first_config: GameConfig):
    data = {'new_key': 50, 'first_key': None}
    updated = first_config.with_overrides('New Layer', data)
    assert updated['new_key'] == 50
    assert updated['first_key'] is None
    data['new_key'] = 1000
    assert updated['new_key'] == 50

def test_with_overrides_adds_high_priority_layer(first_config: GameConfig, first_layer: ConfigLayer):
    data = {'first_key': 50, 'new_key': 'new_value'}
    updated = first_config.with_overrides('New Layer', data)
    assert isinstance(updated, GameConfig)
    assert dict(first_config) == dict(first_layer.values)
    assert dict(first_config) != dict(updated)
    assert updated['first_key'] == 50 and first_config['first_key'] == 100
    assert list(updated.keys()) == ['first_key', 'second_key', 'new_key']
    assert updated.layer_names() == ('First Layer', 'New Layer')
    assert updated is not first_config
    assert updated.get_layer('New Layer').values == {'first_key': 50, 'new_key': 'new_value'}

    data = {'new_key1': 5, 'new_key2': 'key'}
    updated = first_config.with_overrides('layer2', data)
    assert dict(updated) == first_layer.values | data

def test_merge_rejects_invalid_config(first_config: GameConfig):
    with pytest.raises(TypeError):
        first_config.merge([1, 2, 3])
    with pytest.raises(TypeError):
        first_config.merge({'data': 'value'})
    with pytest.raises(TypeError):
        first_config.merge(5)

def test_merge_rejects_duplicate_layer_names(first_config: GameConfig):
     with pytest.raises(ValueError):
        first_config.merge(
            GameConfig(
                (ConfigLayer('First Layer', {}), )
            )
        )

def test_merge_with_empty_config(first_config: GameConfig, first_layer: ConfigLayer):
    empty_config1 = GameConfig()
    empty_config2 = GameConfig()
    res = empty_config1.merge(empty_config2)
    assert dict(res) == {}
    assert len(res.layers) == 0
    assert res is not empty_config1 and res is not empty_config2

    res = first_config.merge(empty_config1)
    assert dict(res) == dict(first_layer.values)
    assert len(res.layers) == 1
    assert res.layer_names() == (first_layer.name, )
    assert res is not first_config and res is not empty_config1

    res = empty_config1.merge(first_config)
    assert dict(res) == dict(first_layer.values)
    assert len(res.layers) == 1
    assert res.layer_names() == (first_layer.name, )
    assert res is not first_config and res is not empty_config1

def test_merge_preserves_layer_order(first_config: GameConfig, second_config: GameConfig):
    first_layer = first_config.layers[0]
    second_layer = second_config.layers[0]
    res = first_config.merge(second_config)
    assert len(res.layers) == 2
    assert res.layer_names() == (first_layer.name, second_layer.name)
    assert res.get_layer('First Layer') is first_layer
    assert res.get_layer('Second Layer') is second_layer

def test_merge_uses_right_config_priority(first_config: GameConfig, second_config: GameConfig):
    res = first_config.merge(second_config)
    assert res is not first_config and res is not second_config
    assert list(res.data.keys()) == ['first_key', 'second_key', 'third_key']
    assert res['first_key'] == 100 and res['second_key'] == 'second_value2'
    res2 = second_config.merge(first_config)
    assert dict(res.data) != dict(res2.data)

def test_merge_does_not_modify_sources(first_config: GameConfig, second_config: GameConfig):
    first_layer = first_config.layers[0]
    second_layer = second_config.layers[0]
    first_config.merge(second_config)
    assert dict(first_config.data) == dict(first_layer.values)
    assert dict(second_config.data) == dict(second_layer.values)

def test_or_rejects_unsupported_operand(first_config: GameConfig):
    with pytest.raises(TypeError):
        first_config | 10
    with pytest.raises(TypeError):
        first_config | '1234'
    with pytest.raises(TypeError):
        first_config | [1, 2, 3, '123']
    with pytest.raises(TypeError):
        first_config | {'data': 'test'}

def test_or_rejects_duplicate_layer_names(first_config: GameConfig):
    config = GameConfig(
        (ConfigLayer('First Layer', {}), )
    )
    with pytest.raises(ValueError):
        (first_config | config)

def test_or_returns_same_result_as_merge(first_config: GameConfig, second_config: GameConfig):
    res = first_config | second_config
    res_merge = first_config.merge(second_config)
    assert dict(res.data) == dict(res_merge.data)
    assert res.layers == res_merge.layers
    assert res.layer_names() == res_merge.layer_names()

def test_without_layer_rejects_invalid_name(first_config: GameConfig):
    with pytest.raises(TypeError):
        first_config.without_layer([1, 2, 3])
    with pytest.raises(TypeError):
        first_config.without_layer(('12', '233'))
    with pytest.raises(TypeError):
        first_config.without_layer({'set', 'set1'})


def test_without_layer_raises_for_missing_layer(first_config: GameConfig):
    empty_config = GameConfig()
    with pytest.raises(KeyError):
        empty_config.without_layer('Layer 1')
    with pytest.raises(KeyError):
        first_config.without_layer('first layer')
    with pytest.raises(KeyError):
        first_config.without_layer('First layer')

def test_without_layer_removes_only_layer(first_config: GameConfig):
    res = first_config.without_layer('First Layer')
    assert len(res.layers) == 0
    assert res.layer_names() == tuple()
    assert dict(res.data) == {}
    assert res is not first_config

def test_without_layer_removes_layer(
        first_layer: ConfigLayer,
        second_layer: ConfigLayer, 
        third_layer: ConfigLayer
):
    config = GameConfig((first_layer, second_layer, third_layer))
    res = config.without_layer('First Layer')
    assert len(res.layers) == 2
    assert res.layer_names() == (second_layer.name, third_layer.name)
    assert dict(res.data) == dict(GameConfig((second_layer, third_layer)).data)
    assert res.get_layer(second_layer.name) is second_layer 
    assert res.get_layer(third_layer.name) is third_layer

    res = config.without_layer('Second Layer')
    assert len(res.layers) == 2
    assert res.layer_names() == (first_layer.name, third_layer.name)
    assert dict(res.data) == dict(GameConfig((first_layer, third_layer)).data)
    assert res.get_layer(first_layer.name) is first_layer 
    assert res.get_layer(third_layer.name) is third_layer

    res = config.without_layer('Third Layer')
    assert len(res.layers) == 2
    assert res.layer_names() == (first_layer.name, second_layer.name)
    assert res.get_layer(first_layer.name) is first_layer 
    assert res.get_layer(second_layer.name) is second_layer
    assert dict(res.data) == dict(GameConfig((first_layer, second_layer)).data)
    assert res['third_key'] == 'third_value1'
    assert 'fourth_key' not in res

def test_without_layer_does_not_modify_original_config(first_config: GameConfig):
    first_layer = first_config.layers[0]
    res = first_config.without_layer('First Layer')
    assert dict(first_config.data) == dict(GameConfig((first_layer, )).data)
    assert res is not first_config

def test_replace_layer_rejects_invalid_arguments(first_config: GameConfig):
    with pytest.raises(TypeError):
        first_config.replace_layer(10, {'difficulty': 'hard'})
    with pytest.raises(TypeError):
        first_config.replace_layer('First Layer', ['difficulty', 'hard'])
    with pytest.raises(TypeError):
        first_config.replace_layer('First Layer', {5: 'test'})

def test_replace_layer_raises_for_missing_layer(first_config: GameConfig):
    with pytest.raises(KeyError):
        first_config.replace_layer('layer2', {'difficulty': 'hard'})

def test_replace_layer_copies_source_mapping(first_config: GameConfig):
    replace_values = {'second_key':'ru'}
    res = first_config.replace_layer('First Layer', replace_values)
    replace_values['second_key'] = 100
    assert res['second_key'] == 'ru'

def test_replace_layer_replaces_only_layer(first_config: GameConfig):
    res = first_config.replace_layer('First Layer', {'update': 10, 'new_game': False})
    assert res['update'] == 10
    assert 'first_key' not in res
    assert 'second_key' not in res

def test_replace_layer_does_not_modify_original_config(
    first_layer: ConfigLayer,
    second_layer: ConfigLayer,
    third_layer: ConfigLayer
):
    config = GameConfig((first_layer, second_layer, third_layer))
    original_data = dict(config)
    original_layers = config.layers
    replace_values = {'second_key':'ru', 'third_key': 200, 'new_replace_key': 'easy'}
    res = config.replace_layer('Second Layer', replace_values)
    assert dict(config) == original_data
    assert original_layers is config.layers
    assert res is not config

def test_replace_layer_preserves_layer_position(
    first_layer: ConfigLayer,
    second_layer: ConfigLayer,
    third_layer: ConfigLayer    
):
    config = GameConfig((first_layer, second_layer, third_layer))
    replace_values = {'second_key':'ru', 'third_key': 200, 'new_replace_key': 'easy'}   
    res = config.replace_layer('Second Layer', replace_values)
    assert isinstance(res, GameConfig)
    assert res.layer_names() == (first_layer.name, second_layer.name, third_layer.name)
    new_second_layer = res.get_layer('Second Layer')
    assert res.layers[0] is first_layer
    assert res.layers[2] is third_layer
    assert new_second_layer is not second_layer
    assert new_second_layer.name == second_layer.name
    
def test_replace_layer_rebuilds_effective_values(
    first_layer: ConfigLayer,
    second_layer: ConfigLayer,
    third_layer: ConfigLayer         
):
    config = GameConfig((first_layer, second_layer, third_layer))
    replace_values = {'third_key': 200, 'new_replace_key': 'easy'}
    res = config.replace_layer('Second Layer', replace_values)
    new_second_layer = res.get_layer('Second Layer')
    assert new_second_layer.values['third_key'] == 200
    assert res['third_key'] is None
    assert res['new_replace_key'] == 'easy'
    assert res['second_key'] == 'second_value1'

def test_source_of_rejects_invalid_key(first_config: GameConfig):
    with pytest.raises(TypeError):
        first_config.source_of(5)
    with pytest.raises(TypeError):
        first_config.source_of(['1234'])

def test_source_of_raises_for_missing_key(first_config: GameConfig):
    with pytest.raises(KeyError):
        first_config.source_of('test_key')
    with pytest.raises(KeyError):
        first_config.source_of('First layer')

def test_source_of_returns_highest_priority_layer(
    first_layer: ConfigLayer, 
    second_layer: ConfigLayer, 
    third_layer: ConfigLayer
):
    config = GameConfig((first_layer, second_layer, third_layer))
    res = config.source_of('second_key')
    assert isinstance(res, str)
    assert res == second_layer.name
    assert dict(config.data) == dict(GameConfig((first_layer, second_layer, third_layer)).data)
    res = config.source_of('third_key')
    assert res == third_layer.name
    res = config.source_of('first_key')
    assert res == first_layer.name

def test_source_of_reflects_layer_changes(
    first_layer: ConfigLayer, 
    second_layer: ConfigLayer, 
    third_layer: ConfigLayer        
):
    config = GameConfig((first_layer, second_layer, third_layer))

    nconfig = config.without_layer('Second Layer')
    res = nconfig.source_of('second_key')
    assert res == first_layer.name

    nconfig = config.replace_layer('Second Layer', {'pairs':'update'})
    res = nconfig.source_of('pairs')
    assert res == 'Second Layer'

    nconfig = config.merge(GameConfig((ConfigLayer('New Layer', {'second_key': 'test_mission'}),)))
    res = nconfig.source_of('second_key')
    assert res == 'New Layer'

    nconfig = config.with_overrides('New Layer', {'first_key': False})
    res = nconfig.source_of('first_key')
    assert res == 'New Layer'
