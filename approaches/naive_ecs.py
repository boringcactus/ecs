"""
Approach 2: Naive/Manual ECS Implementation
============================================
A basic ECS built from scratch to understand the core concepts.

BENEFITS:
1. Clean separation of data (components) and logic (systems)
2. Entities are just IDs - composition over inheritance
3. Systems process batches of similar components
4. Easy to add new behaviors without modifying existing code

LIMITATIONS OF THIS NAIVE APPROACH:
1. No query optimization (scans all entities)
2. No archetype caching
3. Simple dict storage (not cache-friendly)
"""
import math
import random
from typing import Dict, Set, Type, Any, List, Optional, Iterator, Tuple
from dataclasses import dataclass, field


# =============================================================================
# COMPONENT DEFINITIONS
# =============================================================================
# Components are pure data - no methods beyond simple property access

@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0

@dataclass
class Velocity:
    dx: float = 0.0
    dy: float = 0.0

@dataclass
class Renderable:
    color: Tuple[int, int, int] = (255, 255, 255)
    size: int = 5
    shape: str = "circle"

@dataclass
class Health:
    current: int = 100
    maximum: int = 100

@dataclass
class Collider:
    radius: float = 5.0

@dataclass
class AI:
    behavior: str = "wander"
    target_x: float = 0.0
    target_y: float = 0.0
    decision_timer: float = 0.0

@dataclass
class PlayerTag:
    score: int = 0
    speed: float = 200.0

@dataclass
class EnemyTag:
    damage: int = 10
    points: int = 10

@dataclass
class ProjectileTag:
    damage: int = 25
    owner_id: int = -1

@dataclass
class Lifetime:
    remaining: float = 2.0


# =============================================================================
# ENTITY MANAGER
# =============================================================================

class EntityManager:
    """
    Manages entities and their components.
    Entities are just integer IDs. Components are stored in dictionaries.
    """
    
    def __init__(self):
        self._next_entity_id = 0
        self._entities: Set[int] = set()
        # Component storage: component_type -> {entity_id -> component_instance}
        self._components: Dict[Type, Dict[int, Any]] = {}
    
    def create_entity(self) -> int:
        """Create a new entity and return its ID."""
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        self._entities.add(entity_id)
        return entity_id
    
    def destroy_entity(self, entity_id: int):
        """Remove an entity and all its components."""
        if entity_id in self._entities:
            self._entities.remove(entity_id)
            # Remove all components for this entity
            for component_store in self._components.values():
                component_store.pop(entity_id, None)
    
    def add_component(self, entity_id: int, component: Any):
        """Add a component to an entity."""
        component_type = type(component)
        if component_type not in self._components:
            self._components[component_type] = {}
        self._components[component_type][entity_id] = component
    
    def get_component(self, entity_id: int, component_type: Type) -> Optional[Any]:
        """Get a component from an entity."""
        if component_type in self._components:
            return self._components[component_type].get(entity_id)
        return None
    
    def has_component(self, entity_id: int, component_type: Type) -> bool:
        """Check if entity has a component type."""
        return (component_type in self._components and 
                entity_id in self._components[component_type])
    
    def remove_component(self, entity_id: int, component_type: Type):
        """Remove a component from an entity."""
        if component_type in self._components:
            self._components[component_type].pop(entity_id, None)
    
    def get_entities_with(self, *component_types: Type) -> Iterator[int]:
        """Get all entities that have ALL specified component types."""
        if not component_types:
            return
        
        # Find the smallest component store to start with (optimization)
        stores = [self._components.get(ct, {}) for ct in component_types]
        if not all(stores):
            return
        
        # Start with entities from smallest store
        smallest_store = min(stores, key=len)
        
        for entity_id in smallest_store:
            if all(entity_id in store for store in stores):
                yield entity_id
    
    def get_all_entities(self) -> Set[int]:
        """Get all active entity IDs."""
        return self._entities.copy()
    
    def entity_count(self) -> int:
        return len(self._entities)


# =============================================================================
# SYSTEM BASE CLASS
# =============================================================================

class System:
    """Base class for systems. Systems contain logic that operates on components."""
    
    def __init__(self, entity_manager: EntityManager):
        self.em = entity_manager
    
    def update(self, dt: float):
        """Override this to implement system logic."""
        raise NotImplementedError


# =============================================================================
# CONCRETE SYSTEMS
# =============================================================================

class MovementSystem(System):
    """Updates positions based on velocities."""
    
    def __init__(self, em: EntityManager, bounds: Tuple[int, int] = (800, 600)):
        super().__init__(em)
        self.bounds = bounds
    
    def update(self, dt: float):
        for entity_id in self.em.get_entities_with(Position, Velocity):
            pos = self.em.get_component(entity_id, Position)
            vel = self.em.get_component(entity_id, Velocity)
            
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt
            
            # Optional: Boundary wrapping/clamping
            if self.em.has_component(entity_id, PlayerTag):
                pos.x = max(0, min(self.bounds[0], pos.x))
                pos.y = max(0, min(self.bounds[1], pos.y))


