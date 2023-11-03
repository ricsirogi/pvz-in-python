import pygame


class Pea():
    def __init__(self, pos: tuple[int, int], img: str, screen: pygame.Surface):
        self.pos = pos
        self.img = pygame.image.load(f"sprites/{img}/{img}.png").convert_alpha()
        self.screen = screen

    def draw(self):
        self.screen.blit(self.img, self.pos)


class Sun():
    def __init__(self, pos: tuple[int, int], img: str, screen: pygame.Surface):
        self.pos = pos
        self.img = pygame.image.load(f"sprites/{img}/{img}.png").convert_alpha()
        self.screen = screen

    def draw(self):
        self.screen.blit(self.img, self.pos)
