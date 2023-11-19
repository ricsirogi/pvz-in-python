import pygame
import pygame.surfarray as surfarray
import numpy as np
import sys
import time
import random
from typing import List, Optional, Union
from grid import Grid
from seed import Seed
from plants import Peashooter, Sunflower
from falling_sun import FallingSun
import os

#! The seed background RGB code is 163 197 137
#! What to fix:
#!              This bullshit :/


class App():
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.FRAME_RATE = 75

        self.SUN_DISPLAY_POS = (10, 10)
        self.SUN_DISPLAY_FONT_SIZE = 30
        self.SUN_DISPLAY_FONT_COLOR = [255, 255, 255]
        self.font = pygame.font.SysFont("Consolas", self.SUN_DISPLAY_FONT_SIZE)

        self.sun_display = self.font.render("50", True, self.SUN_DISPLAY_FONT_COLOR)

        self.running = True

        self.clock = pygame.time.Clock()

        self.id_dict = {"peashooter": Peashooter, "sunflower": Sunflower}  # helps with placing down the plants

        self.GRID_COLUMN_ROW = [9, 5]
        self.GRID_CELL_SIZE = [130, 120]
        self.GRID_CELL_COLOR_A = [2, 119, 16]
        self.GRID_CELL_COLOR_B = [2, 138, 22]
        self.GRID_BORDER_COLOR = [255, 255, 255]
        self.GRID_BORDER_SIZE = 3
        self.BACKGROUND_COLOR = [218, 207, 183]
        self.FALLING_SUN_FALLING_SPEED = 1.6 if self.FRAME_RATE == 75 else 1.6 * \
            (75/self.FRAME_RATE)  # How quickly the sun falls
        self.FALLING_SUN_SPAWNING_SPEED = 1 if self.FRAME_RATE == 75 else int(
            1 * (75/self.FRAME_RATE))  # How quickly the sun spawns if it comes from a sunflower
        self.FALLING_SUN_PICKUP_SPEED = 75 if self.FRAME_RATE == 75 else int(
            75 * (75/self.FRAME_RATE))    # How quickly it gets picked up
        self.FALLING_SUN_STARTING_Y_POS = 200
        self.FALLING_SUN_STARTING_X_POS_RANGE = [150, 1240]
        self.FALLING_SUN_PATH_LENGTH_RANGE = [400, 600]

        self.SHOVEL_POS = [1000, 50]

        self.PEASHOOTER_SEED_POS = [100, 50]
        self.PEASHOOTER_COST = 100
        self.PEASHOOTER_COOLDOWN = 5

        self.SUNFLOWER_COST = 50
        self.SUNFLOWER_COOLDOWN = 3
        self.SUNFLOWER_SEED_POS = [200, 50]

        self.SEED_WIDTH_HEIGHT = [75, 100]

        self.PEASHOOTER_SEED_AVAILABLE_COLOR = [0, 255, 0]
        self.SUNFLOWER_SEED_AVAILABLE_COLOR = [246, 190, 0]

        self.SHOVEL_BRIGTNESS_CHANGE = 40

        size_x = self.GRID_COLUMN_ROW[0] * (
            self.GRID_CELL_SIZE[0] + self.GRID_BORDER_SIZE) + self.GRID_BORDER_SIZE + 200
        size_y = self.GRID_COLUMN_ROW[1] * (
            self.GRID_CELL_SIZE[1] + self.GRID_BORDER_SIZE) + self.GRID_BORDER_SIZE + 300

        self.screen = pygame.display.set_mode((size_x, size_y))
        pygame.display.set_caption("Plants vs Zombies")

        self.grid = Grid((100, 200), self.GRID_COLUMN_ROW, self.GRID_CELL_SIZE, self.GRID_CELL_COLOR_A, self.GRID_CELL_COLOR_B,
                         self.GRID_BORDER_COLOR, self.GRID_BORDER_SIZE, self.screen)

        self.peashooter_seed = Seed(self.PEASHOOTER_SEED_POS, self.SEED_WIDTH_HEIGHT,
                                    "peashooter", self.PEASHOOTER_COST, self.PEASHOOTER_COOLDOWN, False, self.screen)

        self.sunflower_seed = Seed(self.SUNFLOWER_SEED_POS, self.SEED_WIDTH_HEIGHT, "sunflower",
                                   self.SUNFLOWER_COST, self.SUNFLOWER_COOLDOWN, False, self.screen)

        self.shovel = Seed(self.SHOVEL_POS, self.SEED_WIDTH_HEIGHT, "shovel", 0, 0, False, self.screen)

        self.seeds = [self.peashooter_seed, self.sunflower_seed, self.shovel]

        self.plants = []

        self.pickable_suns = []  # sun that is able to be picked up

        # will add the currently following seed to it, if we click another seed while having one in our hand I'll be able to detect that
        self.clicked_seed: List[Seed] = []

        # The picture of the plant that is following the mouse when a seed is held and its position
        self.following_plant: Optional[pygame.Surface] = None
        self.following_plant_pos: list = [0, 0]

        # The position where the nearest plant space is to the mouse, if a seed is following the mouse
        # The img that will be displayed on the grid and will be used to show where the plant will be placed
        self.ghost_plant_pos: Optional[tuple[int, int]] = None
        self.ghost_plant_img: Optional[pygame.Surface] = None
        self.GHOST_PLANT_ALPHA = 150

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
            if seed.id != "shovel":
                seed.draw(self.stored_sun)
            elif self.clicked_seed == [] or self.clicked_seed[0].id != "shovel":
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
                    self.clicked_seed[0].follow_mouse = False
                    self.clicked_seed.pop(0)

                if seed.id != "shovel":
                    self.following_plant = pygame.image.load(
                        "sprites/" + seed.id + "/" + seed.id + ".png").convert_alpha()
                else:
                    self.following_plant = pygame.image.load("sprites/" + seed.id + ".png").convert_alpha()

                mouse_pos = pygame.mouse.get_pos()
                self.following_plant_pos[0] = mouse_pos[0] - int(seed.width_height[0]/2)
                self.following_plant_pos[1] = mouse_pos[1] - int(seed.width_height[1]/2)
            elif seed in self.clicked_seed:
                self.clicked_seed = []
        if self.clicked_seed == []:
            self.following_plant = None

    def grid_event_handling(self, event: pygame.event.Event):
        if self.clicked_seed != []:
            if self.grid.border.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                if self.clicked_seed[0].id != "shovel":
                    if event.button == 1:

                        # Place down the plant
                        place_pos = self.grid.find_closest_cell(self.following_plant_pos)
                        if str(place_pos) not in self.grid.locked_plants:  # self.grid.locked_plants is a dict where the keys are coordinates
                            self.plants.append(self.id_dict[self.clicked_seed[0].id](
                                place_pos, self.clicked_seed[0].id, self.screen))
                            self.grid.add_to_grid(place_pos, self.plants[-1])

                            # Subtract the sun cost
                            self.stored_sun -= self.clicked_seed[0].cost
                            self.sun_display = self.font.render(str(self.stored_sun), True, self.SUN_DISPLAY_FONT_COLOR)

                            # Put back the seed packet
                            self.clicked_seed[0].place()
                            self.clicked_seed = []
                else:
                    # If we click on a plant with the shovel, then remove it
                    # If we click on an empty cell with the shovel, then place back the shovel
                    remove_pos = self.grid.find_closest_cell(self.following_plant_pos)
                    if str(remove_pos) in self.grid.locked_plants:
                        shoveled_plant = self.grid.locked_plants[str(remove_pos)]
                        self.plants.pop(self.plants.index(shoveled_plant))
                        self.grid.locked_plants.pop(str(remove_pos))
                        del shoveled_plant
                    self.clicked_seed[0].follow_mouse = False
            elif self.grid.border.collidepoint(pygame.mouse.get_pos()):
                # get the closest cell to the mouse position
                try_pos = self.grid.find_closest_cell(self.following_plant_pos)

                if self.clicked_seed[0].id != "shovel":
                    # make the ghost plant follow the try_pos if there's no plant there
                    if str(try_pos) not in self.grid.locked_plants:
                        if self.ghost_plant_pos != try_pos:
                            self.ghost_plant_pos = try_pos
                    else:  # if there is a plant in that cell, then don't show the ghost plant
                        self.ghost_plant_pos = None
            else:  # if the mouse is not hovering over the grid, then don't show the ghost plant
                self.ghost_plant_pos = None
        else:  # if no seed is following the mouse, then don't show the ghost plant
            self.ghost_plant_pos = None

    def grid_draw(self):
        self.grid.draw()

    def plant_stuff(self):
        if self.plants != []:
            for plant in self.plants:
                plant.draw()

                # Handle the sunflower's sun dropping
                if isinstance(plant, self.id_dict["sunflower"]):
                    if plant.time_of_last_drop + plant.cooldown < time.time():
                        self.summon_sun("sunflower", plant.pos)
                        plant.time_of_last_drop = time.time()
        if self.ghost_plant_pos != None and self.clicked_seed != []:
            # set the ghost_plant_img to the currently held seed's image
            if self.ghost_plant_img == None:
                self.ghost_plant_img = pygame.image.load(
                    f"sprites/{self.clicked_seed[0].id}/{self.clicked_seed[0].id}.png").convert_alpha()
                self.ghost_plant_img.set_alpha(self.GHOST_PLANT_ALPHA)

            self.screen.blit(self.ghost_plant_img, self.ghost_plant_pos)
        else:
            self.ghost_plant_img = None

    def summon_sun(self, source: str = "sky", start_pos: tuple[int, int] = (0, 0)):
        if source == "sky":
            self.pickable_suns.append(FallingSun(self.FALLING_SUN_FALLING_SPEED, self.FALLING_SUN_PICKUP_SPEED, self.FALLING_SUN_STARTING_Y_POS,
                                                 self.FALLING_SUN_STARTING_X_POS_RANGE, self.FALLING_SUN_PATH_LENGTH_RANGE, self.SUN_DISPLAY_POS, source, self.screen))
        elif source == "sunflower":
            self.pickable_suns.append(FallingSun(self.FALLING_SUN_SPAWNING_SPEED, self.FALLING_SUN_PICKUP_SPEED, start_pos[1],
                                                 self.FALLING_SUN_STARTING_X_POS_RANGE, self.FALLING_SUN_PATH_LENGTH_RANGE, self.SUN_DISPLAY_POS, source, self.screen, start_pos[0]))

    def sun_draw(self):
        hovering = []
        new_pickable_suns = []
        for sun in self.pickable_suns:
            if not sun.can_delete_me:
                mouse_over_sun = pygame.rect.Rect((sun.x_pos, sun.y_pos), (sun.img.get_width(), sun.img.get_height())
                                                  ).collidepoint(pygame.mouse.get_pos())
                hovering.append(True if mouse_over_sun and not sun.picked_up else False)
                sun.draw()
                new_pickable_suns.append(sun)
            else:
                del sun
        if self.clicked_seed == []:  # Only change the cursor to hand if no seed is following the mouse
            self.change_cursor.append(True if True in hovering else False)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.pickable_suns = new_pickable_suns

    def sun_event_handling(self, event):
        picked_up = False
        for sun in self.pickable_suns:
            mouse_over_sun = pygame.rect.Rect((sun.x_pos, sun.y_pos), (sun.img.get_width(), sun.img.get_height())
                                              ).collidepoint(pygame.mouse.get_pos())
            if (not self.clicked_seed) and event.type == pygame.MOUSEBUTTONDOWN and mouse_over_sun:
                if event.button == 1 and not picked_up:
                    sun.pickup()
                    self.stored_sun += 25
                    self.sun_display = self.font.render(str(self.stored_sun), True, self.SUN_DISPLAY_FONT_COLOR)
                    picked_up = True

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

                self.seeds_event_handling(event)

                self.sun_event_handling(event)

                self.grid_event_handling(event)

            self.screen.fill(self.BACKGROUND_COLOR)

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

            self.screen.blit(self.sun_display, self.SUN_DISPLAY_POS)

            if self.following_plant != None and self.clicked_seed != []:
                self.screen.blit(self.following_plant, self.following_plant_pos)

            pygame.display.flip()
            self.clock.tick(self.FRAME_RATE)


if __name__ == "__main__":
    os.chdir(__file__.rstrip("main.py"))
    app = App()
    app.mainloop()
