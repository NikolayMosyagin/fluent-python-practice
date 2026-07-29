from collections.abc import Mapping, Iterable
from types import MappingProxyType
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfigLayer:
    name: str
    values: Mapping[str, object]

    def __post_init__(self):
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
class GameConfig(Mapping[str, object]):
    data: MappingProxyType[str, object]
    layers: tuple[ConfigLayer, ...]

    def __init__(self, layers: Iterable[ConfigLayer] | None = None):
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

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __or__(self, other: 'GameConfig') -> 'GameConfig':
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
        result = next((layer for layer in self.layers if layer.name == name), None)
        if result is None:
            raise KeyError(f'Layer named {name} does not exist.')
        return result

    def with_overrides(self, name: str, values: Mapping[str, object]) -> 'GameConfig':
        layer = ConfigLayer(name, values)
        return GameConfig(self.layers + (layer, ))

    def merge(self, other: 'GameConfig') -> 'GameConfig':
        if not isinstance(other, GameConfig):
            raise TypeError("The parameter 'other' must have a type 'GameConfig'")
        return self._merge_internal(other)
    
    def _merge_internal(self, other: 'GameConfig') -> 'GameConfig':
        return GameConfig(self.layers + other.layers)