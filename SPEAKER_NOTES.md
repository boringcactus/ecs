# ECS Presentation - Speaker Notes & Exercises

## Timing Guide (30 minutes total)

| Time | Section | Key Points | Notes |
|------|---------|------------|-------|
| 0:00-1:00 | Introduction | Hook: "Have you ever had a Player class with 50 attributes?" | |
| 1:00-6:00 | Part 1: OOP Problems | Diamond problem, feature explosion | Live coding the diamond issue |
| 6:00-14:00 | Part 2: ECS Concepts | Entity, Component, System | Use diagrams heavily |
| 14:00-24:00 | Part 3: Implementations | Naive, Esper, Pattern | Code comparison side-by-side |
| 24:00-29:00 | Part 4: Demo | Run benchmarks live | Have backup results ready |
| 29:00-30:00 | Part 5: When to Use | Decision tree | Leave this on screen for Q&A |

---

## Speaker Notes by Slide

### Slide: The Diamond Problem

**Key talking points:**
1. Python uses MRO (C3 linearization) to resolve diamond inheritance
2. But MRO doesn't solve the architectural problem
3. The real issue: what happens when you need BOTH a FlyingPlayer AND a SwimmingPlayer that can also fly?

**Live demo:**
```python
# Show this in interpreter
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

print(D().method())  # B
print(D.__mro__)  # Shows resolution order
```

---

### Slide: Components Are Pure Data

**Emphasize:**
- No `def move(self)` on Position
- No `def take_damage(self, amount)` on Health
- Just data fields

**Anti-pattern to show:**
```python
# BAD - Component with logic
@dataclass
class Health:
    current: int
    maximum: int
    
    def take_damage(self, amount):  # NO! This is system logic
        self.current -= amount

# GOOD - Pure data
@dataclass
class Health:
    current: int
    maximum: int
```

---

### Slide: Benchmark Results

**Important context:**
1. Don't let students think ECS is "slow"
2. Emphasize that Python's interpreter overhead dominates
3. The real C++ story: ECS can be 10-100x faster due to cache locality

**Have this ready to explain:**
```
CPU Cache Hierarchy:
L1 Cache: ~1ns access (32KB)
L2 Cache: ~4ns access (256KB)
L3 Cache: ~12ns access (8MB)
RAM: ~100ns access

ECS in C++: Components in contiguous arrays = cache hits
OOP in C++: Objects scattered = cache misses
```

---

## Hands-On Exercises

### Exercise 1: Build a Component (5 minutes)

Create a `Poison` component that represents damage over time:

```python
from dataclasses import dataclass

# Your code here - define a Poison component with:
# - damage_per_second: float
# - remaining_duration: float
# - source: str (what caused the poison)

# Solution:
@dataclass
class Poison:
    damage_per_second: float = 5.0
    remaining_duration: float = 10.0
    source: str = "unknown"
```

---

### Exercise 2: Build a System (10 minutes)

Create a `PoisonSystem` that:
1. Finds all entities with both `Health` and `Poison` components
2. Reduces health based on poison damage
3. Reduces poison duration
4. Removes the Poison component when duration hits 0

```python
# Using esper
class PoisonProcessor(esper.Processor):
    def process(self, dt):
        to_remove = []
        
        for ent, (health, poison) in esper.get_components(Health, Poison):
            # Apply damage
            health.current -= poison.damage_per_second * dt
            
            # Reduce duration
            poison.remaining_duration -= dt
            
            # Mark for removal if expired
            if poison.remaining_duration <= 0:
                to_remove.append(ent)
        
        # Remove expired poison
        for ent in to_remove:
            esper.remove_component(ent, Poison)
```

---

### Exercise 3: Runtime Composition (10 minutes)

Implement a "power-up" system where:
1. Player collides with power-up
2. Power-up's effect is transferred to player
3. Power-up entity is destroyed

```python
@dataclass
class PowerUp:
    effect_type: str  # "speed", "invincibility", "damage"
    duration: float = 10.0

@dataclass
class SpeedBoost:
    multiplier: float = 2.0
    remaining: float = 10.0

@dataclass
class Invincibility:
    remaining: float = 5.0

class PowerUpSystem(esper.Processor):
    def process(self, dt):
        # Get all players and powerups
        players = list(esper.get_components(Position, Collider, PlayerTag))
        powerups = list(esper.get_components(Position, Collider, PowerUp))
        
        for p_ent, (p_pos, p_col, _) in players:
            for pu_ent, (pu_pos, pu_col, power) in powerups:
                if self._collides(p_pos, p_col, pu_pos, pu_col):
                    # Apply power-up effect
                    if power.effect_type == "speed":
                        esper.add_component(p_ent, SpeedBoost(duration=power.duration))
                    elif power.effect_type == "invincibility":
                        esper.add_component(p_ent, Invincibility(remaining=power.duration))
                    
                    # Destroy power-up
                    esper.delete_entity(pu_ent)
```

