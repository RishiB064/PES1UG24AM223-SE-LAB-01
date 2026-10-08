import math

class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.radius = radius
        self.kind = kind  # "fruit" or "bomb"
        self.sliced = False

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        return math.hypot(self.x - x, self.y - y) <= self.radius

    def intersects_segment(self, p1, p2):
        """
        Calculates shortest distance between circle center and the line segment (p1 -> p2).
        Returns True if line segment crosses within the fruit's radius.
        """
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1

        # Check endpoints directly
        if self.contains_point(x1, y1) or self.contains_point(x2, y2):
            return True

        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            return self.contains_point(x1, y1)

        # Parameter t: project center onto segment line, clamped to [0, 1]
        t = ((self.x - x1) * dx + (self.y - y1) * dy) / seg_len_sq
        t = max(0.0, min(1.0, t))

        # Closest point on the segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.hypot(self.x - closest_x, self.y - closest_y) <= self.radius

    def off_screen(self, height):
        return self.y - self.radius > height
