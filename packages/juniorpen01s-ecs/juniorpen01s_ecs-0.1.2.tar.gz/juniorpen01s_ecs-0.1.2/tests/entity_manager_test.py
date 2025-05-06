from typing import Self
from unittest import TestCase

from juniorpen01s_ecs import Entity, EntityManager

from tests.position import Position
from tests.velocity import Velocity


class EntityManagerTest(TestCase):
    def setUp(self: Self) -> None:
        self.entity_manager = EntityManager()

    def test_entity_manager_insert_component(self: Self) -> None:
        entity: Entity = self.entity_manager.spawn_entity()
        self.entity_manager.insert_component(entity, Position(8, 14))

    def test_entity_manager_query_component_none(self: Self) -> None:
        self.entity_manager.spawn_entity()
        self.assertEqual(list(self.entity_manager.query_component(Position)), [])

    def test_entity_manager_query_component(self: Self) -> None:
        entity: Entity = self.entity_manager.spawn_entity()
        self.entity_manager.insert_component(entity, Position(8, 14))
        self.assertNotEqual(list(self.entity_manager.query_component(Position)), [])

    def test_entity_manager_query_components_none(self: Self) -> None:
        entity: Entity = self.entity_manager.spawn_entity()
        self.entity_manager.insert_component(entity, Position(8, 14))
        self.assertEqual(
            list(self.entity_manager.query_components(Position, Velocity)), []
        )

    def test_entity_manager_query_components(self: Self) -> None:
        entity: Entity = self.entity_manager.spawn_entity()
        self.entity_manager.insert_components(entity, Position(8, 14), Velocity(2, 5))
        self.assertNotEqual(
            list(self.entity_manager.query_components(Position, Velocity)), []
        )
