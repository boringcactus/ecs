"""
Approach 4: ecs_pattern Library
===============================
Using ecs_pattern - focused on simplicity and Pythonic design.

KEY DIFFERENCES FROM ESPER:
1. Uses decorator-based component/entity definition
2. Entities are actual classes (with slots for performance)
3. Components are mixins on entities
4. SystemManager handles system lifecycle
5. More explicit about entity types

This approach is good for:
- Teams new to ECS who want clear structure
- Projects where entity "archetypes" are well-defined
- Situations where you want IDE autocompletion on entities
"""
import math
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod


# Since ecs_pattern may not be installed, let's create our own implementation
# that follows the same philosophy

def component(cls):
    """Decorator that marks a class as a component (uses dataclass internally)."""
    return dataclass(cls)


def entity(cls):
    """Decorator that marks a class as an entity (uses dataclass with slots)."""
    return dataclass(slots=True)(cls)


# =============================================================================
# COMPONENT DEFINITIONS (as mixins)
# =============================================================================

@component
class ComPosition:
    x: float = 0.0
    y: float = 0.0


@component
class ComVelocity:
    dx: float = 0.0
    dy: float = 0.0


@component
class ComRenderable:
    color: Tuple[int, int, int] = (255, 255, 255)
    size: int = 5
    shape: str = "circle"


@component
class ComHealth:
    current: int = 100
    maximum: int = 100


@component
class ComCollider:
    radius: float = 5.0


@component
class ComAI:
    behavior: str = "wander"
    target_x: float = 0.0
    target_y: float = 0.0
    decision_timer: float = 0.0


@component
class ComPlayer:
    score: int = 0
    speed: float = 200.0


@component
class ComEnemy:
    damage: int = 10
    points: int = 10


@component
class ComProjectile:
    damage: int = 25
    owner_id: int = -1


@component
class ComLifetime:
    remaining: float = 2.0


# =============================================================================
# ENTITY DEFINITIONS (composed from components)
# =============================================================================
# In ecs_pattern style, entities are classes that inherit from components

@entity
class Player(ComPosition, ComVelocity, ComRenderable, ComHealth, ComCollider, ComPlayer):
    """Player entity with all required components."""
    pass


@entity 
class Enemy(ComPosition, ComVelocity, ComRenderable, ComHealth, ComCollider, ComEnemy, ComAI):
    """Enemy entity with AI behavior."""
    pass


@entity
class Projectile(ComPosition, ComVelocity, ComRenderable, ComCollider, ComProjectile, ComLifetime):
    """Projectile entity with limited lifetime."""
    pass


# =============================================================================
# ENTITY MANAGER (ecs_pattern style)
# =============================================================================

class EntityManager:
    """
    Manages entity storage and queries.
    In ecs_pattern, you work with actual entity objects.
    """
    
    def __init__(self):
        self._entities: List[object] = []
        self._next_id = 0
        self._entity_ids: dict = {}  # entity id(obj) -> numeric id mapping
    
    def add(self, entity: object) -> int:
        """Register an entity and return its ID."""
        self._entities.append(entity)
        entity_id = self._next_id
        self._entity_ids[id(entity)] = entity_id
        self._next_id += 1
        return entity_id
    
    def remove(self, entity: object):
        """Remove an entity."""
        if entity in self._entities:
            self._entities.remove(entity)
        self._entity_ids.pop(id(entity), None)
    
    def get_id(self, entity: object) -> int:
        """Get the ID of an entity."""
        return self._entity_ids.get(id(entity), -1)
    
    def get_by_class(self, *entity_classes) -> List:
        """Get all entities of specified classes."""
        return [e for e in self._entities if isinstance(e, entity_classes)]
    
    def get_with_component(self, *component_types) -> List:
        """Get all entities that have all specified component types."""
        return [e for e in self._entities 
                if all(isinstance(e, ct) for ct in component_types)]
    
    def count(self) -> int:
        return len(self._entities)
    
    def clear(self):
        self._entities.clear()
        self._entity_ids.clear()


