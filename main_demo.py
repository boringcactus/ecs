#!/usr/bin/env python3
"""
Entity Component System Demo - Main Runner
===========================================
Compares different approaches to game architecture:
1. Traditional OOP (inheritance-based)
2. Naive/Manual ECS (built from scratch)
3. Esper Library ECS (optimized, popular)
4. ECS Pattern Style (entity-class focused)

Run this file to see benchmarks and comparisons.
"""
import sys
import time
from typing import Dict, List
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, '/home/claude/ecs_demo')

from approaches.oop_approach import OOPWorld, run_benchmark as oop_benchmark
from approaches.naive_ecs import NaiveECSWorld, run_benchmark as naive_benchmark
from approaches.esper_ecs import EsperWorld, run_benchmark as esper_benchmark
from approaches.ecs_pattern_approach import ECSPatternWorld, run_benchmark as pattern_benchmark


@dataclass
class BenchmarkResult:
    approach: str
    entities: int
    frames: int
    total_time: float
    avg_frame_time: float
    fps: float


def run_all_benchmarks(entity_counts: List[int] = None, num_frames: int = 100) -> List[BenchmarkResult]:
    """Run benchmarks for all approaches with various entity counts."""
    if entity_counts is None:
        entity_counts = [100, 500, 1000, 2000]
    
    results = []
    
    for count in entity_counts:
        print(f"\n{'='*60}")
        print(f"Benchmarking with {count} entities, {num_frames} frames...")
        print('='*60)
        
        # OOP Approach
        print("  Running OOP benchmark...", end=" ", flush=True)
        result = oop_benchmark(count, num_frames)
        results.append(BenchmarkResult(**result))
        print(f"Done ({result['fps']:.1f} FPS)")
        
        # Naive ECS
        print("  Running Naive ECS benchmark...", end=" ", flush=True)
        result = naive_benchmark(count, num_frames)
        results.append(BenchmarkResult(**result))
        print(f"Done ({result['fps']:.1f} FPS)")
        
        # Esper ECS
        print("  Running Esper ECS benchmark...", end=" ", flush=True)
        result = esper_benchmark(count, num_frames)
        results.append(BenchmarkResult(**result))
        print(f"Done ({result['fps']:.1f} FPS)")
        
        # ECS Pattern
        print("  Running ECS Pattern benchmark...", end=" ", flush=True)
        result = pattern_benchmark(count, num_frames)
        results.append(BenchmarkResult(**result))
        print(f"Done ({result['fps']:.1f} FPS)")
    
    return results


def print_results_table(results: List[BenchmarkResult]):
    """Print results as a formatted table."""
    print("\n" + "="*80)
    print("BENCHMARK RESULTS")
    print("="*80)
    
    # Group by entity count
    by_count: Dict[int, List[BenchmarkResult]] = {}
    for r in results:
        if r.entities not in by_count:
            by_count[r.entities] = []
        by_count[r.entities].append(r)
    
    for count in sorted(by_count.keys()):
        print(f"\n{count} Entities:")
        print("-" * 70)
        print(f"{'Approach':<20} {'Total Time':>12} {'Avg Frame':>12} {'FPS':>10}")
        print("-" * 70)
        
        for r in sorted(by_count[count], key=lambda x: x.fps, reverse=True):
            print(f"{r.approach:<20} {r.total_time*1000:>10.2f}ms {r.avg_frame_time*1000:>10.3f}ms {r.fps:>10.1f}")


def print_comparison_analysis():
    """Print qualitative comparison of approaches."""
    print("\n" + "="*80)
    print("APPROACH COMPARISON ANALYSIS")
    print("="*80)
    
    comparison = """
┌─────────────────────┬─────────────────────────────────────────────────────────┐
│ ASPECT              │ COMPARISON                                               │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ CODE COMPLEXITY     │ OOP > ECS Pattern > Naive ECS > Esper                   │
│                     │ (OOP has most inheritance complexity)                    │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ FLEXIBILITY         │ Esper = Naive ECS > ECS Pattern > OOP                    │
│                     │ (ECS allows runtime composition; OOP is static)          │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ LEARNING CURVE      │ OOP < ECS Pattern < Naive ECS < Esper                    │
│                     │ (OOP familiar but ECS concepts take time)                │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ MAINTAINABILITY     │ Esper > ECS Pattern > Naive ECS > OOP                    │
│                     │ (ECS separation of concerns wins long-term)              │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ PERFORMANCE (Python)│ Esper ≈ Naive ECS > ECS Pattern ≈ OOP                    │
│                     │ (Esper has optimizations; Python limits all)             │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ DEBUGGING           │ ECS Pattern > Esper > Naive ECS > OOP                    │
│                     │ (Typed entities help; deep inheritance hurts)            │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ TESTING             │ All ECS approaches >> OOP                                │
│                     │ (Systems are pure functions on data)                     │
├─────────────────────┼─────────────────────────────────────────────────────────┤
│ BEST USE CASE       │ OOP: Tiny projects, beginners                            │
│                     │ Naive ECS: Learning ECS concepts                          │
│                     │ Esper: Production Python games                            │
│                     │ ECS Pattern: Teams wanting explicit archetypes            │
└─────────────────────┴─────────────────────────────────────────────────────────┘
"""
    print(comparison)


