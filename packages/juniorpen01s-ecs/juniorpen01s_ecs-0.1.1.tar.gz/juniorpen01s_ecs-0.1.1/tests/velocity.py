from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T", int, float, complex)


@dataclass
class Velocity(Generic[T]):
    x: T
    y: T
