"""
Класс пули/лазера
"""

import arcade
from src.constants import BULLET_SPEED, SCREEN_HEIGHT

class Bullet:
    """Класс пули/лазера"""

    def __init__(self, x, y, speed=None, is_super=False):
        """
        Инициализация пули

        Args:
            x: Позиция по X
            y: Позиция по Y
            speed: Скорость пули (если None, берется из BULLET_SPEED)
            is_super: Является ли супер-пулей
        """
        self.center_x = x
        self.center_y = y
        self.speed = speed if speed is not None else BULLET_SPEED
        self.is_super = is_super
        self.active = True
        self.damage = 3 if is_super else 1  # Супер-пуля наносит больше урона
        self.width = 4 if is_super else 2   # Ширина пули
        self.height = 20 if is_super else 15 # Высота пули

        # Цвета
        if is_super:
            self.color = (255, 255, 0)    # Желтый для супер-пули
            self.glow_color = (255, 255, 200, 100)  # Светящийся эффект
        else:
            self.color = (255, 50, 50)    # Красный для обычной пули
            self.glow_color = (255, 100, 100, 50)   # Слабый светящийся эффект

        # Для супер-пули увеличиваем скорость
        if is_super:
            self.speed *= 1.5

    def update(self, delta_time):
        """Обновляет позицию пули"""
        self.center_y += self.speed

        # Деактивируем если вышла за экран
        if self.center_y > SCREEN_HEIGHT + 50:
            self.active = False

    def draw(self):
        """Рисует пулю"""
        # Основной корпус пули
        arcade.draw_rectangle_filled(
            self.center_x, self.center_y,
            self.width, self.height,
            self.color
        )

        # Эффект свечения (особенно для супер-пули)
        arcade.draw_rectangle_filled(
            self.center_x, self.center_y,
            self.width + 2, self.height + 4,
            self.glow_color
        )

        # Носок пули (ярче)
        if self.is_super:
            arcade.draw_rectangle_filled(
                self.center_x, self.center_y + self.height/2,
                self.width - 1, 3,
                (255, 255, 200)
            )
        else:
            arcade.draw_rectangle_filled(
                self.center_x, self.center_y + self.height/2,
                self.width - 1, 2,
                (255, 150, 150)
            )

    def check_collision(self, enemy):
        """Проверяет столкновение с врагом"""
        # Простая проверка AABB (Axis-Aligned Bounding Box)
        enemy_left = enemy.center_x - enemy.width/2
        enemy_right = enemy.center_x + enemy.width/2
        enemy_bottom = enemy.center_y - enemy.height/2
        enemy_top = enemy.center_y + enemy.height/2

        bullet_left = self.center_x - self.width/2
        bullet_right = self.center_x + self.width/2
        bullet_bottom = self.center_y - self.height/2
        bullet_top = self.center_y + self.height/2

        return (bullet_left < enemy_right and
                bullet_right > enemy_left and
                bullet_bottom < enemy_top and
                bullet_top > enemy_bottom)

    def on_hit(self):
        """Вызывается при попадании"""
        self.active = False
        return self.damage