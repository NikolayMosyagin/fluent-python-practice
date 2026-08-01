import pytest
from game_config import ConfigDiff, GameConfig, ConfigLayer
from dataclasses import FrozenInstanceError

@pytest.fixture
def config_diff1() -> ConfigDiff:
    return ConfigDiff(
        added=['10', '20', 'test'],
        removed={'test1', 'test2'},
        changed=('test3', ),
        unchanged=(f'{i}_test' for i in range(3))
    )

@pytest.fixture
def layer1() -> ConfigLayer:
    return ConfigLayer('layer1', {'difficults': 'ease', 'music': 'main.mp3'})

@pytest.fixture()
def layer2() -> ConfigLayer:
    return ConfigLayer('layer2', {'volume': 30, 'difficults': 'hard', 'music': 'main.mp3'})

def test_empty_config_diff():
    empty = ConfigDiff()
    assert len(empty.added) == 0 and len(empty.removed) == 0 and len(empty.changed) == 0 and len(empty.unchanged) == 0

def test_default_value_config_diff():
    config = ConfigDiff(
        added=['10', '20', '30'],
        changed=['40'],
        unchanged=['100']
    )
    assert len(config.removed) == 0

    config = ConfigDiff(
        removed=['10', '20', '30'],
        changed=['40'],
        unchanged=['100']
    )
    assert len(config.added) == 0

    config = ConfigDiff(
        added=['10', '20', '30'],
        removed=['40'],
        unchanged=['100']
    )
    assert len(config.changed) == 0

    config = ConfigDiff(
        added=['10', '20', '30'],
        removed=['40'],
        changed=['100']
    )
    assert len(config.unchanged) == 0


def test_creation_errors_config_diff():
    with pytest.raises(TypeError):
        ConfigDiff(added=5, removed=['124'])
    with pytest.raises(TypeError):
        ConfigDiff(removed=10)
    with pytest.raises(TypeError):
        ConfigDiff(changed=True)
    with pytest.raises(TypeError):
        ConfigDiff(unchanged=False)

    with pytest.raises(TypeError):
        ConfigDiff(added=['1234', 5])
    with pytest.raises(TypeError):
        ConfigDiff(removed=['test', ['test']])
    with pytest.raises(TypeError):
        ConfigDiff(changed={123})
    with pytest.raises(TypeError):
        ConfigDiff(unchanged=('test', 12, 12.0))
    with pytest.raises(ValueError):
        ConfigDiff(added=['test', ''])

    first_set = ['10', '20']
    second_set = ['20', '30']
    with pytest.raises(ValueError):
        ConfigDiff(added=first_set, removed=second_set)
    with pytest.raises(ValueError):
        ConfigDiff(added=first_set, changed=second_set)
    with pytest.raises(ValueError):
        ConfigDiff(added=first_set, unchanged=second_set)
    with pytest.raises(ValueError):
        ConfigDiff(removed=first_set, changed=second_set)
    with pytest.raises(ValueError):
        ConfigDiff(removed=first_set, unchanged=second_set)       
    with pytest.raises(ValueError):
        ConfigDiff(changed=first_set, unchanged=second_set)    

def test_type_attributes_config_diff(config_diff1: ConfigDiff):
    assert isinstance(config_diff1.added, frozenset)
    assert isinstance(config_diff1.removed, frozenset)
    assert isinstance(config_diff1.changed, frozenset)
    assert isinstance(config_diff1.unchanged, frozenset)

def test_frozen_attributes_config_diff(config_diff1: ConfigDiff):
    with pytest.raises(FrozenInstanceError):
        config_diff1.added = ['10', '20']
    with pytest.raises(AttributeError):
        config_diff1.added.append('20')

    with pytest.raises(FrozenInstanceError):
        config_diff1.removed = frozenset(('test1', 'test2'))
    with pytest.raises(AttributeError):
            config_diff1.removed.append('test1')

    with pytest.raises(FrozenInstanceError):
        config_diff1.changed = frozenset(('test1', 'test2'))
    with pytest.raises(AttributeError):
        config_diff1.changed.append('test1')

    with pytest.raises(FrozenInstanceError):
        config_diff1.unchanged = frozenset(('test1', 'test2'))
    with pytest.raises(AttributeError):
        config_diff1.unchanged.append('test1')

def test_all_keys_config_diff(config_diff1: ConfigDiff):
    res = config_diff1.all_keys
    assert isinstance(res, frozenset)
    assert res is not config_diff1.added
    assert res is not config_diff1.removed
    assert res is not config_diff1.changed
    assert res is not config_diff1.unchanged
    assert res == frozenset(['10', '20', 'test', 'test1', 'test2', 'test3', '0_test', '1_test', '2_test'])
    assert config_diff1.added == frozenset(['10', '20', 'test'])
    assert config_diff1.removed == frozenset(['test1', 'test2'])
    assert config_diff1.changed == frozenset(['test3'])
    assert config_diff1.unchanged == frozenset(['0_test', '1_test', '2_test'])
    empty_diff = ConfigDiff()
    res = empty_diff.all_keys
    assert res is not empty_diff.added
    assert res is not empty_diff.removed
    assert res is not empty_diff.changed
    assert res is not empty_diff.unchanged
    assert res == frozenset({})


def test_has_changes_config_diff(config_diff1: ConfigDiff):
    assert config_diff1.has_changes
    empty_diff = ConfigDiff()
    assert not empty_diff.has_changes
    keys = ['10', '20']
    assert ConfigDiff(added=keys).has_changes
    assert ConfigDiff(removed=keys).has_changes
    assert ConfigDiff(changed=keys).has_changes
    assert not ConfigDiff(unchanged=keys).has_changes

