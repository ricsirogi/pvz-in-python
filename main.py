import pygame
import sys
import time
import random
from grid import Grid
import seed
from plants import Pea, Sun
from falling_sun import FallingSun

#! The seed background RGB code is 163 197 137


class App():
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()

        self.SUN_DISPLAY_POS = (10, 10)
        self.SUN_DISPLAY_FONT_SIZE = 30
        self.SUN_DISPLAY_FONT_COLOR = [255, 255, 255]
        self.font = pygame.font.SysFont("Consolas", self.SUN_DISPLAY_FONT_SIZE)

        self.sun_display = self.font.render("50", True, self.SUN_DISPLAY_FONT_COLOR)

        self.running = True

        self.clock = pygame.time.Clock()

        self.id_dict = {"peashooter": Pea, "sunflower": Sun}  # helps with placing down the plants

        self.GRID_COLUMN_ROW = [9, 5]
        self.GRID_CELL_SIZE = [130, 120]
        self.GRID_CELL_COLOR = [0, 0, 0]
        self.GRID_BORDER_COLOR = [255, 255, 255]
        self.GRID_BORDER_SIZE = 3

        self.FALLING_SUN_FALLING_SPEED = 1.6  # How quickly the sun falls
        self.FALLING_SUN_PICKUP_SPEED = 75     # How quickly it gets picked up
        self.FALLING_SUN_STARTING_Y_POS = 200
        self.FALLING_SUN_STARTING_X_POS_RANGE = [150, 1240]
        self.FALLING_SUN_PATH_LENGTH_RANGE = [400, 400]

        self.SHOVEL_POS = [1000, 50]

        self.PEASHOOTER_SEED_POS = [100, 50]
        self.PEASHOOTER_COST = 100
        self.PEASHOOTER_COOLDOWN = 5

        self.SUNFLOWER_COST = 50
        self.SUNFLOWER_COOLDOWN = 3
        self.SUNFLOWER_SEED_POS = [200, 50]

        self.SEED_WIDTH_HEIGHT = [75, 100]
        self.SEED_UNAVAILABLE_COLOR = [255, 0, 0]
        self.SEED_AVAILABLE = True

        self.PEASHOOTER_SEED_AVAILABLE_COLOR = [0, 255, 0]
        self.SUNFLOWER_SEED_AVAILABLE_COLOR = [246, 190, 0]

        size_x = self.GRID_COLUMN_ROW[0] * (
            self.GRID_CELL_SIZE[0] + self.GRID_BORDER_SIZE) + self.GRID_BORDER_SIZE + 200
        size_y = self.GRID_COLUMN_ROW[1] * (
            self.GRID_CELL_SIZE[1] + self.GRID_BORDER_SIZE) + self.GRID_BORDER_SIZE + 300

        self.screen = pygame.display.set_mode((size_x, size_y))
        pygame.display.set_caption("Plants vs Zombies")

        self.grid = Grid((100, 200), self.GRID_COLUMN_ROW, self.GRID_CELL_SIZE, self.GRID_CELL_COLOR,
                         self.GRID_BORDER_COLOR, self.GRID_BORDER_SIZE, self.screen)

        self.peashooter_seed = seed.Seed(self.PEASHOOTER_SEED_POS, self.SEED_WIDTH_HEIGHT, self.PEASHOOTER_SEED_AVAILABLE_COLOR,
                                         self.SEED_UNAVAILABLE_COLOR, self.SEED_AVAILABLE, "peashooter", self.PEASHOOTER_COST, self.PEASHOOTER_COOLDOWN, self.screen)

        self.sunflower_seed = seed.Seed(self.SUNFLOWER_SEED_POS, self.SEED_WIDTH_HEIGHT, self.SUNFLOWER_SEED_AVAILABLE_COLOR,
                                        self.SEED_UNAVAILABLE_COLOR, self.SEED_AVAILABLE, "sunflower", self.SUNFLOWER_COST, self.SUNFLOWER_COOLDOWN, self.screen)

        self.shovel = seed.Seed(self.SHOVEL_POS, self.SEED_WIDTH_HEIGHT, self.SUNFLOWER_SEED_AVAILABLE_COLOR,
                                self.SEED_UNAVAILABLE_COLOR, self.SEED_AVAILABLE, "shovel", 0, 0, self.screen)

        self.seeds = [self.peashooter_seed, self.sunflower_seed, self.shovel]

        self.plants = []

        self.pickable_suns = []  # sun that is able to be picked up

        self.clicked_seed = []  # will add the currently following seed to it, if we click another seed while having one in our hand I'll be able to detect that
        # https://gaming.stackexchange.com/questions/141636/at-what-rate-does-the-sun-generate-in-pvz2#:~:text=The%20sun%20drops%205%20seconds%20after%20the%20game,starts%2C%20it%20then%20regularly%20drop%20every%209%20seconds
        # I read that sun drops every 9 seconds, but it drops 5 seconds after starting the game as well
        # But I'll spice it up and make it random so it drops every 5-9 seconds (very spicy)
        # However, I'll keep the initial 5 seconds as is
        self.next_sun_drop = time.time() + 5
        self.SUN_DROP_RATE_MIN = 5
        self.SUN_DROP_RATE_MAX = 9
        self.stored_sun = 50

        # A list that'll contain bools that are appended to it by different objects that when hovered over make the cursor change into pygame.SYSTEM.CURSOR.HAND
        self.change_cursor = []

    def seeds_draw(self):
        hovering = []  # list of bools where each bool says if the cursor is hovering over a seed packet

        for seed in self.seeds:
            seed.draw(self.stored_sun)

            hovering.append(True if seed.is_cursor_hovering() and seed.available else False)

        if self.clicked_seed == []:  # Only change the cursor to hand if no seed is following the mouse
            self.change_cursor.append(True if True in hovering else False)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def seeds_event_handling(self, event):
        for seed in self.seeds:
            seed.is_clicked(event)
            if seed.follow_mouse:
                if seed not in self.clicked_seed:
                    self.clicked_seed.append(seed)

                # If we click another seed packet while having one already following our mouse, then put back the one in our hand and take out the new one
                if len(self.clicked_seed) > 1:
                    self.clicked_seed[0].reset()
                    self.clicked_seed.pop(0)

                mouse_pos = pygame.mouse.get_pos()
                seed.pos[0] = mouse_pos[0] - int(seed.width_height[0]/2)
                seed.pos[1] = mouse_pos[1] - int(seed.width_height[1]/2)
            elif seed in self.clicked_seed:
                self.clicked_seed = []

    def grid_event_handling(self, event: pygame.event.Event):
        if self.clicked_seed != []:
            if self.grid.border.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                if self.clicked_seed[0].id != "shovel":
                    if event.button == 1:

                        # Place down the plant
                        place_pos = self.grid.find_closest_cell(self.clicked_seed[0].pos)
                        if str(place_pos) not in self.grid.locked_plants:
                            self.plants.append(self.id_dict[self.clicked_seed[0].id](
                                place_pos, self.clicked_seed[0].id, self.screen))
                            self.grid.add_to_grid(place_pos, self.plants[-1])

                            # Put back the seed packet
                            self.clicked_seed[0].place()

                            # Subtract the sun cost
                            self.stored_sun -= self.clicked_seed[0].cost
                            self.sun_display = self.font.render(str(self.stored_sun), True, self.SUN_DISPLAY_FONT_COLOR)
                else:
                    remove_pos = self.grid.find_closest_cell(self.clicked_seed[0].pos)
                    if str(remove_pos) in self.grid.locked_plants:
                        print(self.plants)
                        shoveled_plant = self.grid.locked_plants[str(remove_pos)]
                        self.plants.pop(self.plants.index(shoveled_plant))
                        self.grid.locked_plants.pop(str(remove_pos))
                        del shoveled_plant
                        print(self.plants)

    def grid_draw(self):
        self.grid.draw()

    def plant_stuff(self):
        if self.plants != []:
            for plant in self.plants:
                plant.draw()

    def summon_sun(self, source: str = "sky"):
        self.pickable_suns.append(FallingSun(self.FALLING_SUN_FALLING_SPEED, self.FALLING_SUN_PICKUP_SPEED, self.FALLING_SUN_STARTING_Y_POS,
                                             self.FALLING_SUN_STARTING_X_POS_RANGE, self.FALLING_SUN_PATH_LENGTH_RANGE, self.SUN_DISPLAY_POS, self.screen))

    def sun_draw(self):
        hovering = []
        for sun in self.pickable_suns:
            if not sun.can_delete_me:
                mouse_over_sun = pygame.rect.Rect((sun.x_pos, sun.y_pos), (sun.img.get_width(), sun.img.get_height())
                                                  ).collidepoint(pygame.mouse.get_pos())
                hovering.append(True if mouse_over_sun and not sun.picked_up else False)

                if self.clicked_seed == []:  # Only change the cursor to hand if no seed is following the mouse
                    self.change_cursor.append(True if True in hovering else False)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                sun.draw()
            else:
                self.pickable_suns.pop(self.pickable_suns.index(sun))
                del sun

    def sun_event_handling(self, event):

        for sun in self.pickable_suns:
            mouse_over_sun = pygame.rect.Rect((sun.x_pos, sun.y_pos), (sun.img.get_width(), sun.img.get_height())
                                              ).collidepoint(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_over_sun:
                if event.button == 1:
                    sun.pickup()
                    self.stored_sun += 25
                    self.sun_display = self.font.render(str(self.stored_sun), True, self.SUN_DISPLAY_FONT_COLOR)

        if time.time() > self.next_sun_drop:
            self.summon_sun()
            self.next_sun_drop = time.time() + random.uniform(self.SUN_DROP_RATE_MIN, self.SUN_DROP_RATE_MAX)

    def mainloop(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.summon_sun()
                    if event.key == pygame.K_0:
                        print(pygame.mouse.get_pos())

                self.grid_event_handling(event)

                self.seeds_event_handling(event)

                self.sun_event_handling(event)

            self.screen.fill(self.GRID_CELL_COLOR)

            self.change_cursor = []

            self.grid_draw()

            self.plant_stuff()

            self.seeds_draw()

            self.sun_draw()

            # If the cursor is hovering over an object that makes it turn into hand, then turn it into hand
            if True in self.change_cursor:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            # If there's a seed following the mouse, draw that on top of the other seeds
            if self.clicked_seed != []:
                self.clicked_seed[0].draw(self.stored_sun)

            self.screen.blit(self.sun_display, self.SUN_DISPLAY_POS)

            pygame.display.flip()
            self.clock.tick(75)


if __name__ == "__main__":
    app = App()
    app.mainloop()
