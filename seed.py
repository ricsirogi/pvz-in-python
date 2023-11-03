import pygame
import time


class Seed():
    def __init__(self, pos: list[int], width_height: list[int], available_color: list[int], unavailable_color: list[int], available: bool, id: str, cost: int, cooldown: int, screen: pygame.Surface):
        self.pos = pos
        self.og_pos = pos.copy()  # (original position/default position)
        self.id = id
        self.cost = cost
        self.cooldown = cooldown
        self.time_of_placement = 0
        if self.id != "shovel":
            self.width_height = width_height
            self.available_color = available_color
            self.unavailable_color = unavailable_color
            self.img = pygame.image.load(f"sprites/{self.id}/{self.id}_seed.png")
            self.slot_img = pygame.image.load(f"sprites/{self.id}/{self.id}_seed_slot.png")
            self.unavailable_img = pygame.image.load(f"sprites/{self.id}/{self.id}_seed_unavailable.png")
        else:
            self.img = pygame.image.load("sprites/shovel.png").convert_alpha()
            self.width_height = [self.img.get_width(), self.img.get_height()]
        self.screen = screen
        self.available = available

        self.follow_mouse = False

    def draw(self, stored_sun: int):
        if self.id != "shovel":
            self.screen.blit(self.slot_img, self.og_pos)
        if stored_sun >= self.cost and time.time() - self.cooldown > self.time_of_placement:
            self.screen.blit(self.img, self.pos)
            self.available = True
        else:
            self.available = False
            if stored_sun < self.cost:
                self.screen.blit(self.unavailable_img, self.og_pos)
            if time.time() - self.cooldown < self.time_of_placement:
                self.screen.blit(self.unavailable_img, self.og_pos)

    def is_clicked(self, event: pygame.event.Event):
        if self.is_cursor_hovering() and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.id == "shovel":
                    self.follow_mouse = False
                    self.reset()

                if not self.follow_mouse:
                    self.follow_mouse = True
                else:  # if the seed is following the mouse and we click at it's original place, then put it back
                    self.follow_mouse = False
                    self.reset()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right mouse button
                if self.follow_mouse:
                    self.reset()

    def place(self):
        self.time_of_placement = time.time()
        self.reset()

    def reset(self):
        self.follow_mouse = False
        self.pos = self.og_pos.copy()

    def is_cursor_hovering(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.og_pos[0] <= mouse_pos[0] <= self.og_pos[0] + self.width_height[0] and self.og_pos[1] <= mouse_pos[1] <= self.og_pos[1] + self.width_height[1]
