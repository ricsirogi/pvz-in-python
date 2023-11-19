import pygame
import time


class Seed():
    def __init__(self, pos: list[int], width_height: list[int], id: str, cost: int, cooldown: float, start_with_cooldown: bool, screen: pygame.Surface):
        self.pos = pos
        self.og_pos = pos.copy()  # (original position/default position)
        self.id = id
        self.cost = cost
        self.cooldown = cooldown

        self.time_of_placement = time.time() if start_with_cooldown else time.time() - cooldown

        if self.id != "shovel":
            self.width_height = width_height
            self.img = pygame.image.load(f"sprites/{self.id}/{self.id}_seed.png")
            self.slot_img = pygame.image.load(f"sprites/{self.id}/{self.id}_seed_slot.png")
            self.unavailable_img = pygame.image.load(f"sprites/{self.id}/{self.id}_seed_unavailable.png")
        else:
            self.img = pygame.image.load("sprites/shovel.png").convert_alpha()
            self.width_height = [self.img.get_width(), self.img.get_height()]
        self.screen = screen
        self.available = True

        self.follow_mouse = False

        # A transparent surface that will change in size proportional to the amount of time left on the cooldown of the seed
        self.cooldown_rectangle = pygame.Surface((self.width_height[0], self.width_height[1]))
        self.cooldown_rectangle_color = (0, 0, 0)
        self.cooldown_rectangle.set_alpha(100)

        self.cooldown_rectangle.fill(self.cooldown_rectangle_color)

    def draw(self, stored_sun: int):
        if self.id != "shovel":
            self.screen.blit(self.slot_img, self.og_pos)
        if stored_sun >= self.cost and time.time() - self.cooldown > self.time_of_placement and not self.follow_mouse:
            self.screen.blit(self.img, self.pos)
            self.available = True
        else:
            self.available = False
            if stored_sun < self.cost:
                self.screen.blit(self.unavailable_img, self.og_pos)
            if time.time() - self.cooldown < self.time_of_placement:
                self.screen.blit(self.unavailable_img, self.og_pos)

                # Calculate the height of the coodlown rectangle and later blit it to the screen
                time_since_placement = time.time() - self.time_of_placement
                cooldown_percentage = 1 - time_since_placement / self.cooldown

                self.cooldown_rectangle_pos = [self.pos[0], self.pos[1] +
                                               self.width_height[1] - int(cooldown_percentage * self.width_height[1])]
                self.cooldown_rectangle_size = [self.width_height[0], int(cooldown_percentage * self.width_height[1])]
                self.cooldown_rectangle.fill(self.cooldown_rectangle_color)

                self.screen.blit(self.cooldown_rectangle, self.cooldown_rectangle_pos,
                                 (0, 0, self.cooldown_rectangle_size[0], self.cooldown_rectangle_size[1]))

    def is_clicked(self, event: pygame.event.Event):
        if self.is_cursor_hovering() and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.follow_mouse:  # if the seed is following the mouse and we click at it's original place, then put it back
                    self.follow_mouse = False
                elif self.available:
                    self.follow_mouse = True

            elif event.button == 3:  # Right mouse button
                if self.follow_mouse:  # if the seed is following the mouse and we click at it's original place, then put it back
                    self.follow_mouse = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button
                if self.follow_mouse:
                    self.follow_mouse = False

    def place(self):
        self.time_of_placement = time.time()
        self.follow_mouse = False

    def is_cursor_hovering(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.og_pos[0] <= mouse_pos[0] <= self.og_pos[0] + self.width_height[0] and self.og_pos[1] <= mouse_pos[1] <= self.og_pos[1] + self.width_height[1]
