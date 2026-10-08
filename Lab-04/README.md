# Real-Time Fruit Slice Game

An interactive, real-time Fruit Ninja–style arcade game built in Python using **Pygame**. This project demonstrates object-oriented game architecture, continuous collision detection, dynamic difficulty scaling, and procedural sound synthesis.

---

## Features

- **Continuous Collision Detection (Swept Line Segments):** Fast blade swipes are checked using segment-to-circle distance calculations between consecutive frames, preventing quick cuts from skipping over targets.
- **Interactive Game Over Screen:** A dedicated modal overlay replaces raw terminal logs, displaying the final score, loss condition (*"Bomb Detonated!"* vs. *"Out of Lives!"*), and actionable prompts.
- **Replay System with Difficulty Presets:** Restart the game immediately after a loss without restarting the application:
  - **Easy:** Relaxed spawn intervals, lower bomb frequency (8%), slower projectile launch speed.
  - **Medium:** Standard arcade pacing with balanced fruit and bomb spawns (15% bomb chance).
  - **Hard:** Fast-paced spawning, high bomb presence (28%), accelerated projectile speeds.
- **Procedural Sound Engine:** Uses a built-in `SoundManager` utilizing Python's `array` module and `pygame.mixer` to synthesize 16-bit PCM waveforms on the fly (blade whooshes, bomb detonations, and defeat jingles) without requiring external audio assets.
- **Visual Feedback & HUD:** Real-time blade slash trails, remaining lives tracker, live score counter, and current difficulty indicators.

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` package manager

### Installation

1. Clone or download the repository to your local machine:

   ```bash
   git clone <repository-url>
   cd 41_fruit-ninja
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   (Or install Pygame directly: `pip install pygame`)

3. Launch the game:

   ```bash
   python main.py
   ```

---

## Controls

### Gameplay

| Action      | Input                                       |
|-------------|---------------------------------------------|
| Slice Blade | Click & drag / swipe mouse across fruits    |
| Quit Game   | Close window or press `ESC`                 |

### Game Over / Replay Screen

| Action             | Input Shortcut | Mouse Input              |
|--------------------|----------------|--------------------------|
| Replay (Easy)      | `1` or `E`     | Click **[E] Easy** button   |
| Replay (Medium)    | `2` or `M`     | Click **[M] Medium** button |
| Replay (Hard)      | `3` or `H`     | Click **[H] Hard** button   |
| Quit Application   | `Q` or `ESC`   | Close window             |

---

## Completed Tasks & Implementation Details

### Task 1: Refine Collision Detection

- **Issue:** The original `contains_point` implementation tested only discrete mouse coordinates. Fast swipes jumped over fruit radii between frames, causing visual cuts to miss.
- **Solution:** Added `intersects_segment(p1, p2)` in `game/fruit.py`. It projects the circle center onto the segment defined by consecutive mouse positions (`last_pos` to `pos`) using scalar projection clamped to $[0, 1]$, computing the exact minimum distance to the swipe segment.

### Task 2: Implement Game Over Condition

- **Issue:** The original engine printed the final score to standard output and froze object updates without giving the player a graphic UI.
- **Solution:** Built an in-engine semi-transparent overlay in `GameEngine.render()` that shows the failure reason, highlighted score, and prompts for replaying or exiting while preserving the main event loop.

### Task 3: Add Replay Option

- **Issue:** Players had to kill and restart the terminal process to play again.
- **Solution:** Implemented `reset_game(difficulty)` and clickable UI buttons alongside keyboard shortcuts. The engine supports Easy, Medium, and Hard configurations that dynamically adjust `spawn_interval`, `bomb_chance`, and `speed_scale`.

### Task 4: Add Sound Feedback

- **Issue:** The game had no audio cues for slicing, bomb explosions, or death screens.
- **Solution:** Added an integrated `SoundManager` that synthesizes sound waveforms into memory:
  - **Slice:** Frequency sweep downward (850 Hz → 300 Hz).
  - **Bomb:** Filtered brownian noise burst.
  - **Game Over:** Descending minor-arpeggio jingle.

---

## Folder Structure

```text
41_fruit-ninja/
├── main.py                 # Application entry point and display initialization
├── requirements.txt        # Project dependencies (pygame)
├── README.md               # Project documentation and specifications
└── game/
    ├── __init__.py         # Module initialization
    ├── fruit.py            # Fruit/bomb physics and segment collision detection
    └── game_engine.py      # Core game loop, sound engine, HUD, and state management
```
