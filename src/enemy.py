import arcade
import random
from src.constants import SCREEN_WIDTH, ENEMY_SPEED


class Enemy:
    def __init__(self):
        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = SCREEN_HEIGHT + 50
        self.width = 30
        self.height = 30
        self.speed = ENEMY_SPEED
        self.hp = 1
        self.is_alive = True
        self.color = (255, 50, 150)

    def update(self, delta_time):
        self.center_y -= self.speed

    def draw(self):
        arcade.draw_rectangle_filled(
            self.center_x, self.center_y,
            self.width, self.height,
            self.color
        )

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.is_alive = False
        return not self.is_alive