import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animated Reptile Follows Cursor")
clock = pygame.time.Clock()

# Colors
BG_COLOR = (20, 30, 20)
BODY_COLOR = (60, 120, 60)
BODY_DARK = (40, 80, 40)
EYE_COLOR = (255, 220, 0)
PUPIL_COLOR = (20, 20, 20)
TONGUE_COLOR = (200, 50, 50)

class Reptile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 4.5
        # Segments for body (spine points)
        self.segments = [(x, y) for _ in range(12)]
        self.segment_distance = 18
        # Animation
        self.leg_phase = 0
        self.tongue_timer = 0
        self.tongue_out = False

    def update(self, target_x, target_y):
        # Calculate direction to target (cursor)
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 5:
            # Smooth angle rotation
            target_angle = math.atan2(dy, dx)
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += angle_diff * 0.15

            # Move forward
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed

        # Update spine segments (inverse kinematics chain)
        self.segments[0] = (self.x, self.y)
        for i in range(1, len(self.segments)):
            prev_x, prev_y = self.segments[i - 1]
            cur_x, cur_y = self.segments[i]
            dx = prev_x - cur_x
            dy = prev_y - cur_y
            d = math.hypot(dx, dy)
            if d > self.segment_distance:
                # Move segment toward previous one
                ratio = self.segment_distance / d
                new_x = prev_x - dx * ratio
                new_y = prev_y - dy * ratio
                self.segments[i] = (new_x, new_y)

        # Leg animation phase based on movement
        self.leg_phase += 0.3

        # Tongue animation
        self.tongue_timer += 1
        if self.tongue_timer > 60:  # every ~1 second
            self.tongue_out = not self.tongue_out
            self.tongue_timer = 0

    def draw(self, surface):
        # Draw legs (behind body)
        self.draw_legs(surface)

        # Draw body segments from tail to head (so head is on top)
        for i in range(len(self.segments) - 1, 0, -1):
            x, y = self.segments[i]
            # Tail tapers
            radius = max(4, 14 - i)
            color = BODY_DARK if i % 2 == 0 else BODY_COLOR
            pygame.draw.circle(surface, color, (int(x), int(y)), radius)

        # Draw head (first segment)
        hx, hy = self.segments[0]
        head_radius = 16
        pygame.draw.circle(surface, BODY_COLOR, (int(hx), int(hy)), head_radius)
        pygame.draw.circle(surface, BODY_DARK, (int(hx), int(hy)), head_radius, 2)

        # Draw eyes based on angle
        self.draw_eyes(surface, hx, hy)

        # Draw tongue
        if self.tongue_out:
            self.draw_tongue(surface, hx, hy)

    def draw_eyes(self, surface, hx, hy):
        # Eye positions perpendicular to head angle
        perp_angle = self.angle + math.pi / 2
        eye_offset = 7
        forward_offset = 5

        # Eye centers
        eye1_x = hx + math.cos(self.angle) * forward_offset + math.cos(perp_angle) * eye_offset
        eye1_y = hy + math.sin(self.angle) * forward_offset + math.sin(perp_angle) * eye_offset
        eye2_x = hx + math.cos(self.angle) * forward_offset - math.cos(perp_angle) * eye_offset
        eye2_y = hy + math.sin(self.angle) * forward_offset - math.sin(perp_angle) * eye_offset

        for ex, ey in [(eye1_x, eye1_y), (eye2_x, eye2_y)]:
            pygame.draw.circle(surface, EYE_COLOR, (int(ex), int(ey)), 5)
            # Pupil looks toward cursor
            pupil_offset = 2
            px = ex + math.cos(self.angle) * pupil_offset
            py = ey + math.sin(self.angle) * pupil_offset
            pygame.draw.circle(surface, PUPIL_COLOR, (int(px), int(py)), 2)

    def draw_tongue(self, surface, hx, hy):
        # Tongue extends forward from head
        tongue_len = 22
        tip_x = hx + math.cos(self.angle) * tongue_len
        tip_y = hy + math.sin(self.angle) * tongue_len
        mid_x = hx + math.cos(self.angle) * (tongue_len * 0.6)
        mid_y = hy + math.sin(self.angle) * (tongue_len * 0.6)

        pygame.draw.line(surface, TONGUE_COLOR, (hx, hy), (mid_x, mid_y), 3)
        # Forked tongue
        fork_angle = 0.4
        left_x = mid_x + math.cos(self.angle - fork_angle) * 8
        left_y = mid_y + math.sin(self.angle - fork_angle) * 8
        right_x = mid_x + math.cos(self.angle + fork_angle) * 8
        right_y = mid_y + math.sin(self.angle + fork_angle) * 8
        pygame.draw.line(surface, TONGUE_COLOR, (mid_x, mid_y), (left_x, left_y), 2)
        pygame.draw.line(surface, TONGUE_COLOR, (mid_x, mid_y), (right_x, right_y), 2)

    def draw_legs(self, surface):
        # Draw 4 legs at positions along the body
        leg_indices = [2, 4, 7, 9]
        for idx in leg_indices:
            if idx >= len(self.segments):
                continue
            sx, sy = self.segments[idx]
            # Determine if front or back leg
            is_front = idx < 6

            # Leg swings with phase
            phase_offset = 0 if is_front else math.pi
            swing = math.sin(self.leg_phase + phase_offset) * 0.5

            # Leg angles relative to body
            if is_front:
                base_angles = [self.angle + math.pi/3 + swing, self.angle - math.pi/3 - swing]
            else:
                base_angles = [self.angle + 2*math.pi/3 + swing, self.angle - 2*math.pi/3 - swing]

            for leg_angle in base_angles[:1]:  # one leg per side
                leg_len = 16
                ex = sx + math.cos(leg_angle) * leg_len
                ey = sy + math.sin(leg_angle) * leg_len
                # Upper leg
                pygame.draw.line(surface, BODY_DARK, (sx, sy), (ex, ey), 5)
                # Foot
                pygame.draw.circle(surface, BODY_DARK, (int(ex), int(ey)), 4)

            # Opposite side leg
            for leg_angle in base_angles[1:]:
                leg_len = 16
                ex = sx + math.cos(leg_angle) * leg_len
                ey = sy + math.sin(leg_angle) * leg_len
                pygame.draw.line(surface, BODY_DARK, (sx, sy), (ex, ey), 5)
                pygame.draw.circle(surface, BODY_DARK, (int(ex), int(ey)), 4)


def draw_background(surface):
    surface.fill(BG_COLOR)
    # Draw some grass tufts for atmosphere
    import random
    random.seed(42)  # consistent grass
    for _ in range(60):
        gx = random.randint(0, WIDTH)
        gy = random.randint(0, HEIGHT)
        for i in range(3):
            offset = (i - 1) * 4
            pygame.draw.line(surface, (30, 70, 30),
                             (gx + offset, gy),
                             (gx + offset + random.randint(-3, 3), gy - random.randint(5, 12)), 2)


def main():
    reptile = Reptile(WIDTH // 2, HEIGHT // 2)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update
        reptile.update(mouse_x, mouse_y)

        # Draw
        draw_background(screen)
        reptile.draw(screen)

        # Draw small cursor marker
        pygame.draw.circle(screen, (255, 100, 100), (mouse_x, mouse_y), 4, 1)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
