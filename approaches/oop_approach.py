"""
Approach 1: Traditional Object-Oriented Programming
====================================================
This is the "classic" game architecture using inheritance hierarchies.
Included for comparison to demonstrate ECS benefits.

PROBLEMS WITH THIS APPROACH:
1. Diamond inheritance problem
2. God objects (entities become bloated)
3. Tight coupling between behavior and data
4. Difficult to add new behaviors without modifying classes
5. Hard to optimize - data scattered in memory
"""
import math
import random
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod


class GameObject(ABC):
    """Base class for all game objects - the root of our hierarchy."""
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
        self.alive = True
    
    @abstractmethod
    def update(self, dt: float):
        pass
    
    @abstractmethod
    def render(self, surface) -> dict:
        """Return render info for comparison (no pygame dependency)."""
        pass


class MovableObject(GameObject):
    """Adds movement capability."""
    
    def __init__(self, x: float = 0, y: float = 0, dx: float = 0, dy: float = 0):
        super().__init__(x, y)
        self.dx = dx
        self.dy = dy
    
    def update(self, dt: float):
        self.x += self.dx * dt
        self.y += self.dy * dt


class CollidableObject(GameObject):
    """Adds collision detection."""
    
    def __init__(self, x: float = 0, y: float = 0, radius: float = 5):
        super().__init__(x, y)
        self.radius = radius
    
    def collides_with(self, other: 'CollidableObject') -> bool:
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (self.radius + other.radius)


# Here's where OOP gets messy - we need both movement AND collision
class MovableCollidable(MovableObject, CollidableObject):
    """Diamond inheritance! Both parents inherit from GameObject."""
    
    def __init__(self, x: float = 0, y: float = 0, dx: float = 0, dy: float = 0, radius: float = 5):
        # MRO complexity begins...
        super().__init__(x, y, dx, dy)
        self.radius = radius


class HealthMixin:
    """Mixin for health - but mixins have their own problems."""
    
    def __init__(self):
        self.health = 100
        self.max_health = 100
    
    def take_damage(self, amount: int):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.alive = False
    
    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)


class RenderMixin:
    """Mixin for rendering."""
    
    def __init__(self):
        self.color = (255, 255, 255)
        self.size = 5
        self.shape = "circle"


# Now our actual game entities become complex multi-inheritance classes

class Player(MovableCollidable, HealthMixin, RenderMixin):
    """Player class - note the inheritance complexity."""
    
    def __init__(self, x: float = 400, y: float = 300):
        MovableCollidable.__init__(self, x, y, 0, 0, 10)
        HealthMixin.__init__(self)
        RenderMixin.__init__(self)
        self.score = 0
        self.color = (0, 255, 0)
        self.speed = 200
    
    def update(self, dt: float):
        super().update(dt)
        # Boundary checking
        self.x = max(0, min(800, self.x))
        self.y = max(0, min(600, self.y))
    
    def render(self, surface) -> dict:
        return {"type": "circle", "x": self.x, "y": self.y, 
                "color": self.color, "radius": self.size}
    
    def handle_input(self, keys: dict):
        self.dx = 0
        self.dy = 0
        if keys.get('left'):
            self.dx = -self.speed
        if keys.get('right'):
            self.dx = self.speed
        if keys.get('up'):
            self.dy = -self.speed
        if keys.get('down'):
            self.dy = self.speed


class Enemy(MovableCollidable, HealthMixin, RenderMixin):
    """Enemy class - lots of duplicated structure from Player."""
    
    def __init__(self, x: float = 0, y: float = 0):
        MovableCollidable.__init__(self, x, y, 0, 0, 8)
        HealthMixin.__init__(self)
        RenderMixin.__init__(self)
        self.health = 50
        self.max_health = 50
        self.color = (255, 0, 0)
        self.damage = 10
        self.points = 10
        self.behavior = "wander"
        self.target_x = x
        self.target_y = y
        self.decision_timer = 0
    
    def update(self, dt: float):
        # AI behavior is embedded in the class
        self.decision_timer -= dt
        if self.decision_timer <= 0:
            self.target_x = random.uniform(50, 750)
            self.target_y = random.uniform(50, 550)
            self.decision_timer = random.uniform(1, 3)
        
        # Move toward target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 5:
            speed = 80
            self.dx = (dx / distance) * speed
            self.dy = (dy / distance) * speed
        else:
            self.dx = 0
            self.dy = 0
        
        super().update(dt)
    
    def render(self, surface) -> dict:
        return {"type": "circle", "x": self.x, "y": self.y,
                "color": self.color, "radius": self.size}