def test_bool_config_diff(config_diff1: ConfigDiff):
    assert bool(config_diff1)
    assert bool(config_diff1) == config_diff1.has_changes
    empty_diff = ConfigDiff()
    assert not empty_diff
    keys = ['10', '20']
    assert bool(ConfigDiff(added=keys))
    assert bool(ConfigDiff(removed=keys))
    assert bool(ConfigDiff(changed=keys))
    assert not bool(ConfigDiff(unchanged=keys))


def test_independence_config_diff():
    value_list = ['10', '20']
    value_set = {'10', '20'}
    
    config_diff = ConfigDiff(added=value_list)
    assert config_diff.added == frozenset(value_list)
    value_list.append('30')
    assert config_diff.added == frozenset(['10', '20'])

    config_diff = ConfigDiff(removed=value_set)
    assert config_diff.removed == frozenset(value_set)
    value_set.add('30')
    assert config_diff.removed == frozenset(['10', '20'])

def test_equals_config_diff():
    assert ConfigDiff(
        added={'test1', 'test2'},
        unchanged={'test3', 'test4'}
    ) == ConfigDiff(
        added= {'test1', 'test2'},
        unchanged={'test3', 'test4'}
    )

def test_repr_config_diff(config_diff1: ConfigDiff):
    res = repr(config_diff1)
    assert 'ConfigDiff(' in res
    assert 'added=frozenset(' in res
    assert 'removed=frozenset(' in res
    assert 'changed=frozenset(' in res
    assert 'unchanged=frozenset(' in res

def test_diff_empty_game_config():
    config1 = GameConfig()
    config2 = GameConfig()
    diff = config1.diff(config2)
    assert len(diff.added) == 0 and len(diff.removed) == 0 and len(diff.changed) == 0 and len(diff.unchanged) == 0

def test_diff_equals_game_config(layer1: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((layer1, ))
    diff = config1.diff(config2)
    assert len(diff.added) == 0 and len(diff.removed) == 0 and len(diff.changed) == 0 and len(diff.unchanged) == len(layer1.values)
    assert diff.unchanged == frozenset(layer1.values.keys())

def test_diff_only_added_keys_game_config(layer1: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((
        ConfigLayer(
            'layer2',
            {'difficults': 'ease', 'music': 'main.mp3', 'volume': 25}
        ), 
    ))
    diff = config1.diff(config2)
    assert len(diff.removed) == 0 and len(diff.changed) == 0
    assert len(diff.added) == 1
    assert len(diff.unchanged) == 2
    assert diff.added == frozenset(('volume', ))
    assert diff.unchanged == frozenset(layer1.values.keys())

def test_diff_only_removed_keys_game_config(layer1: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((
        ConfigLayer(
            'layer2',
            {'music': 'main.mp3'}
        ),

    ))
    diff = config1.diff(config2)
    assert len(diff.added) == 0 and len(diff.changed) == 0
    assert len(diff.removed) == 1
    assert len(diff.unchanged) == 1
    assert diff.removed == frozenset(('difficults', ))
    assert diff.unchanged == frozenset(('music', ))

def test_diff_only_changed_keys_game_config(layer1: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((
        ConfigLayer(
            'layer2',
            {'difficults': 'hard', 'music': 'new_main.mp3'}
        ),
    ))
    diff = config1.diff(config2)
    assert len(diff.added) == 0 and len(diff.removed) == 0 and len(diff.unchanged) == 0
    assert len(diff.changed) == 2
    assert diff.changed == frozenset(('difficults', 'music'))

def test_diff_errors_game_config(layer1: ConfigLayer):
    config1 = GameConfig((layer1, ))
    with pytest.raises(TypeError):
        config1.diff(5)
    with pytest.raises(TypeError):
        config1.diff(layer1)

def test_diff_type_game_config(layer1: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((
        ConfigLayer(
            'layer2', {'volume': 30}
        ),
    ))
    diff = config1.diff(config2)
    assert isinstance(diff, ConfigDiff)

def test_diff_equivalence_game_diff(layer1: ConfigLayer, layer2: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((layer2, ))
    diff = config1.diff(config2)
    assert diff.added == config1.added_keys(config2)
    assert diff.removed == config1.removed_keys(config2)
    assert diff.changed == config1.changed_keys(config2)
    assert diff.unchanged == config1.unchanged_keys(config2)

def test_diff_unchanged_game_diff(layer1: ConfigLayer, layer2: ConfigLayer):
    config1 = GameConfig((layer1, ))

    config2 = GameConfig((layer2, ))
    diff = config1.diff(config2)
    assert dict(config1) == dict(layer1.values)
    assert dict(config2) == dict(layer2.values)

def test_diff_common_game_diff(layer1: ConfigLayer, layer2: ConfigLayer):
    config1 = GameConfig((layer1, ConfigLayer('layer_test', {'test1': 'test2'})))
    config2 = GameConfig((layer2, ))

    diff = config1.diff(config2)
    assert len(diff.added) > 0 and len(diff.removed) > 0 and len(diff.changed) > 0 and len(diff.unchanged) > 0
    assert diff.added == frozenset(('volume', ))
    assert diff.removed == frozenset(('test1', ))
    assert diff.changed == frozenset(('difficults', ))
    assert diff.unchanged == frozenset(('music', ))


def test_diff_directions_game_diff(layer1: ConfigLayer, layer2: ConfigLayer):
    config1 = GameConfig((layer1, ))
    config2 = GameConfig((layer2, ))

    diff1 = config1.diff(config2)
    diff2 = config2.diff(config1)

    assert diff1.changed == diff2.changed and diff1.unchanged == diff2.unchanged
    assert diff1.added == diff2.removed and diff1.removed == diff2.added