class AISystem(System):
    """Updates AI behaviors."""
    
    def update(self, dt: float):
        for entity_id in self.em.get_entities_with(Position, Velocity, AI):
            pos = self.em.get_component(entity_id, Position)
            vel = self.em.get_component(entity_id, Velocity)
            ai = self.em.get_component(entity_id, AI)
            
            ai.decision_timer -= dt
            
            if ai.decision_timer <= 0:
                # Pick new random target
                ai.target_x = random.uniform(50, 750)
                ai.target_y = random.uniform(50, 550)
                ai.decision_timer = random.uniform(1, 3)
            
            # Move toward target
            dx = ai.target_x - pos.x
            dy = ai.target_y - pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 5:
                speed = 80
                vel.dx = (dx / distance) * speed
                vel.dy = (dy / distance) * speed
            else:
                vel.dx = 0
                vel.dy = 0


class LifetimeSystem(System):
    """Destroys entities whose lifetime has expired."""
    
    def __init__(self, em: EntityManager):
        super().__init__(em)
        self._to_destroy: List[int] = []
    
    def update(self, dt: float):
        self._to_destroy.clear()
        
        for entity_id in self.em.get_entities_with(Lifetime):
            lifetime = self.em.get_component(entity_id, Lifetime)
            lifetime.remaining -= dt
            
            if lifetime.remaining <= 0:
                self._to_destroy.append(entity_id)
        
        for entity_id in self._to_destroy:
            self.em.destroy_entity(entity_id)


class CollisionSystem(System):
    """Handles collision detection and response."""
    
    def __init__(self, em: EntityManager):
        super().__init__(em)
        self._to_destroy: List[int] = []
    
    def update(self, dt: float):
        self._to_destroy.clear()
        
        # Get all collidable entities grouped by type
        projectiles = list(self.em.get_entities_with(Position, Collider, ProjectileTag))
        enemies = list(self.em.get_entities_with(Position, Collider, EnemyTag, Health))
        players = list(self.em.get_entities_with(Position, Collider, PlayerTag, Health))
        
        # Projectile vs Enemy
        for proj_id in projectiles:
            if proj_id in self._to_destroy:
                continue
            proj_pos = self.em.get_component(proj_id, Position)
            proj_col = self.em.get_component(proj_id, Collider)
            proj_tag = self.em.get_component(proj_id, ProjectileTag)
            
            for enemy_id in enemies:
                if enemy_id in self._to_destroy:
                    continue
                enemy_pos = self.em.get_component(enemy_id, Position)
                enemy_col = self.em.get_component(enemy_id, Collider)
                
                if self._check_collision(proj_pos, proj_col, enemy_pos, enemy_col):
                    # Damage enemy
                    enemy_health = self.em.get_component(enemy_id, Health)
                    enemy_health.current -= proj_tag.damage
                    
                    # Destroy projectile
                    self._to_destroy.append(proj_id)
                    
                    # Check if enemy died
                    if enemy_health.current <= 0:
                        enemy_tag = self.em.get_component(enemy_id, EnemyTag)
                        # Award points to player
                        for player_id in players:
                            player_tag = self.em.get_component(player_id, PlayerTag)
                            player_tag.score += enemy_tag.points
                        self._to_destroy.append(enemy_id)
                    break
        
        # Enemy vs Player
        for player_id in players:
            player_pos = self.em.get_component(player_id, Position)
            player_col = self.em.get_component(player_id, Collider)
            player_health = self.em.get_component(player_id, Health)
            
            for enemy_id in enemies:
                if enemy_id in self._to_destroy:
                    continue
                enemy_pos = self.em.get_component(enemy_id, Position)
                enemy_col = self.em.get_component(enemy_id, Collider)
                enemy_tag = self.em.get_component(enemy_id, EnemyTag)
                
                if self._check_collision(player_pos, player_col, enemy_pos, enemy_col):
                    player_health.current -= enemy_tag.damage
        
        # Destroy marked entities
        for entity_id in self._to_destroy:
            self.em.destroy_entity(entity_id)
    
    def _check_collision(self, pos1: Position, col1: Collider, 
                         pos2: Position, col2: Collider) -> bool:
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (col1.radius + col2.radius)


# =============================================================================
# WORLD FACADE
# =============================================================================