def demonstrate_flexibility():
    """Show how ECS allows runtime composition that OOP cannot."""
    print("\n" + "="*80)
    print("FLEXIBILITY DEMONSTRATION: Runtime Component Addition")
    print("="*80)
    
    print("""
In OOP, changing an entity's capabilities requires:
  1. Creating a new class
  2. Migrating state
  3. Updating all references

In ECS, it's just adding/removing components:
""")
    
    # Demonstrate with Esper
    from approaches.esper_ecs import EsperWorld, Position, Velocity, AI, PlayerTag
    import esper
    
    world = EsperWorld()
    player_id = world.spawn_player()
    
    print(f"  Created player entity: {player_id}")
    print(f"  Has AI component? {esper.has_component(player_id, AI)}")
    
    # Add AI to player (making them AI-controlled)
    esper.add_component(player_id, AI())
    print(f"  Added AI component!")
    print(f"  Has AI component? {esper.has_component(player_id, AI)}")
    
    # Remove player control
    esper.remove_component(player_id, PlayerTag)
    print(f"  Removed PlayerTag - entity is now an NPC!")
    
    print("""
This dynamic composition is IMPOSSIBLE with traditional inheritance:
  - A Player class can't become an Enemy at runtime
  - Adding 'swimming' requires a SwimmingPlayer subclass
  - The inheritance tree explodes with combinations
""")


def demonstrate_system_isolation():
    """Show how systems are isolated and can be easily tested/modified."""
    print("\n" + "="*80)
    print("SYSTEM ISOLATION DEMONSTRATION")
    print("="*80)
    
    print("""
Each system operates independently on components it cares about:

┌──────────────────────────────────────────────────────────────────────┐
│ MovementSystem                                                        │
│   Requires: Position, Velocity                                        │
│   Ignores:  Health, AI, Renderable, etc.                             │
│   Does:     position += velocity * dt                                 │
├──────────────────────────────────────────────────────────────────────┤
│ AISystem                                                              │
│   Requires: Position, Velocity, AI                                    │
│   Ignores:  Health, Renderable, PlayerTag, etc.                      │
│   Does:     Updates velocity based on AI decisions                    │
├──────────────────────────────────────────────────────────────────────┤
│ CollisionSystem                                                       │
│   Requires: Position, Collider                                        │
│   Optional: Health, Damage                                            │
│   Does:     Detects overlaps, triggers damage                         │
├──────────────────────────────────────────────────────────────────────┤
│ RenderSystem                                                          │
│   Requires: Position, Renderable                                      │
│   Ignores:  Everything else                                           │
│   Does:     Draws entities to screen                                  │
└──────────────────────────────────────────────────────────────────────┘

Benefits:
  ✓ Systems can be tested in isolation
  ✓ Adding new systems doesn't affect existing ones
  ✓ Systems can run in parallel (if no shared mutation)
  ✓ Easy to enable/disable features (just remove system)
""")


def run_interactive_demo():
    """Run an interactive simulation you can watch."""
    print("\n" + "="*80)
    print("INTERACTIVE SIMULATION (text-based)")
    print("="*80)
    
    from approaches.esper_ecs import EsperWorld
    
    world = EsperWorld(80, 24)  # Console-sized
    world.spawn_player()
    
    for _ in range(10):
        world.spawn_enemy()
    
    print("\nSimulating 5 seconds of gameplay...")
    
    for second in range(5):
        for frame in range(60):
            # Occasional shooting
            if frame % 30 == 0:
                world.spawn_projectile(40, 12, 60, 12)
            
            world.update(1/60, {'right': frame % 120 < 60})
        
        stats = world.get_stats()
        print(f"  Second {second+1}: {stats['enemy_count']} enemies, "
              f"{stats['bullet_count']} bullets, "
              f"Score: {stats['player_score']}, "
              f"Health: {stats['player_health']}")
    
    print("\nFinal state:", world.get_stats())


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              ENTITY COMPONENT SYSTEM (ECS) ARCHITECTURE DEMO                 ║
║                                                                              ║
║  Comparing 4 approaches to game architecture in Python:                      ║
║    1. Traditional Object-Oriented Programming                                ║
║    2. Naive/Manual ECS Implementation                                        ║
║    3. Esper Library (production-ready ECS)                                   ║
║    4. ECS Pattern Style (typed entity classes)                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Run all demonstrations
    demonstrate_flexibility()
    demonstrate_system_isolation()
    
    print("\n" + "="*80)
    print("RUNNING PERFORMANCE BENCHMARKS...")
    print("="*80)
    
    results = run_all_benchmarks([100, 500, 1000], num_frames=60)
    print_results_table(results)
    print_comparison_analysis()
    
    run_interactive_demo()
    
    print("\n" + "="*80)
    print("DEMO COMPLETE!")
    print("="*80)
    print("""
Key Takeaways:
  1. ECS separates DATA (components) from LOGIC (systems)
  2. Entities are just IDs - composition over inheritance
  3. Systems process batches of entities with specific components
  4. This enables flexibility, testability, and (in other languages) performance
  
For Python game development, we recommend:
  • Esper for production games
  • Naive ECS for learning the concepts
  • ECS Pattern style when you want typed entities
  • Avoid deep OOP inheritance hierarchies

Check out the individual files in the 'approaches/' directory for detailed code!
""")


if __name__ == "__main__":
    main()