class Bullet(MovableCollidable, RenderMixin):
    """Projectile - doesn't need health but still complex inheritance."""
    
    def __init__(self, x: float, y: float, dx: float, dy: float, owner: GameObject):
        MovableCollidable.__init__(self, x, y, dx, dy, 3)
        RenderMixin.__init__(self)
        self.owner = owner
        self.damage = 25
        self.lifetime = 2.0
        self.color = (255, 255, 0)
        self.size = 3
    
    def update(self, dt: float):
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
    
    def render(self, surface) -> dict:
        return {"type": "circle", "x": self.x, "y": self.y,
                "color": self.color, "radius": self.size}


# What if we want a new entity type? We need to figure out the inheritance!
# What if an enemy can become friendly? We'd need to change its class!
# What if we want an invincible enemy? Lots of special cases!


class OOPWorld:
    """
    Game world manager for OOP approach.
    
    Note how the world needs to know about specific entity types
    and handle them differently. This breaks the Open/Closed principle.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.all_objects: List[GameObject] = []
    
    def spawn_player(self):
        self.player = Player(self.width / 2, self.height / 2)
        self.all_objects.append(self.player)
    
    def spawn_enemy(self):
        x = random.uniform(50, self.width - 50)
        y = random.uniform(50, self.height - 50)
        enemy = Enemy(x, y)
        self.enemies.append(enemy)
        self.all_objects.append(enemy)
    
    def spawn_bullet(self, x: float, y: float, target_x: float, target_y: float):
        if self.player:
            dx = target_x - x
            dy = target_y - y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                speed = 400
                bullet = Bullet(x, y, (dx/dist) * speed, (dy/dist) * speed, self.player)
                self.bullets.append(bullet)
                self.all_objects.append(bullet)
    
    def update(self, dt: float, keys: dict):
        # Update player with input
        if self.player and self.player.alive:
            self.player.handle_input(keys)
            self.player.update(dt)
        
        # Update enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(dt)
        
        # Update bullets
        for bullet in self.bullets:
            if bullet.alive:
                bullet.update(dt)
        
        # Check collisions - O(n*m) nested loops, type-specific logic
        self._check_collisions()
        
        # Remove dead objects - lots of list filtering
        self._cleanup()
    
    def _check_collisions(self):
        # Bullet vs Enemy
        for bullet in self.bullets:
            if not bullet.alive:
                continue
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                if bullet.collides_with(enemy):
                    enemy.take_damage(bullet.damage)
                    bullet.alive = False
                    if not enemy.alive and self.player:
                        self.player.score += enemy.points
        
        # Enemy vs Player
        if self.player and self.player.alive:
            for enemy in self.enemies:
                if enemy.alive and self.player.collides_with(enemy):
                    self.player.take_damage(enemy.damage)
    
    def _cleanup(self):
        self.enemies = [e for e in self.enemies if e.alive]
        self.bullets = [b for b in self.bullets if b.alive]
        self.all_objects = [o for o in self.all_objects if o.alive]
    
    def get_render_data(self) -> List[dict]:
        """Get all render data for visualization."""
        return [obj.render(None) for obj in self.all_objects if obj.alive]
    
    def get_stats(self) -> dict:
        return {
            "player_health": self.player.health if self.player else 0,
            "player_score": self.player.score if self.player else 0,
            "enemy_count": len([e for e in self.enemies if e.alive]),
            "bullet_count": len([b for b in self.bullets if b.alive]),
            "total_entities": len([o for o in self.all_objects if o.alive])
        }


def run_benchmark(num_entities: int = 1000, num_frames: int = 100) -> dict:
    """Run a performance benchmark for the OOP approach."""
    import time
    
    world = OOPWorld()
    world.spawn_player()
    
    # Spawn many enemies
    for _ in range(num_entities):
        world.spawn_enemy()
    
    # Simulate frames
    start = time.perf_counter()
    for frame in range(num_frames):
        dt = 1/60  # 60 FPS
        keys = {}  # No input for benchmark
        world.update(dt, keys)
    
    elapsed = time.perf_counter() - start
    
    return {
        "approach": "OOP",
        "entities": num_entities,
        "frames": num_frames,
        "total_time": elapsed,
        "avg_frame_time": elapsed / num_frames,
        "fps": num_frames / elapsed
    }


if __name__ == "__main__":
    # Quick demo
    world = OOPWorld()
    world.spawn_player()
    for _ in range(5):
        world.spawn_enemy()
    
    for _ in range(60):  # 1 second at 60fps
        world.update(1/60, {})
    
    print("OOP Demo Stats:", world.get_stats())
    print("Benchmark:", run_benchmark(100, 100))
