import collections
import itertools
from typing import Self, NewType
from collections.abc import Iterator

Entity = NewType("Entity", int)


class EntityManager:
    def __init__(self: Self) -> None:
        self._entity_counter: itertools.count[Entity] = itertools.count()
        self._components: dict[type, dict[Entity, object]] = collections.defaultdict(
            dict
        )

    def spawn_entity(self: Self) -> Entity:
        return Entity(next(self._entity_counter))

    def insert_component(self: Self, entity: Entity, component: object) -> None:
        self._components[type(component)][entity] = component

    def insert_components(self: Self, entity: Entity, *components: object) -> None:
        for component in components:
            self._components[type(component)][entity] = component

    def query_component(self: Self, component_type: type) -> Iterator[object]:
        for value in self._components[component_type].values():
            yield value

    def query_components(self: Self, *component_types: type) -> Iterator[object]:
        entity_sets: list[set[Entity]] = [
            set(self._components[component_type]) for component_type in component_types
        ]
        shared_entities: set[Entity] = set[Entity].intersection(*entity_sets)
        for entity in shared_entities:
            yield tuple(
                self._components[component_type][entity]
                for component_type in component_types
            )
