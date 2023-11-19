import pygame
import random
import time
from falling_sun import FallingSun


class Peashooter():
    def __init__(self, pos: tuple[int, int], img: str, screen: pygame.Surface):
        self.pos = pos
        self.img = pygame.image.load(f"sprites/{img}/{img}.png").convert_alpha()
        self.screen = screen

    def draw(self):
        self.screen.blit(self.img, self.pos)


class Sunflower():
    def __init__(self, pos: tuple[int, int], img: str, screen: pygame.Surface):
        self.pos = pos
        self.img = pygame.image.load(f"sprites/{img}/{img}.png").convert_alpha()
        self.screen = screen
        self.cooldown = 3
        self.time_of_last_drop = time.time()

    def draw(self):
        self.screen.blit(self.img, self.pos)
