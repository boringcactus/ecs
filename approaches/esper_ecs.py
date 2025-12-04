"""
Approach 3: Esper Library ECS
=============================
Using the esper library - a popular, performance-focused Python ECS.

BENEFITS:
1. Optimized component queries with caching
2. Clean, Pythonic API
3. Supports dataclasses natively
4. Well-tested and maintained
5. Minimal boilerplate

KEY CONCEPTS:
- Components are just data classes
- Processors (Systems) define logic
- World manages everything (but in esper 3.0, module-level functions)
"""
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple
import esper


# =============================================================================
# COMPONENT DEFINITIONS
# =============================================================================
# Esper works great with dataclasses

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
# PROCESSORS (SYSTEMS)
# =============================================================================
# Esper calls systems "Processors"

class MovementProcessor(esper.Processor):
    """Updates positions based on velocities."""
    
    def __init__(self, bounds: Tuple[int, int] = (800, 600)):
        self.bounds = bounds
    
    def process(self, dt: float):
        # esper.get_components returns iterator of (entity, (comp1, comp2, ...))
        for ent, (pos, vel) in esper.get_components(Position, Velocity):
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt
            
            # Clamp player to bounds
            if esper.has_component(ent, PlayerTag):
                pos.x = max(0, min(self.bounds[0], pos.x))
                pos.y = max(0, min(self.bounds[1], pos.y))


class AIProcessor(esper.Processor):
    """Updates AI behaviors."""
    
    def process(self, dt: float):
        for ent, (pos, vel, ai) in esper.get_components(Position, Velocity, AI):
            ai.decision_timer -= dt
            
            if ai.decision_timer <= 0:
                ai.target_x = random.uniform(50, 750)
                ai.target_y = random.uniform(50, 550)
                ai.decision_timer = random.uniform(1, 3)
            
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


class LifetimeProcessor(esper.Processor):
    """Destroys entities whose lifetime has expired."""
    
    def process(self, dt: float):
        to_destroy = []
        
        for ent, (lifetime,) in esper.get_components(Lifetime):
            lifetime.remaining -= dt
            if lifetime.remaining <= 0:
                to_destroy.append(ent)
        
        for ent in to_destroy:
            esper.delete_entity(ent)


class CollisionProcessor(esper.Processor):
    """Handles collision detection and response."""
    
    def process(self, dt: float):
        to_destroy = []
        
        # Get grouped entities
        projectiles = list(esper.get_components(Position, Collider, ProjectileTag))
        enemies = list(esper.get_components(Position, Collider, EnemyTag, Health))
        players = list(esper.get_components(Position, Collider, PlayerTag, Health))
        
        # Projectile vs Enemy
        for proj_ent, (proj_pos, proj_col, proj_tag) in projectiles:
            if proj_ent in to_destroy:
                continue
                
            for enemy_ent, (enemy_pos, enemy_col, enemy_tag, enemy_health) in enemies:
                if enemy_ent in to_destroy:
                    continue
                
                if self._check_collision(proj_pos, proj_col, enemy_pos, enemy_col):
                    enemy_health.current -= proj_tag.damage
                    to_destroy.append(proj_ent)
                    
                    if enemy_health.current <= 0:
                        # Award points
                        for player_ent, (_, _, player_tag, _) in players:
                            player_tag.score += enemy_tag.points
                        to_destroy.append(enemy_ent)
                    break
        
        # Enemy vs Player
        for player_ent, (player_pos, player_col, player_tag, player_health) in players:
            for enemy_ent, (enemy_pos, enemy_col, enemy_tag, _) in enemies:
                if enemy_ent in to_destroy:
                    continue
                
                if self._check_collision(player_pos, player_col, enemy_pos, enemy_col):
                    player_health.current -= enemy_tag.damage
        
        for ent in set(to_destroy):
            if esper.entity_exists(ent):
                esper.delete_entity(ent)
    
    def _check_collision(self, pos1: Position, col1: Collider,
                         pos2: Position, col2: Collider) -> bool:
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (col1.radius + col2.radius)


