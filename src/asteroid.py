import arcade
import random
from src.constants import SCREEN_WIDTH


class Asteroid:
    def __init__(self):
        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = SCREEN_HEIGHT + 50
        self.width = 40
        self.height = 40
        self.speed = random.uniform(1.0, 3.0)
        self.hp = 2
        self.is_alive = True
        self.color = (150, 150, 150)

    def update(self, delta_time):
        self.center_y -= self.speed

    def draw(self):
        arcade.draw_circle_filled(
            self.center_x, self.center_y,
            self.width // 2,
            self.color
        )

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.is_alive = False
        return not self.is_alive