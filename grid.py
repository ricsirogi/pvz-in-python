import pygame
import math
import numpy as np


class Grid(object):
    def __init__(self, pos: tuple[int, int], column_row: list[int], cell_size: list[int], cell_color_a: list[int], cell_color_b: list[int], border_color: list[int], border_size: int, screen: pygame.Surface):
        self.column_row = column_row  # I know that it's supposed to be row and then column but the code flips it around and idk how to fix it
        self.cell_size = cell_size
        self.cell_color_a = cell_color_a
        self.cell_color_b = cell_color_b
        self.border_color = border_color
        self.border_size = border_size
        self.pos = pos
        self.x_positions = []
        self.y_positions = []
        self.all_positions = []
        self.cells = []
        self.screen = screen
        self.locked_plants = {}
        self.returned_value = None
        self.was_clicked = False

        border_width = self.cell_size[0] * self.column_row[0] + \
            (self.column_row[0] + 1) * self.border_size
        border_height = self.cell_size[1] * self.column_row[1] + \
            (self.column_row[1] + 1) * self.border_size

        self.border = pygame.Rect(
            (self.pos), (border_width, border_height))

        for i in range(self.column_row[1]):
            self.cells.append([])
            pos_y = self.pos[1] + self.cell_size[1] * i + \
                self.border_size * i + self.border_size
            if pos_y not in self.y_positions:
                self.y_positions.append(pos_y)

            for j in range(self.column_row[0]):
                pos_x = self.pos[0] + self.cell_size[0] * j + \
                    self.border_size * j + self.border_size
                if pos_x not in self.x_positions:
                    self.x_positions.append(pos_x)
                self.cells[i].append(pygame.Rect(
                    (pos_x, pos_y), self.cell_size))

        for y in range(self.column_row[1]):
            self.all_positions.append([])
            for x in range(self.column_row[0]):
                self.all_positions[y].append(
                    (self.x_positions[x], self.y_positions[y]))

    def remove_from_grid(self, cord: list[int]):
        self.locked_plants.pop(str(cord))

    def add_to_grid(self, cord, plant):
        self.locked_plants[str(cord)] = plant

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

    def find_closest_cell(self, pos_in_question):
        smallest_distance = 9999
        smallest_distance_cell_cord = (0, 0)
        for cell_num_y, position_y in enumerate(self.all_positions):
            for cell_num_x, position_x in enumerate(position_y):
                x = abs(position_x[0] - pos_in_question[0])
                y = abs(position_x[1] - pos_in_question[1])

                dist = math.sqrt(x ** 2 + y ** 2)

                if dist < smallest_distance:
                    smallest_distance = dist
                    smallest_distance_cell_cord = (cell_num_y, cell_num_x)

        return self.all_positions[smallest_distance_cell_cord[0]][smallest_distance_cell_cord[1]]

    def draw(self):
        pygame.draw.rect(self.screen, self.border_color, self.border)
        for y_count, y in enumerate(self.cells):
            for x_count, x in enumerate(y):
                if y_count % 2 == 0:
                    color = self.cell_color_a if x_count % 2 == 0 else self.cell_color_b
                else:
                    color = self.cell_color_a if x_count % 2 == 1 else self.cell_color_b
                pygame.draw.rect(self.screen, color, x)

    def __del__(self):
        pass
