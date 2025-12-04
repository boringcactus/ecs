#!/usr/bin/env python3
"""
Pygame Visualization for ECS Demo
==================================
A visual demonstration of the Esper ECS architecture using Pygame.

Controls:
- Arrow Keys / WASD: Move player
- Mouse Click: Shoot projectiles
- SPACE: Spawn enemy
- ESC: Quit
- R: Restart
"""
import sys
import pygame
from approaches.esper_ecs import EsperWorld


class PygameECSDemo:
    """Pygame visualization wrapper for the ECS demo."""

    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("ECS Demo - Esper + Pygame")

        self.clock = pygame.time.Clock()
        self.running = True
        self.world = EsperWorld(width, height)

        # UI font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Initialize game
        self.reset_game()

    def reset_game(self):
        """Reset the game world."""
        self.world = EsperWorld(self.width, self.height)
        self.world.spawn_player()

        # Spawn initial enemies
        for _ in range(5):
            self.world.spawn_enemy()

    def handle_events(self) -> dict:
        """Process pygame events and return key state."""
        keys = {}
        mouse_click = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_SPACE:
                    self.world.spawn_enemy()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_click = pygame.mouse.get_pos()

        # Get continuous key states
        pressed = pygame.key.get_pressed()
        keys['left'] = pressed[pygame.K_LEFT] or pressed[pygame.K_a]
        keys['right'] = pressed[pygame.K_RIGHT] or pressed[pygame.K_d]
        keys['up'] = pressed[pygame.K_UP] or pressed[pygame.K_w]
        keys['down'] = pressed[pygame.K_DOWN] or pressed[pygame.K_s]

        # Handle shooting
        if mouse_click and self.world.player_id:
            import esper
            if esper.entity_exists(self.world.player_id):
                from approaches.esper_ecs import Position
                player_pos = esper.component_for_entity(self.world.player_id, Position)
                self.world.spawn_projectile(
                    player_pos.x, player_pos.y,
                    mouse_click[0], mouse_click[1]
                )

        return keys

    def render(self):
        """Render the game world."""
        # Clear screen with dark background
        self.screen.fill((20, 20, 30))

        # Get render data from ECS world
        render_data = self.world.get_render_data()

        # Draw all entities
        for entity in render_data:
            color = entity['color']
            x = int(entity['x'])
            y = int(entity['y'])
            radius = int(entity['radius'])

            if entity['type'] == 'circle':
                pygame.draw.circle(self.screen, color, (x, y), radius)
                # Add a white outline for better visibility
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius, 1)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        """Draw UI elements (stats, controls)."""
        stats = self.world.get_stats()

        # Health bar
        health_width = 200
        health_height = 20
        health_x = 10
        health_y = 10

        # Background
        pygame.draw.rect(self.screen, (60, 60, 60),
                        (health_x, health_y, health_width, health_height))

        # Health fill
        health_percent = max(0, min(1, stats['player_health'] / 100))
        health_color = self._get_health_color(health_percent)
        pygame.draw.rect(self.screen, health_color,
                        (health_x, health_y, int(health_width * health_percent), health_height))

        # Health outline
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (health_x, health_y, health_width, health_height), 2)

        # Health text
        health_text = self.small_font.render(
            f"Health: {stats['player_health']}/100", True, (255, 255, 255)
        )
        self.screen.blit(health_text, (health_x + health_width + 10, health_y))

        # Score
        score_text = self.font.render(f"Score: {stats['player_score']}", True, (255, 255, 0))
        self.screen.blit(score_text, (10, 40))

        # Entity counts
        y_offset = 80
        entities_text = self.small_font.render(
            f"Enemies: {stats['enemy_count']} | Bullets: {stats['bullet_count']} | Total: {stats['total_entities']}",
            True, (200, 200, 200)
        )
        self.screen.blit(entities_text, (10, y_offset))

        # Controls help (bottom right)
        controls = [
            "Arrow/WASD: Move",
            "Mouse: Shoot",
            "SPACE: Spawn Enemy",
            "R: Restart",
            "ESC: Quit"
        ]

        y = self.height - len(controls) * 25 - 10
        for control in controls:
            text = self.small_font.render(control, True, (150, 150, 150))
            self.screen.blit(text, (self.width - 200, y))
            y += 25

        # FPS counter (top right)
        fps = int(self.clock.get_fps())
        fps_text = self.small_font.render(f"FPS: {fps}", True, (100, 255, 100))
        self.screen.blit(fps_text, (self.width - 100, 10))

    def _get_health_color(self, percent: float) -> tuple:
        """Get color based on health percentage (green -> yellow -> red)."""
        if percent > 0.6:
            return (0, 255, 0)
        elif percent > 0.3:
            return (255, 255, 0)
        else:
            return (255, 0, 0)

    def run(self):
        """Main game loop."""
        target_fps = 60

        while self.running:
            # Calculate delta time
            dt = self.clock.tick(target_fps) / 1000.0

            # Handle input
            keys = self.handle_events()

            # Update ECS world
            self.world.update(dt, keys)

            # Render
            self.render()

        pygame.quit()
        sys.exit()


def main():
    """Entry point for the Pygame demo."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ECS DEMO - PYGAME VISUALIZATION                           ║
║                                                                              ║
║  This demo visualizes the Esper ECS architecture in action!                 ║
║                                                                              ║
║  Controls:                                                                   ║
║    • Arrow Keys or WASD - Move your player (green circle)                   ║
║    • Mouse Click - Shoot projectiles (yellow circles)                       ║
║    • SPACE - Spawn a new enemy (red circles)                                ║
║    • R - Restart the game                                                   ║
║    • ESC - Quit                                                             ║
║                                                                              ║
║  Watch how the ECS systems work together:                                   ║
║    • Movement System: Updates positions based on velocity                   ║
║    • AI System: Enemies wander around randomly                              ║
║    • Collision System: Detects hits and applies damage                      ║
║    • Lifetime System: Removes expired projectiles                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    try:
        demo = PygameECSDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
