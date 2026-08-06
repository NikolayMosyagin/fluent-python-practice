from collections.abc import Mapping, Iterable, Iterator
from dataclasses import dataclass
from types import MappingProxyType, NotImplementedType


@dataclass(frozen=True)
class ConfigLayer:
    name: str
    values: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("The parameter 'name' must have a type 'str'")
        if self.name == '':
            raise ValueError("The parameter 'name' must not be empty")
        if not isinstance(self.values, Mapping):
            raise TypeError("The parameter 'values' must have a type 'Mapping'")
        if not all(isinstance(key, str) for key in self.values):
            raise TypeError("The keys of parameter 'values' must be of type 'str'")
        if any(key == '' for key in self.values):
            raise ValueError("The keys of parameter 'values' must not be empty")
        object.__setattr__(self, 'values', MappingProxyType(dict(self.values)))


@dataclass(frozen=True, init=False)
class ConfigDiff:
    added: frozenset[str]
    removed: frozenset[str]
    changed: frozenset[str]
    unchanged: frozenset[str]

    def __init__(
        self, 
        added: Iterable[str] | None = None, 
        removed: Iterable[str] | None = None, 
        changed: Iterable[str] | None = None, 
        unchanged: Iterable[str] | None = None
    ) -> None:
        self._update_attributes('added', added)
        self._update_attributes('removed', removed)
        self._update_attributes('changed', changed)
        self._update_attributes('unchanged', unchanged)
        if self._has_intersections():
            raise ValueError(
                "Attributes 'added', 'removed', 'changed', and 'unchanged' "
                "must not overlap"
            )

    def _update_attributes(self, name: str, value: Iterable[str] | None) -> None:
        if value is None:
            object.__setattr__(self, name, frozenset())
        elif not isinstance(value, Iterable) or isinstance(value, str):
            raise TypeError(f"The parameter {name!r} must have a type 'Iterable[str]' or 'None'")
        else:
            final_values = frozenset(value)
            if not all(isinstance(key, str) for key in final_values):
                raise TypeError(f"All {name!r} elements must be of type 'str'")
            if not all(key != '' for key in final_values):
                raise ValueError("The keys of parameter 'value' must not be empty")
            object.__setattr__(self, name, final_values)

    def _has_intersections(self) -> bool:
        return (
            bool(self.added & self.removed) or bool(self.added & self.changed) or 
            bool(self.added & self.unchanged) or bool(self.removed & self.changed) or 
            bool(self.removed & self.unchanged) or bool(self.changed & self.unchanged)
        )

    @property
    def all_keys(self) -> frozenset[str]:
        return self.added | self.removed | self.changed | self.unchanged
    
    @property
    def has_changes(self) -> bool:
        return len(self.added) > 0 or len(self.removed) > 0 or len(self.changed) > 0

    def __bool__(self) -> bool:
        return self.has_changes


