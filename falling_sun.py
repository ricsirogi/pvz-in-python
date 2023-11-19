import pygame
import random
import numpy as np
import math
import time


class FallingSun():
    def __init__(self, falling_speed: float, pickup_speed: int, y_pos: int, starting_range: list[int], path_length_range: list[int], collect_destination_cord: tuple[int, int], source: str, screen: pygame.Surface, x_pos: int = -1) -> None:
        self.lifespan = 8  # How long the sun will stay on the screen in seconds (I tested it out in game)
        self.start_of_life = time.time()

        self.falling_speed = falling_speed
        self.pickup_speed = pickup_speed
        self.y_pos = y_pos
        self.x_pos = random.randint(starting_range[0], starting_range[1]) if source == "sky" else x_pos
        self.picked_up = False
        self.pickup_destination_cord = collect_destination_cord
        self.starting_range = starting_range
        # until which y coordinate the sun should fall
        self.path_length = random.randint(path_length_range[0], path_length_range[1])
        self.source = source
        self.screen = screen

        self.pickup_speed = self.real_round(self.pickup_speed * self.x_pos/starting_range[1])

        # this is the original image, it will be scaled down if the source is sunflower
        # it's better than scaling an image that was alreasdy scaled down before
        self.original_img = pygame.image.load("sprites/falling_sun.png").convert_alpha()
        self.original_img = pygame.transform.scale(self.original_img, (self.original_img.get_width()
                                                                       * 0.9, self.original_img.get_height() * 0.9))
        self.original_img.set_alpha(230)
        self.img = pygame.transform.scale(self.original_img, (self.original_img.get_width()
                                          * 0.3, self.original_img.get_height() * 0.3)) if source == "sunflower" else self.original_img

        self.pickup_progress = 1  # the pickup progress starts with 1 because the coordinates are generated backwards and the last coordinate in the list is the first one it should go to
        self.coordinates_towards_destination = []  # The list of coordinates the sun will go through to reach its animation's end point
        self.can_delete_me = False  # If the sun is picked up and it reached its destination, then it can be deleted

        # If the source is "sky" then the next 2 won't be used
        self.spawn_progress = 0
        self.coordinates_towards_spawn_destionation = []
        self.spawn_destination = -1

        if source == "sunflower":
            self.get_spawn_path()

    def draw(self):
        if not self.picked_up:
            if self.source == "sky":
                if self.y_pos < self.path_length:
                    self.y_pos += self.falling_speed
            elif self.source == "sunflower" and self.coordinates_towards_spawn_destionation != [] and self.spawn_progress < len(self.coordinates_towards_spawn_destionation):
                self.scale_spawning_sun()
                self.x_pos = self.coordinates_towards_spawn_destionation[self.spawn_progress][0]
                self.y_pos = self.coordinates_towards_spawn_destionation[self.spawn_progress][1]
                self.spawn_progress += 1

            # Safety net if for some reason the animation is shorter than 10 frames
            elif self.source == "sunflower" and self.spawn_progress == len(self.coordinates_towards_spawn_destionation):
                if self.img.get_width() != self.original_img.get_width():
                    self.img = self.original_img.copy()
        elif self.coordinates_towards_destination != [] and self.x_pos > self.pickup_destination_cord[0]:
            self.x_pos = self.coordinates_towards_destination[-self.pickup_progress][0]
            self.y_pos = self.coordinates_towards_destination[-self.pickup_progress][1]
            self.pickup_progress += 1
        elif self.picked_up:
            self.can_delete_me = True

        if self.start_of_life + self.lifespan < time.time():
            self.can_delete_me = True
        self.screen.blit(self.img, (self.x_pos, self.y_pos))
        return self.can_delete_me

    def scale_spawning_sun(self):
        """
        Scale the spawning sun to make it look like it's coming out of the sunflower
        The size is getting bigger progressively and reaches it's original size at the 10th frame
        """
        if self.spawn_progress < 11:
            scale_factor = 0.37 + 0.07 * (self.spawn_progress - 1)
            self.img = pygame.transform.scale(
                self.original_img,
                (int(self.original_img.get_width() * scale_factor), int(self.original_img.get_height() * scale_factor))
            )

    def pickup(self):
        """
        calculate the coordinates the sun will have to go through to reach its animation's end point
        and then make a list of the coordinates it will go through while slowing its speed towards the end like in pvz
        """
        self.coordinates_towards_destination = []
        x_difference = abs(self.x_pos - self.pickup_destination_cord[0])
        y_difference = abs(self.y_pos - self.pickup_destination_cord[1])

        for x in range(x_difference):
            # For the first 80% of the way add every self.speed"th" (right now 5th) coordinate to the list
            # But we have to flip it because the first 20% of the list is the last 20% of the "journey" of the sun
            # This means that the basic speed will be every self.speed"th" coord and it will get slower from there

            # Gradually slow down
            if x < x_difference * 0.1:
                if x % self.real_round(self.pickup_speed * 0.1) != 0:
                    continue
            elif x_difference * 0.1 < x < x_difference * 0.2:
                if x % self.real_round(self.pickup_speed * 0.3) != 0:
                    continue
            elif x_difference * 0.2 < x < x_difference * 0.25:
                if x % self.real_round(self.pickup_speed * 0.5) != 0:
                    continue
            elif x_difference * 0.25 < x < x_difference * 0.35:
                if x % self.real_round(self.pickup_speed * 0.7) != 0:
                    continue
            elif x_difference * 0.35 < x < x_difference * 0.45:
                if x % self.real_round(self.pickup_speed * 0.9) != 0:
                    continue
            # This is the default speed
            else:
                if x % self.pickup_speed != 0:
                    continue

            # The destination is not in the corner but it's a bit off so I account to that by adding self.pickup_destination_cord[0 or 1]
            # Sorry for hungarian explaination but I can't explain this in english
            # x * (y_difference/x_difference) + 10 Magyarázata:
            # Az alábbi sorban az append()-en belül igazából egy függvénynek a hozzárendelési szabálya látható, amikor az y-t adom meg
            # y = m*x + b =(a b-t elhagyjuk, mert nem transzformáltuk a függvényt az y koordinátán)=> y = m*x
            # m - meredekség, ami jelenleg y_difference/x_difference
            self.coordinates_towards_destination.append(
                (x + self.pickup_destination_cord[0], x * (y_difference/x_difference) + self.pickup_destination_cord[1]))
        self.picked_up = True

    def get_spawn_path(self):
        """
        start_point:
            x coordinate is the current x position + the half of self.img's width 
            y coordinate is y_pos
        end_point: 
            x coordinate is adding randint(-50, 50) to x_pos
            y coordinate is adding self.img's height plus randint(-20, 20) to y_pos
        control_y:  the y coordinate of control point
                    value is between y_pos and y_pos + 20
        control_point: 
            x coordinate is between start and end point's x coordinate
            y coordinate is control_y
        path: the list of coordinates the sun will go through throughout its path
        """

        start_point = (self.x_pos + self.real_round(self.img.get_width()/2), self.y_pos + 5)

        end_point = [start_point[0] + random.randint(-60, 60), self.y_pos +
                     self.img.get_height() + random.randint(-10, 15)]
        margin = 30
        if -margin < abs(end_point[0] - start_point[0]) < margin:
            end_point[0] += margin if end_point[0] >= 0 else -margin

        self.spawn_destination = end_point

        control_y = random.randint(start_point[1] - self.img.get_height()*4, start_point[1])
        if start_point[0] + self.img.get_width() < end_point[0]:
            control_point = (start_point[0] + int((end_point[0] - start_point[0]) / 2), control_y)
        else:
            control_point = (start_point[0] - int((start_point[0] - end_point[0]) / 2), control_y)

        path = self.calculate_curve_points(start_point, control_point, end_point)

        for count, coordinate in enumerate(path):
            # If the source of the sun is a sunflower, than falling speed will be self.FALLING_SUN_SPAWNING_SPEED from main.py instead of FALLING_SPEED
            if count % (1 if len(path) < 21 else 2) != 0:
                continue
            self.coordinates_towards_spawn_destionation.append(coordinate)
        if len(self.coordinates_towards_spawn_destionation) < 11:
            print("not what this guy says")

    def quadratic_bezier(self, t, p0, p1, p2):
        return self.real_round((1-t)**2 * p0 + 2 * (1-t) * t * p1 + t**2 * p2)

    def calculate_curve_points(self, p0: tuple[int, int], p1: tuple[int, int], p2: list[int]) -> list[tuple[int, int]]:
        """

        Args:
            p0 (tuple[int, int]): Starting point
            p1 (tuple[int, int]): Control point
            p2 (list[int]): Ending point (It asks for a list instead of a tuple because I'm changing end_point and that cause issues)

        Returns:
            list[tuple[int, int]]: A list of coordinates that the sun will have to go through throughout its path
        """
        a = abs(p0[0] - p2[0])
        b = abs(p0[1] - p2[1])

        # Get the distance between the start position and the end position
        # It will be the amount of coordinates that the sun will go through throughout its path
        num_points = self.real_round(math.sqrt(a ** 2 + b ** 2))

        t_values = np.linspace(0, 1, num_points)
        curve_points = [(self.quadratic_bezier(t, p0[0], p1[0], p2[0]),
                         self.quadratic_bezier(t, p0[1], p1[1], p2[1])) for t in t_values]

        return curve_points

    def real_round(self, number: float) -> int:
        """
        scuffed rounding
        """

        if int(str(number)[str(number).find(".") + 1]) < 5:
            number = int(number)
        else:
            number = int(number) + 1
        return number
