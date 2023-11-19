import pygame
import random
import json


class Zombie():
    def __init__(self) -> None:
        with open("config.json", "r") as f:
            self.config = json.load(f)["zombie"]

        self.health = self.config["health"]
        self.speed = random.randint(self.config["speed_range"][0], self.config["speed_range"][1])
        self.attack_speed = self.config["attack_speed"]
        self.starting_pos = self.config["starting_poses"][random.randint(0, 4)]
