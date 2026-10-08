import pygame
import random
import math
import array
from .fruit import Fruit

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (40, 45, 60)
ACCENT_GREEN = (46, 204, 113)
ACCENT_YELLOW = (241, 196, 15)
ACCENT_RED = (231, 76, 60)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [(220, 60, 60), (230, 140, 40), (230, 200, 40), (90, 180, 90)]

DIFFICULTY_PRESETS = {
    "easy": {"interval": 70, "bomb_chance": 0.08, "speed": 0.85, "label": "Easy"},
    "medium": {"interval": 55, "bomb_chance": 0.15, "speed": 1.0, "label": "Medium"},
    "hard": {"interval": 38, "bomb_chance": 0.28, "speed": 1.25, "label": "Hard"},
}


class SoundManager:
    """Manages sound effects, falling back to procedural synthesis if files are missing."""
    def __init__(self):
        self.slice_sound = None
        self.bomb_sound = None
        self.game_over_sound = None
        self._init_mixer()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self._load_or_synthesize()
        except Exception as e:
            print(f"[SoundManager] Audio initialization error: {e}")

    def _load_or_synthesize(self):
        # 1. Slice sound (high-to-low fast whoosh)
        self.slice_sound = self._synthesize_sweep(850, 300, duration=0.12, volume=0.35)
        # 2. Bomb explosion (brownian noise burst)
        self.bomb_sound = self._synthesize_noise(duration=0.45, volume=0.5)
        # 3. Game Over (descending minor chords)
        self.game_over_sound = self._synthesize_jingle()

    def _synthesize_sweep(self, f_start, f_end, duration, volume):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        for i in range(n_samples):
            t = i / sample_rate
            prog = t / duration
            freq = f_start + (f_end - f_start) * prog
            env = math.sin(math.pi * (1.0 - prog) * 0.5)
            val = int(32767 * volume * env * math.sin(2 * math.pi * freq * t))
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _synthesize_noise(self, duration, volume):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        val = 0.0
        for i in range(n_samples):
            prog = i / n_samples
            env = (1.0 - prog) ** 1.6
            step = random.uniform(-1.0, 1.0)
            val = 0.85 * val + 0.15 * step
            buf.append(int(32767 * volume * env * val))
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _synthesize_jingle(self):
        sample_rate = 22050
        buf = array.array('h')
        notes = [440, 370, 311, 220]
        note_dur = 0.18
        for freq in notes:
            n_samples = int(sample_rate * note_dur)
            for i in range(n_samples):
                t = i / sample_rate
                prog = t / note_dur
                env = 1.0 - prog
                val = int(32767 * 0.35 * env * math.sin(2 * math.pi * freq * t))
                buf.append(val)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def play_slice(self):
        if self.slice_sound:
            self.slice_sound.play()

    def play_bomb(self):
        if self.bomb_sound:
            self.bomb_sound.play()

    def play_game_over(self):
        if self.game_over_sound:
            self.game_over_sound.play()


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fruits = []
        self.trail = []
        self.last_pos = None

        self.difficulty = "medium"
        self._apply_difficulty(self.difficulty)

        self.lives = 3
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""

        # Fonts
        self.font = pygame.font.SysFont("Arial", 28)
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)

        # Audio
        self.sounds = SoundManager()

        # UI button rects for Game Over screen
        self.buttons = {
            "easy": pygame.Rect(width // 2 - 210, 360, 120, 45),
            "medium": pygame.Rect(width // 2 - 60, 360, 120, 45),
            "hard": pygame.Rect(width // 2 + 90, 360, 120, 45),
        }

    def _apply_difficulty(self, diff_name):
        self.difficulty = diff_name
        settings = DIFFICULTY_PRESETS[diff_name]
        self.spawn_interval = settings["interval"]
        self.bomb_chance = settings["bomb_chance"]
        self.speed_scale = settings["speed"]
        self._spawn_timer = 0

    def reset_game(self, difficulty=None):
        if difficulty is not None:
            self._apply_difficulty(difficulty)
        self.fruits = []
        self.trail = []
        self.last_pos = None
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""
        self._spawn_timer = 0

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(x, self.height + 30, vx, vy, gravity, kind=kind)
        fruit.color = BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)
        self.fruits.append(fruit)

    def handle_event(self, event):
        if self.game_over:
            # Handle Game Over keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_e):
                    self.reset_game("easy")
                elif event.key in (pygame.K_2, pygame.K_m):
                    self.reset_game("medium")
                elif event.key in (pygame.K_3, pygame.K_h):
                    self.reset_game("hard")
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            # Handle Game Over mouse click input
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for diff, rect in self.buttons.items():
                    if rect.collidepoint(event.pos):
                        self.reset_game(diff)
                        break
            return

        # Normal Gameplay: Motion and slice detection
        if event.type == pygame.MOUSEMOTION:
            self._handle_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.last_pos = None

    def _handle_motion(self, pos):
        # Task 1: Check segment intersection between last_pos and current pos
        if self.last_pos is not None:
            for fruit in self.fruits:
                if not fruit.sliced and fruit.intersects_segment(self.last_pos, pos):
                    self._slice(fruit)
        else:
            for fruit in self.fruits:
                if not fruit.sliced and fruit.contains_point(*pos):
                    self._slice(fruit)

        self.last_pos = pos
        self.trail.append(pos)
        if len(self.trail) > 15:
            self.trail.pop(0)

    def _slice(self, fruit):
        fruit.sliced = True
        if fruit.kind == "bomb":
            self.sounds.play_bomb()
            self._trigger_game_over("Bomb Detonated!")
        else:
            self.sounds.play_slice()
            self.score += 1

    def _trigger_game_over(self, reason):
        self.game_over = True
        self.game_over_reason = reason
        self.sounds.play_game_over()

    def handle_input(self):
        pass

    def update(self):
        if self.game_over:
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []
        for fruit in self.fruits:
            fruit.update()
            if fruit.sliced:
                continue
            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue
            still_alive.append(fruit)
        self.fruits = still_alive

        if self.lives <= 0:
            self._trigger_game_over("Out of Lives!")

    def render(self, screen):
        # Render active fruits
        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)
            pygame.draw.circle(screen, color, (int(fruit.x), int(fruit.y)), fruit.radius)

        # Render blade trail
        if len(self.trail) >= 2:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        # Render HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (15, 15))

        lives_text = self.font.render(f"Lives: {self.lives}", True, ACCENT_RED if self.lives == 1 else WHITE)
        screen.blit(lives_text, (self.width - 130, 15))

        diff_badge = self.font_small.render(f"Mode: {self.difficulty.capitalize()}", True, GRAY)
        screen.blit(diff_badge, (15, 50))

        # Task 2 & 3: Render Game Over Modal Overlay
        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        # Darkened transparent backdrop
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 215))
        screen.blit(overlay, (0, 0))

        # Game Over Title
        title = self.font_large.render("GAME OVER", True, ACCENT_RED)
        screen.blit(title, title.get_rect(center=(self.width // 2, 170)))

        # Reason for failure
        reason = self.font.render(self.game_over_reason, True, WHITE)
        screen.blit(reason, reason.get_rect(center=(self.width // 2, 225)))

        # Final Score
        score = self.font_large.render(f"Final Score: {self.score}", True, ACCENT_YELLOW)
        screen.blit(score, score.get_rect(center=(self.width // 2, 280)))

        # Replay prompt
        prompt = self.font_small.render("Select a difficulty to replay, or press Q to exit:", True, GRAY)
        screen.blit(prompt, prompt.get_rect(center=(self.width // 2, 335)))

        # Difficulty Selection Buttons
        mouse_pos = pygame.mouse.get_pos()
        colors = {"easy": ACCENT_GREEN, "medium": ACCENT_YELLOW, "hard": ACCENT_RED}

        for diff, rect in self.buttons.items():
            is_hover = rect.collidepoint(mouse_pos)
            btn_color = colors[diff] if is_hover else DARK_GRAY
            border_color = colors[diff]

            pygame.draw.rect(screen, btn_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)

            label = self.font_small.render(f"[{diff[0].upper()}] {diff.capitalize()}", True, WHITE)
            screen.blit(label, label.get_rect(center=rect.center))

        quit_hint = self.font_small.render("Keyboard: [1] Easy  [2] Med  [3] Hard  |  [Q/ESC] Quit", True, GRAY)
        screen.blit(quit_hint, quit_hint.get_rect(center=(self.width // 2, 440)))