# =============================================================================
# SYSTEM DEFINITIONS
# =============================================================================

class System(ABC):
    """Base system class following ecs_pattern design."""
    
    def __init__(self, entities: EntityManager):
        self.entities = entities
    
    def start(self):
        """Called once before the main loop."""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """Called every frame."""
        pass
    
    def stop(self):
        """Called once after the main loop."""
        pass


class MovementSystem(System):
    def __init__(self, entities: EntityManager, bounds: Tuple[int, int] = (800, 600)):
        super().__init__(entities)
        self.bounds = bounds
    
    def update(self, dt: float):
        for entity in self.entities.get_with_component(ComPosition, ComVelocity):
            entity.x += entity.dx * dt
            entity.y += entity.dy * dt
            
            # Clamp player
            if isinstance(entity, Player):
                entity.x = max(0, min(self.bounds[0], entity.x))
                entity.y = max(0, min(self.bounds[1], entity.y))


class AISystem(System):
    def update(self, dt: float):
        for entity in self.entities.get_with_component(ComPosition, ComVelocity, ComAI):
            entity.decision_timer -= dt
            
            if entity.decision_timer <= 0:
                entity.target_x = random.uniform(50, 750)
                entity.target_y = random.uniform(50, 550)
                entity.decision_timer = random.uniform(1, 3)
            
            dx = entity.target_x - entity.x
            dy = entity.target_y - entity.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 5:
                speed = 80
                entity.dx = (dx / distance) * speed
                entity.dy = (dy / distance) * speed
            else:
                entity.dx = 0
                entity.dy = 0


class LifetimeSystem(System):
    def __init__(self, entities: EntityManager):
        super().__init__(entities)
        self._to_remove: List = []
    
    def update(self, dt: float):
        self._to_remove.clear()
        
        for entity in self.entities.get_with_component(ComLifetime):
            entity.remaining -= dt
            if entity.remaining <= 0:
                self._to_remove.append(entity)
        
        for entity in self._to_remove:
            self.entities.remove(entity)


class CollisionSystem(System):
    def __init__(self, entities: EntityManager):
        super().__init__(entities)
        self._to_remove: List = []
    
    def update(self, dt: float):
        self._to_remove.clear()
        
        projectiles = self.entities.get_by_class(Projectile)
        enemies = self.entities.get_by_class(Enemy)
        players = self.entities.get_by_class(Player)
        
        # Projectile vs Enemy
        for proj in projectiles:
            if proj in self._to_remove:
                continue
            
            for enemy in enemies:
                if enemy in self._to_remove:
                    continue
                
                if self._check_collision(proj, enemy):
                    enemy.current -= proj.damage
                    self._to_remove.append(proj)
                    
                    if enemy.current <= 0:
                        for player in players:
                            player.score += enemy.points
                        self._to_remove.append(enemy)
                    break
        
        # Enemy vs Player
        for player in players:
            for enemy in enemies:
                if enemy in self._to_remove:
                    continue
                if self._check_collision(player, enemy):
                    player.current -= enemy.damage
        
        for entity in self._to_remove:
            self.entities.remove(entity)
    
    def _check_collision(self, e1, e2) -> bool:
        dx = e1.x - e2.x
        dy = e1.y - e2.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (e1.radius + e2.radius)


# =============================================================================
# SYSTEM MANAGER
# =============================================================================

class SystemManager:
    """Manages system lifecycle and execution order."""
    
    def __init__(self):
        self._systems: List[System] = []
    
    def add(self, system: System):
        self._systems.append(system)
    
    def start_all(self):
        for system in self._systems:
            system.start()
    
    def update_all(self, dt: float):
        for system in self._systems:
            system.update(dt)
    
    def stop_all(self):
        for system in self._systems:
            system.stop()


# =============================================================================
# WORLD FACADE
# =============================================================================