@dataclass(frozen=True, init=False)
class GameConfig(Mapping[str, object]):
    data: MappingProxyType[str, object]
    layers: tuple[ConfigLayer, ...]

    def __init__(self, layers: Iterable[ConfigLayer] | None = None) -> None:
        if layers is None: 
            object.__setattr__(self, 'data', MappingProxyType({}))
            object.__setattr__(self, 'layers', tuple())
            return
        if not isinstance(layers, Iterable):
            raise TypeError("The parameter 'layers' must have a type 'Iterable[ConfigLayer]' or 'None'")
        
        temp_layers: set[str] = set()
        result: dict[str, object] = {}
        final_layers = tuple(layers)
        for layer in final_layers:
            if not isinstance(layer, ConfigLayer):
                raise TypeError("All 'layers' elements must be of type 'ConfigLayer'")
            if layer.name in temp_layers:
                raise ValueError(f'Layer names must be unique: {layer.name} occurs more than once')
            temp_layers.add(layer.name)
            for key, value in layer.values.items():
                result[key] = value
        object.__setattr__(self, 'data', MappingProxyType(result))
        object.__setattr__(self, 'layers', final_layers)

    def __getitem__(self, key: str) -> object:
        return self.data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __or__(self, other: 'GameConfig') -> 'GameConfig | NotImplementedType':
        if not isinstance(other, GameConfig):
            return NotImplemented
        return self._merge_internal(other)

    def added_keys(self, other: 'GameConfig') -> frozenset[str]:
        if not isinstance(other, GameConfig):
            raise TypeError("The parameter 'other' must have a type 'GameConfig'")
        return frozenset(other.keys() - self.keys())

    def removed_keys(self, other: 'GameConfig') -> frozenset[str]:
        if not isinstance(other, GameConfig):
            raise TypeError("The parameter 'other' must have a type 'GameConfig'")
        return frozenset(self.keys() - other.keys())

    def changed_keys(self, other: 'GameConfig') -> frozenset[str]:
        if not isinstance(other, GameConfig):
            raise TypeError("The parameter 'other' must have a type 'GameConfig'")
        shared_keys = self.keys() & other.keys()
        return frozenset(key for key in shared_keys if self[key] != other[key])

    def unchanged_keys(self, other: 'GameConfig') -> frozenset[str]:
        if not isinstance(other, GameConfig):
            raise TypeError("The parameter 'other' must have a type 'GameConfig'")
        shared_keys = self.keys() & other.keys()
        return frozenset(key for key in shared_keys if self[key] == other[key])

    def layer_names(self) -> tuple[str, ...]:
        return tuple(layer.name for layer in self.layers)

    def get_layer(self, name: str) -> ConfigLayer:
        if not isinstance(name, str):
            raise TypeError("The parameter 'name' must have a type 'str'")
        index = self._get_layer_index_by_name(name)
        if index is None:
            raise KeyError(f'Layer named {name} does not exist.')
        return self.layers[index]

    def with_overrides(self, name: str, values: Mapping[str, object]) -> 'GameConfig':
        layer = ConfigLayer(name, values)
        return GameConfig(self.layers + (layer, ))

    def merge(self, other: 'GameConfig') -> 'GameConfig':
        if not isinstance(other, GameConfig):
            raise TypeError("The parameter 'other' must have a type 'GameConfig'")
        return self._merge_internal(other)

    def without_layer(self, layer_name: str) -> 'GameConfig':
        if not isinstance(layer_name, str):
            raise TypeError("The parameter 'layer_name' must have a type 'str'")
        index = self._get_layer_index_by_name(layer_name)
        if index is None:
            raise KeyError(f'Layer named {layer_name} does not exist.')
        return GameConfig(self.layers[:index] + self.layers[index + 1:])

    def replace_layer(self, layer_name: str, values: Mapping[str, object]) -> 'GameConfig':
        if not isinstance(layer_name, str):
            raise TypeError("The parameter 'layer_name' must have a type 'str'")
        index = self._get_layer_index_by_name(layer_name)
        if index is None:
            raise KeyError(f'Layer named {layer_name} does not exist.')
        replacement_layer = ConfigLayer(layer_name, values)
        return GameConfig(
            self.layers[:index] 
            + (replacement_layer,) 
            + self.layers[index + 1:]
        )

    def source_of(self, key: str) -> str:
        if not isinstance(key, str):
            raise TypeError("The parameter 'key' must have a type 'str'")
        result = next((layer.name for layer in reversed(self.layers) if key in layer.values), None)
        if result is None:
            raise KeyError(f'Key named {key} does not exist.')
        return result

    def diff(self, other: 'GameConfig') -> ConfigDiff:
        return ConfigDiff(
            added=self.added_keys(other),
            removed=self.removed_keys(other),
            changed=self.changed_keys(other),
            unchanged=self.unchanged_keys(other)
        )
    
    def _merge_internal(self, other: 'GameConfig') -> 'GameConfig':
        return GameConfig(self.layers + other.layers)

    def _get_layer_index_by_name(self, layer_name: str) -> int | None:
        return next(
            (
                index for index, layer in enumerate(self.layers)
                if layer.name == layer_name
            ), 
            None,
        )

    