---

### Exercise 4: Full Mini-Game (20 minutes)

Build a complete mini-game with:
- Player (WASD movement)
- Enemies (random movement)
- Bullets (player shoots with space)
- Score tracking

**Starter template:**
```python
import esper
from dataclasses import dataclass

# Components
@dataclass
class Position:
    x: float
    y: float

@dataclass
class Velocity:
    dx: float = 0.0
    dy: float = 0.0

# TODO: Add Health, PlayerTag, EnemyTag, BulletTag components

# Systems
class MovementProcessor(esper.Processor):
    def process(self, dt):
        for ent, (pos, vel) in esper.get_components(Position, Velocity):
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt

# TODO: Add InputProcessor, CollisionProcessor, ScoreProcessor

# Game setup
def setup():
    esper.add_processor(MovementProcessor())
    # TODO: Add other processors
    
    # Create player
    # TODO
    
    # Create enemies
    # TODO

# Game loop
def game_loop():
    dt = 1/60
    while True:
        esper.process(dt)
        # TODO: Render, check game over, etc.
```

---

## Discussion Questions

### For Group Discussion (5 minutes each)

1. **"What's the biggest project where you've hit OOP inheritance problems?"**
   - Let people share horror stories
   - Builds buy-in for ECS

2. **"How would you handle a dragon that can both fly AND swim in OOP vs ECS?"**
   - OOP: FlyingSwimmingDragon class, or multiple interfaces
   - ECS: Just add Flight and Swimming components

3. **"What happens when you need to temporarily disable an entity's movement?"**
   - OOP: Set a flag, check flag everywhere
   - ECS: Remove Velocity component, or add Stunned component

4. **"How do you handle complex entity behaviors like a state machine?"**
   - Component for current state
   - System that processes state transitions
   - Or: Different components for each state

---

## Common Student Questions

### Q: "Isn't this just going back to procedural programming?"

**A:** Kind of! ECS is sometimes called "procedural with structure." The key differences:
- Components provide the "structure" that raw procedural lacks
- Systems are focused and single-purpose (not god functions)
- Entity IDs replace global state

### Q: "What about entity relationships (parent/child)?"

**A:** Options:
1. Component with parent_id: `@dataclass class Parent: parent_id: int`
2. Dedicated relationship storage (advanced ECS)
3. Some ECS libs have built-in relationship support

### Q: "How do I handle events between systems?"

**A:** Options:
1. Event queue component
2. Message bus (separate from ECS)
3. esper has `dispatch_event`/`set_handler`

### Q: "What about UI? Is that ECS too?"

**A:** Usually not! Common pattern:
- Game entities: ECS
- UI widgets: OOP
- They communicate through a thin interface

---

## Bonus: Advanced Topics (if time permits)

### Archetypes
- Group entities by component signature
- Faster iteration for common patterns
- Unity uses this extensively

### Sparse Sets
- O(1) component lookup
- O(1) entity iteration
- Memory vs speed tradeoff

### Parallelization
```python
# Systems that don't share components can run in parallel
# Movement uses: Position, Velocity
# AI uses: AI, Position, Velocity (CONFLICT with Movement!)
# Particles uses: Position, Particle (OK to parallel with Movement if Position is read-only)
```

### Entity Serialization
- All data is in components = easy to serialize
- Save game = serialize all components
- Network = sync only changed components

---

## Post-Workshop Resources

### Hand out this list:

1. **Esper Documentation**: https://esper.readthedocs.io
2. **ECS FAQ**: https://github.com/SanderMertens/ecs-faq
3. **This Demo Code**: Available in the workshop repo
4. **Discord**: [Game Dev community for questions]

### Homework Assignment:

Build a simple game using ECS:
- Snake game (entities: snake segments, food, walls)
- Asteroids (entities: ship, asteroids, bullets)
- Tower defense (entities: towers, enemies, projectiles)

Submit your Systems and Components for code review!

---

## Troubleshooting Common Issues

### "esper module not found"
```bash
pip install esper --break-system-packages
# or
pip install esper --user
```

### "Circular import errors"
- Put components in separate file
- Import components into systems
- Never import systems into components

### "Entity deleted while iterating"
```python
# BAD
for ent, (...) in esper.get_components(...):
    esper.delete_entity(ent)  # Modifies iterator!

# GOOD
to_delete = []
for ent, (...) in esper.get_components(...):
    if should_delete:
        to_delete.append(ent)
        
for ent in to_delete:
    esper.delete_entity(ent)
```