# =============================================================================
# WORLD FACADE
# =============================================================================

class EsperWorld:
    """
    Facade that wraps esper's module-level functions.
    Provides convenient methods for game setup.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.player_id: Optional[int] = None
        
        # Clear any existing state (esper uses module-level state)
        esper.clear_database()
        
        # Clear processors manually (remove each by type if exists)
        for proc_type in [AIProcessor, MovementProcessor, CollisionProcessor, LifetimeProcessor]:
            try:
                esper.remove_processor(proc_type)
            except KeyError:
                pass
        
        # Add processors in order
        esper.add_processor(AIProcessor())
        esper.add_processor(MovementProcessor((width, height)))
        esper.add_processor(CollisionProcessor())
        esper.add_processor(LifetimeProcessor())
    
    def spawn_player(self) -> int:
        entity = esper.create_entity(
            Position(self.width / 2, self.height / 2),
            Velocity(),
            Renderable(color=(0, 255, 0), size=10),
            Health(100, 100),
            Collider(10),
            PlayerTag()
        )
        self.player_id = entity
        return entity
    
    def spawn_enemy(self) -> int:
        x = random.uniform(50, self.width - 50)
        y = random.uniform(50, self.height - 50)
        return esper.create_entity(
            Position(x, y),
            Velocity(),
            Renderable(color=(255, 0, 0), size=8),
            Health(50, 50),
            Collider(8),
            EnemyTag(),
            AI()
        )
    
    def spawn_projectile(self, x: float, y: float, target_x: float, target_y: float) -> int:
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
        
        return esper.create_entity(
            Position(x, y),
            Velocity(vel_x, vel_y),
            Renderable(color=(255, 255, 0), size=3),
            Collider(3),
            ProjectileTag(owner_id=self.player_id or -1),
            Lifetime(2.0)
        )
    
    def handle_input(self, keys: dict):
        if self.player_id is None or not esper.entity_exists(self.player_id):
            return
        
        vel = esper.component_for_entity(self.player_id, Velocity)
        player_tag = esper.component_for_entity(self.player_id, PlayerTag)
        
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
        self.handle_input(keys)
        esper.process(dt)
    
    def get_render_data(self) -> List[dict]:
        render_data = []
        
        for ent, (pos, rend) in esper.get_components(Position, Renderable):
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
        
        if self.player_id and esper.entity_exists(self.player_id):
            health = esper.component_for_entity(self.player_id, Health)
            player_tag = esper.component_for_entity(self.player_id, PlayerTag)
            player_health = health.current
            player_score = player_tag.score
        
        enemy_count = len(list(esper.get_components(EnemyTag)))
        bullet_count = len(list(esper.get_components(ProjectileTag)))
        
        return {
            "player_health": player_health,
            "player_score": player_score,
            "enemy_count": enemy_count,
            "bullet_count": bullet_count,
            "total_entities": len(list(esper.get_components(Position)))
        }


def run_benchmark(num_entities: int = 1000, num_frames: int = 100) -> dict:
    """Run a performance benchmark for the Esper ECS approach."""
    import time
    
    world = EsperWorld()
    world.spawn_player()
    
    for _ in range(num_entities):
        world.spawn_enemy()
    
    start = time.perf_counter()
    for _ in range(num_frames):
        world.update(1/60, {})
    elapsed = time.perf_counter() - start
    
    return {
        "approach": "Esper ECS",
        "entities": num_entities,
        "frames": num_frames,
        "total_time": elapsed,
        "avg_frame_time": elapsed / num_frames,
        "fps": num_frames / elapsed
    }


if __name__ == "__main__":
    world = EsperWorld()
    world.spawn_player()
    for _ in range(5):
        world.spawn_enemy()
    
    for _ in range(60):
        world.update(1/60, {})
    
    print("Esper ECS Demo Stats:", world.get_stats())
    print("Benchmark:", run_benchmark(100, 100))
