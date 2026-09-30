import math
import random
import array
import pygame
from game.beat import Note, LANES, LANE_KEYS, LANE_LABELS, LANE_COLORS

WIDTH, HEIGHT = 480, 640
FPS = 60
BPM = 120
NOTE_EVERY_N_BEATS = 2
HOLD_CHANCE = 0.15
HIT_Y = HEIGHT - 80
HIT_WINDOW = 45
BG = (15, 10, 25)
LANE_W = WIDTH // LANES


class GameEngine:
    def __init__(self):
        pygame.init()
        self.hit_sounds = {}

        try:
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=1,
                buffer=512
            )
            self.hit_sounds = {
                "PERFECT": self._make_beep(880),
                "GREAT": self._make_beep(660),
                "OK": self._make_beep(440),
            }
        except pygame.error:
            # The game can still run if no audio device is available.
            self.hit_sounds = {}

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rhythm Tap")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 26, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.reset()

    def _make_beep(self, frequency, duration=0.08):
        sample_rate = 44100
        samples = int(sample_rate * duration)
        amplitude = 10000
        data = array.array("h")

        for i in range(samples):
            value = int(
                amplitude
                * math.sin(2 * math.pi * frequency * i / sample_rate)
            )
            data.append(value)

        return pygame.mixer.Sound(buffer=data.tobytes())

    def reset(self):
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.misses = 0
        self.grade_counts = {
            "PERFECT": 0,
            "GREAT": 0,
            "OK": 0,
        }
        self.speed = 5
        self.frame = 0
        self.feedback = []
        self.game_over = False
        self.held_keys = set()
        self.active_holds = {}

        self.start_time = pygame.time.get_ticks()
        self.beat_interval = 60.0 / BPM
        self.beat_interval_ms = 60000.0 / BPM

        # The head of both normal and hold notes travels from y=-30 to
        # HIT_Y, so they use the same travel time. Keep next_beat_time as
        # the target HIT time, not the spawn time.
        self.travel_ms = (
            (HIT_Y - (-30)) / (self.speed * FPS)
        ) * 1000.0

        # First note should spawn about 1 second after reset.
        self.next_beat_time = (
            self.start_time + self.travel_ms + 1000.0
        )
        self.beat_number = NOTE_EVERY_N_BEATS

    def _lane_is_safe_for_normal(self, lane, beat_time):
        # A hold occupies its lane from 1000 ms before its hit until
        # 1000 ms after its hit.
        for note in self.notes:
            if note.lane != lane or note.hit or note.missed:
                continue
            if not note.is_hold or note.scheduled_hit_time is None:
                continue

            if abs(beat_time - note.scheduled_hit_time) <= 1000.0:
                return False

        return True

    def _lane_is_safe_for_hold(self, lane, beat_time):
        # A new hold cannot overlap any existing note in its lane.
        for note in self.notes:
            if note.lane != lane or note.hit or note.missed:
                continue
            if note.scheduled_hit_time is None:
                continue

            if abs(beat_time - note.scheduled_hit_time) <= 1000.0:
                return False

        return True

    def _choose_lane(self, is_hold, beat_time):
        lanes = list(range(LANES))
        random.shuffle(lanes)

        for lane in lanes:
            if is_hold:
                if self._lane_is_safe_for_hold(lane, beat_time):
                    return lane
            else:
                if self._lane_is_safe_for_normal(lane, beat_time):
                    return lane

        return None

    def spawn_note_for_beat(self, beat_time, now):
        is_hold = random.random() < HOLD_CHANCE
        lane = self._choose_lane(is_hold, beat_time)

        # If a hold cannot fit, try a normal note in a safe lane.
        if lane is None and is_hold:
            is_hold = False
            lane = self._choose_lane(False, beat_time)

        # If no lane is safe, skip this beat rather than overlapping notes.
        if lane is None:
            return

        spawn_time = beat_time - self.travel_ms
        lateness_ms = max(0.0, now - spawn_time)

        # A very late frame should not create a note in the middle of the
        # screen. The beat clock will continue normally and won't drift.
        if lateness_ms > 100.0:
            return

        lateness_seconds = lateness_ms / 1000.0
        speed_pixels_per_second = self.speed * FPS

        if is_hold:
            hold_length = self.speed * FPS

            # The head is the bottom of the bar. The whole bar starts above
            # the screen, with its head initially at y=-30.
            head_spawn_y = -30
            y = (
                head_spawn_y
                - hold_length
                + lateness_seconds * speed_pixels_per_second
            )

            note = Note(
                lane,
                y=y,
                speed=self.speed,
                is_hold=True
            )
        else:
            # A normal note's center is y + HEIGHT//2, so start at -40 so
            # the center travels from -30 to HIT_Y, matching travel_ms.
            spawn_y = -40
            y = spawn_y + lateness_seconds * speed_pixels_per_second

            note = Note(
                lane,
                y=y,
                speed=self.speed,
                is_hold=False
            )

        note.scheduled_hit_time = beat_time
        self.notes.append(note)

    def update_spawn_schedule(self):
        now = pygame.time.get_ticks()

        # next_beat_time is the target HIT time. Spawn exactly one travel
        # time before that target. Float milliseconds prevent BPM drift.
        while now >= self.next_beat_time - self.travel_ms:
            beat_time = self.next_beat_time

            if self.beat_number % NOTE_EVERY_N_BEATS == 0:
                self.spawn_note_for_beat(beat_time, now)

            self.beat_number += 1
            self.next_beat_time += self.beat_interval_ms

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.clear_active_holds()
                    self.reset()
                elif not self.game_over:
                    for i, key in enumerate(LANE_KEYS):
                        if event.key == key:
                            self.held_keys.add(key)

                            # A lane with an active hold is already being
                            # handled by that hold, so don't trigger another
                            # note in the same lane.
                            if i not in self.active_holds:
                                self.process_tap(i)
                            break

            elif event.type == pygame.KEYUP:
                if event.key in LANE_KEYS:
                    self.held_keys.discard(event.key)

                    lane = LANE_KEYS.index(event.key)
                    if lane in self.active_holds:
                        self.fail_hold(self.active_holds[lane])

        return True

    def process_tap(self, lane):
        # Find closest note in this lane near hit zone.
        # An active hold in this lane is deliberately ignored.
        if lane in self.active_holds:
            return

        best = None
        best_dist = 9999

        for note in self.notes:
            if note.lane != lane or note.hit or note.missed:
                continue

            if note.is_hold and note.hold_started:
                continue

            note_head_y = note.get_head_y()
            dist = abs(note_head_y - HIT_Y)

            if dist < best_dist:
                best_dist = dist
                best = note

        lane_x = lane * LANE_W + LANE_W // 2

        if best and best_dist <= HIT_WINDOW:
            if best.is_hold:
                self.start_hold(best, best_dist)
                return

            best.hit = True

            if best_dist < 8:
                grade, pts = "PERFECT", 300
                col = (255, 220, 0)
            elif best_dist < 18:
                grade, pts = "GREAT", 200
                col = (100, 220, 100)
            else:
                grade, pts = "OK", 100
                col = (180, 180, 255)

            self.grade_counts[grade] += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += pts * max(1, self.combo // 5)

            if grade in self.hit_sounds:
                self.hit_sounds[grade].play()

            self.feedback.append(
                [grade, col, 40, lane_x, HIT_Y - 30]
            )
        else:
            self.combo = 0
            self.feedback.append(
                ["MISS", (220, 60, 60), 40, lane_x, HIT_Y - 30]
            )

    def start_hold(self, note, best_dist):
        lane = note.lane

        if lane in self.active_holds:
            return

        if best_dist < 8:
            grade, pts = "PERFECT", 300
        elif best_dist < 18:
            grade, pts = "GREAT", 200
        else:
            grade, pts = "OK", 100

        note.hold_started = True
        note.hold_start_time = pygame.time.get_ticks()
        note.hold_grade = grade
        note.hold_points = pts
        self.active_holds[lane] = note

    def complete_hold(self, note):
        if note.missed or not note.hold_started:
            return

        note.hit = True
        note.hold_started = False
        self.active_holds.pop(note.lane, None)

        grade = note.hold_grade
        pts = note.hold_points
        self.grade_counts[grade] += 1

        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.score += pts * max(1, self.combo // 5)

        col = {
            "PERFECT": (255, 220, 0),
            "GREAT": (100, 220, 100),
            "OK": (180, 180, 255)
        }[grade]

        if grade in self.hit_sounds:
            self.hit_sounds[grade].play()

        lane_x = note.lane * LANE_W + LANE_W // 2
        self.feedback.append(
            [grade, col, 40, lane_x, HIT_Y - 30]
        )

    def fail_hold(self, note):
        if note.missed or not note.hold_started:
            return

        note.missed = True
        note.hold_started = False
        self.active_holds.pop(note.lane, None)
        self.combo = 0
        self.misses += 1

    def clear_active_holds(self):
        for note in list(self.active_holds.values()):
            note.hold_started = False

        self.active_holds.clear()
        self.held_keys.clear()

    def update_holds(self):
        now = pygame.time.get_ticks()

        for note in list(self.active_holds.values()):
            if note.missed or note.hit:
                self.active_holds.pop(note.lane, None)
                continue

            lane_key = LANE_KEYS[note.lane]

            if lane_key not in self.held_keys:
                self.fail_hold(note)
                continue

            if now - note.hold_start_time >= 1000:
                self.complete_hold(note)

    def update(self):
        if self.game_over:
            return

        self.frame += 1

        for note in self.notes:
            note.update()

        self.update_spawn_schedule()

        self.update_holds()

        for note in self.notes:
            if note.hit or note.missed or note.hold_started:
                continue

            # The head of both normal and unstarted hold notes determines
            # when the note can no longer be hit. Active holds are allowed
            # to continue for their full one-second duration.
            if note.get_head_y() > HIT_Y + HIT_WINDOW:
                note.missed = True
                self.misses += 1
                self.combo = 0

        self.notes = [
            n for n in self.notes
            if not (
                (n.hit or n.missed)
                and not n.hold_started
                and n.y > HEIGHT + 10
            )
        ]

        self.feedback = [
            [t, c, ttl - 1, x, y]
            for t, c, ttl, x, y in self.feedback
            if ttl > 1
        ]

        if self.misses >= 15:
            self.clear_active_holds()
            self.game_over = True

    def draw(self):
        self.screen.fill(BG)

        # Lane dividers
        for i in range(LANES + 1):
            pygame.draw.line(
                self.screen,
                (40, 40, 60),
                (i * LANE_W, 0),
                (i * LANE_W, HEIGHT),
                1
            )

        # Hit line
        pygame.draw.line(
            self.screen,
            (80, 80, 100),
            (0, HIT_Y),
            (WIDTH, HIT_Y),
            2
        )

        for i in range(LANES):
            lx = i * LANE_W + LANE_W // 2

            pygame.draw.rect(
                self.screen,
                LANE_COLORS[i],
                pygame.Rect(
                    lx - Note.WIDTH // 2,
                    HIT_Y - 12,
                    Note.WIDTH,
                    24
                ),
                border_radius=6
            )

            lbl = self.font.render(
                LANE_LABELS[i],
                True,
                (20, 20, 20)
            )

            self.screen.blit(
                lbl,
                (lx - lbl.get_width() // 2, HIT_Y - 10)
            )

        # Notes
        for note in self.notes:
            if note.hit and not note.hold_started:
                continue

            lx = note.lane * LANE_W + LANE_W // 2

            if note.is_hold:
                rect = note.get_hold_rect(lx)
                base = LANE_COLORS[note.lane]
                dim = tuple(c // 2 for c in base)

                # Dim, narrower body so it reads as one hold note
                body = rect.inflate(-24, 0)
                pygame.draw.rect(
                    self.screen, dim, body, border_radius=6
                )
                pygame.draw.rect(
                    self.screen, (240, 240, 240), body,
                    width=2, border_radius=6
                )

                # Bright full-width head at the bottom
                head_rect = pygame.Rect(
                    lx - Note.WIDTH // 2,
                    int(note.get_head_y()) - Note.HEIGHT // 2,
                    Note.WIDTH,
                    Note.HEIGHT
                )
                pygame.draw.rect(
                    self.screen, base, head_rect, border_radius=5
                )
                pygame.draw.rect(
                    self.screen, (255, 255, 255), head_rect,
                    width=2, border_radius=5
                )

                if note.hold_started:
                    elapsed = pygame.time.get_ticks() - note.hold_start_time
                    progress = min(1.0, elapsed / 1000.0)
                    progress_height = int(body.height * progress)

                    if progress_height > 0:
                        progress_rect = pygame.Rect(
                            body.x + 3,
                            body.bottom - progress_height,
                            body.width - 6,
                            progress_height
                        )
                        pygame.draw.rect(
                            self.screen, (255, 255, 255),
                            progress_rect, border_radius=3
                        )
            else:
                rect = note.get_rect(lx)

                pygame.draw.rect(
                    self.screen,
                    LANE_COLORS[note.lane],
                    rect,
                    border_radius=5
                )

        # Feedback
        for text, color, ttl, x, y in self.feedback:
            surf = self.font.render(text, True, color)
            alpha = min(255, ttl * 7)
            surf.set_alpha(alpha)

            self.screen.blit(
                surf,
                (x - surf.get_width() // 2, y)
            )

        # HUD
        sc = self.font.render(
            f"Score: {self.score}",
            True,
            (220, 220, 220)
        )

        co = self.font.render(
            f"Combo: {self.combo}x",
            True,
            (255, 220, 80)
        )

        mi = self.font.render(
            f"Misses: {self.misses}/15",
            True,
            (220, 100, 100)
        )

        self.screen.blit(sc, (10, 10))
        self.screen.blit(co, (10, 40))
        self.screen.blit(
            mi,
            (WIDTH - mi.get_width() - 10, 10)
        )

        if self.game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            self.screen.blit(ov, (0, 0))

            msg = self.big_font.render(
                "GAME OVER",
                True,
                (220, 60, 60)
            )

            self.screen.blit(
                msg,
                (
                    WIDTH // 2 - msg.get_width() // 2,
                    55
                )
            )

            hits = (
                self.grade_counts["PERFECT"]
                + self.grade_counts["GREAT"]
                + self.grade_counts["OK"]
            )
            total = hits + self.misses
            accuracy = 0.0 if total == 0 else hits / total * 100.0

            stats = [
                f"PERFECT: {self.grade_counts['PERFECT']}",
                f"GREAT:   {self.grade_counts['GREAT']}",
                f"OK:      {self.grade_counts['OK']}",
                f"MISS:    {self.misses}",
                f"Accuracy: {accuracy:.1f}%",
                f"Final Score: {self.score}",
                f"Max Combo: {self.max_combo}x",
            ]

            y = 135
            for stat in stats:
                surf = self.font.render(
                    stat,
                    True,
                    (220, 220, 220)
                )
                self.screen.blit(
                    surf,
                    (WIDTH // 2 - surf.get_width() // 2, y)
                )
                y += 42

            restart = self.font.render(
                "Press R to Restart",
                True,
                (160, 160, 160)
            )

            self.screen.blit(
                restart,
                (
                    WIDTH // 2 - restart.get_width() // 2,
                    y + 8
                )
            )

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()