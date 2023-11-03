import pygame
import random


class FallingSun():
    def __init__(self, falling_speed: int, pickup_speed: int, y_pos: int, starting_range: list[int], path_length_range: list[int], collect_destination_cord: tuple[int, int], screen: pygame.Surface) -> None:
        self.falling_speed = falling_speed
        self.pickup_speed = pickup_speed
        self.y_pos = y_pos
        self.x_pos = random.randint(starting_range[0], starting_range[1])
        self.picked_up = False
        self.pickup_destination_cord = collect_destination_cord

        # until which y coordinate the sun should fall
        self.path_length = random.randint(path_length_range[0], path_length_range[1])
        self.screen = screen

        self.pickup_speed = self.real_round(self.pickup_speed * self.x_pos/starting_range[1])

        self.screen = screen

        self.img = pygame.image.load("sprites/falling_sun.png")

        self.pickup_progress = 1
        self.coordinates_towards_destination = []
        self.can_delete_me = False

    def draw(self):
        if not self.picked_up:
            if self.y_pos < self.path_length:
                self.y_pos += self.falling_speed
        elif self.coordinates_towards_destination != [] and self.x_pos > self.pickup_destination_cord[0]:
            self.x_pos = self.coordinates_towards_destination[-self.pickup_progress][0]
            self.y_pos = self.coordinates_towards_destination[-self.pickup_progress][1]
            self.pickup_progress += 1
        elif self.picked_up:
            self.can_delete_me = True

        self.screen.blit(self.img, (self.x_pos, self.y_pos))
        return self.can_delete_me

    def pickup(self):
        """
        calculate the coordinates the sun will have to go through to reach the sun display
        and then make a list of the coordinates it will go through while slowing its speed towards the end like in pvz
        """

        x_difference = abs(self.x_pos - self.pickup_destination_cord[0])
        y_difference = abs(self.y_pos - self.pickup_destination_cord[1])
        self.coordinates_towards_destination = []

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
            self.coordinates_towards_destination.append((x + 10, x * (y_difference/x_difference) + 10))
        self.picked_up = True

        print(self.coordinates_towards_destination)

    def real_round(self, number: float) -> int:
        """
        scuffed rounding
        """

        if number == int(number):
            return int(number)
        # print("checking the number:", number, "->", str(number/10)[3])
        if int(str(number/10)[3]) < 6:
            return int(number)
        else:
            return int(number) + 1
