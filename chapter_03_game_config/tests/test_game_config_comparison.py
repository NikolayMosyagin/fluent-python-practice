import pytest
from game_config import ConfigLayer, GameConfig


def test_rejects_invalid_other_config(simple_config: GameConfig):
    with pytest.raises(TypeError):
        simple_config.added_keys(5)
    with pytest.raises(TypeError):
        simple_config.removed_keys(None)
    with pytest.raises(TypeError):
        simple_config.changed_keys('changed keys')
    with pytest.raises(TypeError):
        simple_config.unchanged_keys([])

def test_comparison_methods_return_frozensets(first_config: GameConfig, second_config: GameConfig):
    res_added_keys = first_config.added_keys(second_config)
    res_removed_keys = first_config.removed_keys(second_config)
    res_changed_keys = first_config.changed_keys(second_config)
    res_unchanged_keys = first_config.unchanged_keys(second_config)
    assert isinstance(res_added_keys, frozenset)
    assert isinstance(res_removed_keys, frozenset)
    assert isinstance(res_changed_keys, frozenset)
    assert isinstance(res_unchanged_keys, frozenset)
    assert all(isinstance(key, str) for key in res_added_keys)
    assert all(isinstance(key, str) for key in res_removed_keys)
    assert all(isinstance(key, str) for key in res_changed_keys)
    assert all(isinstance(key, str) for key in res_unchanged_keys)

def test_comparison_empty_configs():
    config1 = GameConfig()
    config2 = GameConfig()
    empty_result = frozenset()
    assert config1.added_keys(config2) == empty_result
    assert config2.removed_keys(config1) == empty_result
    assert config1.changed_keys(config2) == empty_result
    assert config2.unchanged_keys(config1) == empty_result

def test_comparison_with_empty_config(first_config: GameConfig):
    empty_config = GameConfig()
    empty_result = frozenset()
    r = first_config.added_keys(empty_config)
    assert r == empty_result
    r = empty_config.added_keys(first_config)
    assert r == frozenset(first_config.keys())

    r = first_config.removed_keys(empty_config)
    assert r == frozenset(first_config.keys())
    r = empty_config.removed_keys(first_config)
    assert r == empty_result

    r = first_config.changed_keys(empty_config)
    assert r == empty_result
    r = empty_config.changed_keys(first_config)
    assert r == empty_result

    r = first_config.unchanged_keys(empty_config)
    assert r == empty_result
    r = empty_config.unchanged_keys(first_config)
    assert r == empty_result

def test_comparison_identical_configs(first_layer: ConfigLayer):
    config1 = GameConfig((first_layer, ))
    config2 = GameConfig((first_layer, ))
    empty_result = frozenset()

    r = config1.added_keys(config2)
    assert r == empty_result

    r = config2.removed_keys(config1)
    assert r == empty_result

    r = config1.changed_keys(config2)
    assert r == empty_result

    r = config2.unchanged_keys(config1)
    assert r == frozenset(config1.keys())

def test_comparison_does_not_modify_configs(
        first_config: GameConfig, 
        first_layer: ConfigLayer,
        second_config: GameConfig,
        second_layer: ConfigLayer
    ):
    first_config.added_keys(second_config)
    assert dict(first_config) == dict(first_layer.values)
    assert dict(second_config) == dict(second_layer.values)
    second_config.removed_keys(first_config)
    assert dict(first_config) == dict(first_layer.values)
    assert dict(second_config) == dict(second_layer.values)
    second_config.changed_keys(first_config)
    assert dict(first_config) == dict(first_layer.values)
    assert dict(second_config) == dict(second_layer.values)
    first_config.unchanged_keys(second_config)
    assert dict(first_config) == dict(first_layer.values) 
    assert dict(second_config) == dict(second_layer.values)


def test_comparison_returns_expected_key_groups(first_config: GameConfig, second_config: GameConfig):
    assert first_config.added_keys(second_config) == frozenset(('third_key', ))
    assert first_config.removed_keys(second_config) == frozenset(('first_key', ))
    assert first_config.unchanged_keys(second_config) == frozenset()
    assert first_config.changed_keys(second_config) == frozenset(('second_key', ))