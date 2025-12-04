"""
Shared component definitions used across all ECS approaches.
Components are pure data containers - no logic, just state.
"""
from dataclasses import dataclass, field
from typing import Tuple
import random


@dataclass
class Position:
    """2D position in world space."""
    x: float = 0.0
    y: float = 0.0


@dataclass
class Velocity:
    """Movement vector."""
    dx: float = 0.0
    dy: float = 0.0


@dataclass
class Renderable:
    """Visual representation."""
    color: Tuple[int, int, int] = (255, 255, 255)
    size: int = 5
    shape: str = "circle"  # circle, square, triangle


@dataclass
class Health:
    """Entity health/hitpoints."""
    current: int = 100
    maximum: int = 100
    
    @property
    def is_alive(self) -> bool:
        return self.current > 0
    
    @property
    def percentage(self) -> float:
        return self.current / self.maximum


@dataclass
class Collider:
    """Collision detection bounds."""
    radius: float = 5.0


@dataclass 
class AI:
    """Simple AI behavior state."""
    behavior: str = "wander"  # wander, chase, flee
    target_x: float = 0.0
    target_y: float = 0.0
    decision_timer: float = 0.0


@dataclass
class Player:
    """Tag component marking player-controlled entities."""
    score: int = 0


@dataclass
class Enemy:
    """Tag component for enemy entities."""
    damage: int = 10
    points: int = 10


@dataclass
class Projectile:
    """Tag for projectile entities."""
    damage: int = 25
    owner_id: int = -1
    lifetime: float = 2.0


@dataclass
class Lifetime:
    """Entity expires after duration."""
    remaining: float = 5.0


@dataclass
class ParticleEmitter:
    """Spawns particle effects."""
    rate: float = 10.0  # particles per second
    timer: float = 0.0
    particle_lifetime: float = 1.0
    particle_color: Tuple[int, int, int] = (255, 200, 100)


# Factory functions for creating common entity configurations
def create_random_velocity(speed: float = 100.0) -> Velocity:
    """Create a velocity with random direction."""
    import math
    angle = random.uniform(0, 2 * math.pi)
    return Velocity(
        dx=math.cos(angle) * speed,
        dy=math.sin(angle) * speed
    )


def create_random_color() -> Tuple[int, int, int]:
    """Generate a random bright color."""
    return (
        random.randint(100, 255),
        random.randint(100, 255),
        random.randint(100, 255)
    )
