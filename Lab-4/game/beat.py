import pygame
import random

LANES = 4
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_LABELS = ['D', 'F', 'J', 'K']
LANE_COLORS = [(220,80,80),(80,180,220),(100,220,100),(220,180,60)]


class Note:
    WIDTH = 70
    HEIGHT = 20

    def __init__(self, lane, y=-30, speed=4, is_hold=False):
        self.lane = lane
        self.y = y
        self.speed = speed
        self.hit = False
        self.missed = False

        self.is_hold = is_hold
        self.hold_length = 0
        self.hold_started = False
        self.hold_start_time = None
        self.hold_grade = None
        self.hold_points = 0
        self.scheduled_hit_time = None

        if self.is_hold:
            self.hold_length = self.speed * 60

    def update(self):
        self.y += self.speed

    def get_rect(self, lane_x):
        return pygame.Rect(
            lane_x - self.WIDTH // 2,
            int(self.y),
            self.WIDTH,
            self.HEIGHT
        )

    def get_head_y(self):
        if self.is_hold:
            return self.y + self.hold_length
        return self.y + self.HEIGHT // 2

    def get_hold_rect(self, lane_x):
        return pygame.Rect(
            lane_x - self.WIDTH // 2,
            int(self.y),
            self.WIDTH,
            max(1, int(self.hold_length))
        )