class ECSPatternWorld:
    """
    Game world using ecs_pattern-style architecture.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.entities = EntityManager()
        self.systems = SystemManager()
        self.player: Optional[Player] = None
        
        # Set up systems
        self.systems.add(AISystem(self.entities))
        self.systems.add(MovementSystem(self.entities, (width, height)))
        self.systems.add(CollisionSystem(self.entities))
        self.systems.add(LifetimeSystem(self.entities))
        self.systems.start_all()
    
    def spawn_player(self) -> Player:
        player = Player(
            x=self.width / 2,
            y=self.height / 2,
            dx=0, dy=0,
            color=(0, 255, 0),
            size=10,
            shape="circle",
            current=100,
            maximum=100,
            radius=10,
            score=0,
            speed=200.0
        )
        self.entities.add(player)
        self.player = player
        return player
    
    def spawn_enemy(self) -> Enemy:
        x = random.uniform(50, self.width - 50)
        y = random.uniform(50, self.height - 50)
        
        enemy = Enemy(
            x=x, y=y,
            dx=0, dy=0,
            color=(255, 0, 0),
            size=8,
            shape="circle",
            current=50,
            maximum=50,
            radius=8,
            damage=10,
            points=10,
            behavior="wander",
            target_x=x,
            target_y=y,
            decision_timer=0
        )
        self.entities.add(enemy)
        return enemy
    
    def spawn_projectile(self, x: float, y: float, target_x: float, target_y: float) -> Projectile:
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        speed = 400
        
        if dist > 0:
            vel_x = (dx / dist) * speed
            vel_y = (dy / dist) * speed
        else:
            vel_x = speed
            vel_y = 0
        
        proj = Projectile(
            x=x, y=y,
            dx=vel_x, dy=vel_y,
            color=(255, 255, 0),
            size=3,
            shape="circle",
            radius=3,
            damage=25,
            owner_id=self.entities.get_id(self.player) if self.player else -1,
            remaining=2.0
        )
        self.entities.add(proj)
        return proj
    
    def handle_input(self, keys: dict):
        if self.player is None:
            return
        
        self.player.dx = 0
        self.player.dy = 0
        speed = self.player.speed
        
        if keys.get('left'):
            self.player.dx = -speed
        if keys.get('right'):
            self.player.dx = speed
        if keys.get('up'):
            self.player.dy = -speed
        if keys.get('down'):
            self.player.dy = speed
    
    def update(self, dt: float, keys: dict):
        self.handle_input(keys)
        self.systems.update_all(dt)
    
    def get_render_data(self) -> List[dict]:
        render_data = []
        
        for entity in self.entities.get_with_component(ComPosition, ComRenderable):
            render_data.append({
                "type": entity.shape,
                "x": entity.x,
                "y": entity.y,
                "color": entity.color,
                "radius": entity.size
            })
        
        return render_data
    
    def get_stats(self) -> dict:
        return {
            "player_health": self.player.current if self.player and self.player in self.entities._entities else 0,
            "player_score": self.player.score if self.player and self.player in self.entities._entities else 0,
            "enemy_count": len(self.entities.get_by_class(Enemy)),
            "bullet_count": len(self.entities.get_by_class(Projectile)),
            "total_entities": self.entities.count()
        }


def run_benchmark(num_entities: int = 1000, num_frames: int = 100) -> dict:
    """Run a performance benchmark for the ecs_pattern approach."""
    import time
    
    world = ECSPatternWorld()
    world.spawn_player()
    
    for _ in range(num_entities):
        world.spawn_enemy()
    
    start = time.perf_counter()
    for _ in range(num_frames):
        world.update(1/60, {})
    elapsed = time.perf_counter() - start
    
    return {
        "approach": "ECS Pattern",
        "entities": num_entities,
        "frames": num_frames,
        "total_time": elapsed,
        "avg_frame_time": elapsed / num_frames,
        "fps": num_frames / elapsed
    }


if __name__ == "__main__":
    world = ECSPatternWorld()
    world.spawn_player()
    for _ in range(5):
        world.spawn_enemy()
    
    for _ in range(60):
        world.update(1/60, {})
    
    print("ECS Pattern Demo Stats:", world.get_stats())
    print("Benchmark:", run_benchmark(100, 100))