class NaiveECSWorld:
    """
    Facade that manages the entity manager and systems.
    Provides convenient methods for spawning entities.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.em = EntityManager()
        self.player_id: Optional[int] = None
        
        # Create systems in order of execution
        self.systems: List[System] = [
            AISystem(self.em),
            MovementSystem(self.em, (width, height)),
            CollisionSystem(self.em),
            LifetimeSystem(self.em),
        ]
    
    def spawn_player(self) -> int:
        entity = self.em.create_entity()
        self.em.add_component(entity, Position(self.width / 2, self.height / 2))
        self.em.add_component(entity, Velocity())
        self.em.add_component(entity, Renderable(color=(0, 255, 0), size=10))
        self.em.add_component(entity, Health(100, 100))
        self.em.add_component(entity, Collider(10))
        self.em.add_component(entity, PlayerTag())
        self.player_id = entity
        return entity
    
    def spawn_enemy(self) -> int:
        entity = self.em.create_entity()
        x = random.uniform(50, self.width - 50)
        y = random.uniform(50, self.height - 50)
        self.em.add_component(entity, Position(x, y))
        self.em.add_component(entity, Velocity())
        self.em.add_component(entity, Renderable(color=(255, 0, 0), size=8))
        self.em.add_component(entity, Health(50, 50))
        self.em.add_component(entity, Collider(8))
        self.em.add_component(entity, EnemyTag())
        self.em.add_component(entity, AI())
        return entity
    
    def spawn_projectile(self, x: float, y: float, target_x: float, target_y: float) -> int:
        entity = self.em.create_entity()
        
        # Calculate direction
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
        
        self.em.add_component(entity, Position(x, y))
        self.em.add_component(entity, Velocity(vel_x, vel_y))
        self.em.add_component(entity, Renderable(color=(255, 255, 0), size=3))
        self.em.add_component(entity, Collider(3))
        self.em.add_component(entity, ProjectileTag(owner_id=self.player_id or -1))
        self.em.add_component(entity, Lifetime(2.0))
        return entity
    
    def handle_input(self, keys: dict):
        """Handle player input."""
        if self.player_id is None:
            return
        
        vel = self.em.get_component(self.player_id, Velocity)
        player_tag = self.em.get_component(self.player_id, PlayerTag)
        
        if vel and player_tag:
            vel.dx = 0
            vel.dy = 0
            speed = player_tag.speed
            
            if keys.get('left'):
                vel.dx = -speed
            if keys.get('right'):
                vel.dx = speed
            if keys.get('up'):
                vel.dy = -speed
            if keys.get('down'):
                vel.dy = speed
    
    def update(self, dt: float, keys: dict):
        """Update all systems."""
        self.handle_input(keys)
        
        for system in self.systems:
            system.update(dt)
    
    def get_render_data(self) -> List[dict]:
        """Get render data for all renderable entities."""
        render_data = []
        
        for entity_id in self.em.get_entities_with(Position, Renderable):
            pos = self.em.get_component(entity_id, Position)
            rend = self.em.get_component(entity_id, Renderable)
            
            render_data.append({
                "type": rend.shape,
                "x": pos.x,
                "y": pos.y,
                "color": rend.color,
                "radius": rend.size
            })
        
        return render_data
    
    def get_stats(self) -> dict:
        player_health = 0
        player_score = 0
        
        if self.player_id:
            health = self.em.get_component(self.player_id, Health)
            player_tag = self.em.get_component(self.player_id, PlayerTag)
            if health:
                player_health = health.current
            if player_tag:
                player_score = player_tag.score
        
        enemy_count = len(list(self.em.get_entities_with(EnemyTag)))
        bullet_count = len(list(self.em.get_entities_with(ProjectileTag)))
        
        return {
            "player_health": player_health,
            "player_score": player_score,
            "enemy_count": enemy_count,
            "bullet_count": bullet_count,
            "total_entities": self.em.entity_count()
        }


def run_benchmark(num_entities: int = 1000, num_frames: int = 100) -> dict:
    """Run a performance benchmark for the naive ECS approach."""
    import time
    
    world = NaiveECSWorld()
    world.spawn_player()
    
    for _ in range(num_entities):
        world.spawn_enemy()
    
    start = time.perf_counter()
    for _ in range(num_frames):
        world.update(1/60, {})
    elapsed = time.perf_counter() - start
    
    return {
        "approach": "Naive ECS",
        "entities": num_entities,
        "frames": num_frames,
        "total_time": elapsed,
        "avg_frame_time": elapsed / num_frames,
        "fps": num_frames / elapsed
    }


if __name__ == "__main__":
    world = NaiveECSWorld()
    world.spawn_player()
    for _ in range(5):
        world.spawn_enemy()
    
    for _ in range(60):
        world.update(1/60, {})
    
    print("Naive ECS Demo Stats:", world.get_stats())
    print("Benchmark:", run_benchmark(100, 100))
