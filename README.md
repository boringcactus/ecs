# Entity Component System (ECS) Demo

A comprehensive demonstration comparing different game architecture approaches in Python, with a focus on Entity Component System patterns.

## Overview

This project compares four different approaches to game architecture:

1. **Traditional OOP** - Inheritance-based game objects
2. **Naive ECS** - Hand-built Entity Component System for learning
3. **Esper ECS** - Production-ready library (recommended)
4. **ECS Pattern** - Typed entity approach with dataclasses

## Quick Start

```bash
# Install dependencies using uv (recommended)
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or using pip
pip install pygame esper

# Run the Pygame visualization (recommended for visual learners!)
python pygame_demo.py

# Run the text-based demo with benchmarks
python main_demo.py

# Run individual approaches
python approaches/oop_approach.py
python approaches/naive_ecs.py
python approaches/esper_ecs.py
python approaches/ecs_pattern_approach.py
```

## Project Structure

```
ecs_demo/
├── main_demo.py                    # Main comparison and benchmark runner
├── approaches/
│   ├── oop_approach.py             # Traditional OOP (for comparison)
│   ├── naive_ecs.py                # Hand-built ECS implementation
│   ├── esper_ecs.py                # Using esper library
│   └── ecs_pattern_approach.py     # Typed entity approach
├── utils/
│   └── components.py               # Shared component definitions
└── presentation/
    ├── ECS_PRESENTATION.md         # 30-minute slide deck
    └── SPEAKER_NOTES.md            # Teaching materials and exercises
```

## What's Demonstrated

### The Problem with OOP

- Diamond inheritance complexity
- Feature explosion (SwimmingFlyingPlayer?)
- Runtime inflexibility
- The "God Object" anti-pattern

### ECS Core Concepts

- **Entities**: Just integer IDs, no behavior
- **Components**: Pure data containers (dataclasses)
- **Systems**: Logic that processes components

### Runtime Composition

```python
# Can't do this in OOP without recreating the object
esper.add_component(rock_id, AI(behavior="aggressive"))
esper.remove_component(rock_id, AI)
```

## Benchmark Results

| Approach | 100 Entities | 500 Entities | 1000 Entities |
|----------|--------------|--------------|---------------|
| OOP | ~15000 FPS | ~4000 FPS | ~2000 FPS |
| ECS Pattern | ~6000 FPS | ~1200 FPS | ~600 FPS |
| Esper | ~5000 FPS | ~900 FPS | ~400 FPS |
| Naive ECS | ~3000 FPS | ~650 FPS | ~300 FPS |

**Note**: OOP performs well in Python due to optimized attribute access. The benefits of ECS in Python are architectural (flexibility, testability, maintainability), not performance-based. In C++/Rust, ECS can be 10-100x faster due to cache locality.

## Key Takeaways

1. **ECS separates data (components) from logic (systems)**
2. **Composition over inheritance** - no diamond problem
3. **Runtime flexibility** - add/remove behaviors dynamically
4. **Better testability** - systems are pure functions on data
5. **Cleaner code** - each system has a single responsibility

## Recommendations

| Use Case | Recommended Approach |
|----------|---------------------|
| Learning ECS | Naive implementation |
| Production Python game | Esper library |
| Type-heavy codebase | ECS Pattern style |
| Performance critical | PyPy + Esper, or Rust |
| Small jam game | Whatever you know |

## Presentation Materials

The `presentation/` folder contains:

- **ECS_PRESENTATION.md**: Full 30-minute slide deck in Markdown
- **SPEAKER_NOTES.md**: Teaching notes, exercises, and discussion questions

## Pygame Visualization

The project now includes an interactive Pygame visualization that demonstrates ECS concepts in action!

Run it with:
```bash
python pygame_demo.py
```

Features:
- Visual representation of entities (player, enemies, projectiles)
- Real-time ECS system updates
- Interactive controls (keyboard + mouse)
- HUD showing health, score, and entity counts
- Live demonstration of component composition and systems working together

Controls:
- Arrow Keys / WASD: Move player (green circle)
- Mouse Click: Shoot projectiles at cursor
- SPACE: Spawn additional enemy
- R: Restart game
- ESC: Quit

## Dependencies

- Python 3.12+ (for Pygame compatibility)
- pygame (`pip install pygame`)
- esper (`pip install esper`)

## Further Reading

- [Esper Documentation](https://esper.readthedocs.io)
- [ECS FAQ](https://github.com/SanderMertens/ecs-faq)
- [Entity Systems Wiki](https://entity-systems.wikidot.com/)
- [Game Programming Patterns](https://gameprogrammingpatterns.com/) (free online book)

## License

MIT License - Use freely for learning and production.
