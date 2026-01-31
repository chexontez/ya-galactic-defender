"""
Класс игрока (космического корабля)
"""

import arcade
import time

from src.bullet import Bullet
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED


class Player(arcade.Sprite):
    """Класс космического корабля игрока"""

    def __init__(self):
        # Вызываем конструктор родительского класса
        super().__init__()

        # Основные характеристики
        self.center_x = SCREEN_WIDTH // 2  # Начальная позиция по X
        self.center_y = 50  # Начальная позиция по Y (внизу)
        self.scale = 0.5  # Масштаб спрайта
        self.speed = PLAYER_SPEED  # Скорость движения

        # Здоровье
        self.max_hp = 5
        self.hp = self.max_hp
        self.is_alive = True

        # Стрельба
        self.bullets = []  # Список активных пуль
        self.can_shoot = True  # Может ли стрелять сейчас
        self.shoot_cooldown = 0.3  # КД между выстрелами (сек)
        self.last_shot_time = 0  # Время последнего выстрела

        # Система перегрева оружия
        self.heat = 0  # Текущий перегрев (0-100)
        self.max_heat = 100  # Максимальный перегрев
        self.heat_per_shot = 15  # Нагрев за выстрел
        self.cooling_rate = 8  # Скорость остывания в секунду
        self.overheated = False  # Перегрето ли оружие
        self.overheat_threshold = 80  # Порог перегрева

        # Супер-выстрел
        self.super_shot_ready = True  # Доступен ли супер-выстрел
        self.super_shot_cooldown = 25  # КД супер-выстрела (сек)
        self.super_shot_timer = 0  # Таймер перезарядки
        self.super_shot_charge = 0  # Заряд супер-выстрела (0-100)
        self.charge_rate = 100 / 25  # Скорость заряда в секунду

        # Анимации и визуальные эффекты
        self.hit_flash_timer = 0  # Таймер мигания при получении урона
        self.overheat_flash_timer = 0  # Таймер мигания при перегреве

        # Загрузка текстур
        self.load_textures()

    def load_textures(self):
        """Загружает или создает текстуры корабля"""
        try:
            # Пробуем загрузить изображение
            self.texture = arcade.load_texture("assets/images/player.png")
            print("✓ Текстура игрока загружена")
        except FileNotFoundError:
            # Создаем временную текстуру (треугольник)
            print("⚠ Текстура игрока не найдена, создается временная")
            self.create_temp_texture()

    def create_temp_texture(self):
        """Создает временную текстуру треугольника"""
        # Создаем изображение для треугольника
        width = 50
        height = 60

        texture = arcade.Texture.create_empty(f"player_temp", (width, height))
        self.texture = texture

        # Примечание: Временная графика будет нарисована в методе draw()

    def draw(self):
        """Отрисовка игрока с дополнительными эффектами"""
        # Отрисовка базового спрайта
        super().draw()

        # Если нет текстуры, рисуем треугольник
        if self.texture.size == (1, 1):  # Проверка на пустую текстуру
            self.draw_triangle()

        # Эффект мигания при получении урона
        if self.hit_flash_timer > 0:
            self.draw_hit_effect()

        # Индикатор перегрева
        if self.heat > 0:
            self.draw_heat_indicator()

        # Индикатор супер-выстрела
        self.draw_super_shot_indicator()

        # Индикатор здоровья
        self.draw_health_bar()

        for bullet in self.bullets:
            bullet.draw()

    def draw_triangle(self):
        """Рисует треугольный корабль"""
        # Треугольник направленный вверх
        point_list = (
            (self.center_x, self.center_y + 30),  # Верхняя точка (нос)
            (self.center_x - 25, self.center_y - 20),  # Левая нижняя
            (self.center_x + 25, self.center_y - 20)  # Правая нижняя
        )

        # Цвет зависит от перегрева
        if self.overheated:
            color = (255, 100, 100)  # Красный при перегреве
        elif self.heat > 50:
            color = (255, 200, 100)  # Оранжевый при нагреве
        else:
            color = (100, 150, 255)  # Синий в нормальном состоянии

        arcade.draw_polygon_filled(point_list, color)

        # Контур
        arcade.draw_polygon_outline(point_list, (255, 255, 255), 2)

    def draw_hit_effect(self):
        """Рисует эффект получения урона"""
        alpha = int(150 * (self.hit_flash_timer / 0.3))
        arcade.draw_circle_filled(
            self.center_x, self.center_y,
            40, (255, 50, 50, alpha)
        )

    def draw_heat_indicator(self):
        """Рисует индикатор перегрева"""
        # Фон индикатора
        bar_width = 60
        bar_height = 6
        x = self.center_x - bar_width // 2
        y = self.center_y - 40

        arcade.draw_rectangle_filled(
            x + bar_width // 2, y,
            bar_width, bar_height,
            (50, 50, 50)
        )

        # Заполненная часть
        fill_width = bar_width * (self.heat / 100)
        color = (
            255,  # R увеличивается с нагревом
            int(255 * (1 - self.heat / 100)),  # G уменьшается
            50  # B постоянный
        )

        arcade.draw_rectangle_filled(
            x + fill_width // 2, y,
            fill_width, bar_height,
            color
        )

        # Текст перегрева
        if self.overheated:
            arcade.draw_text(
                "ПЕРЕГРЕВ!",
                self.center_x, y - 15,
                (255, 50, 50), 10,
                anchor_x="center"
            )

    def draw_super_shot_indicator(self):
        """Рисует индикатор супер-выстрела"""
        # Круговая шкала заряда
        radius = 20
        x = self.center_x
        y = self.center_y - 60

        # Фон
        arcade.draw_circle_outline(x, y, radius, (100, 100, 100), 2)

        if self.super_shot_ready:
            # Готов - зеленый заполненный круг
            arcade.draw_circle_filled(x, y, radius - 2, (50, 255, 100))
            arcade.draw_text("S", x, y, (0, 0, 0), 12, anchor_x="center", anchor_y="center")
        else:
            # Заряжается - частично заполненный круг
            angle = 360 * (self.super_shot_charge / 100)
            arcade.draw_arc_filled(
                x, y, radius - 2,
                (50, 200, 255), 0, angle
            )
            # Процент заряда
            arcade.draw_text(
                f"{int(self.super_shot_charge)}%",
                x, y, (255, 255, 255), 10,
                anchor_x="center", anchor_y="center"
            )

    def draw_health_bar(self):
        """Рисует полоску здоровья"""
        bar_width = 60
        bar_height = 8
        x = self.center_x - bar_width // 2
        y = self.center_y + 45

        # Фон
        arcade.draw_rectangle_filled(
            x + bar_width // 2, y,
            bar_width, bar_height,
            (50, 50, 50)
        )

        # Здоровье
        health_width = bar_width * (self.hp / self.max_hp)
        health_color = (
            int(255 * (1 - self.hp / self.max_hp)),  # R увеличивается при малом HP
            int(255 * (self.hp / self.max_hp)),  # G уменьшается
            50
        )

        arcade.draw_rectangle_filled(
            x + health_width // 2, y,
            health_width, bar_height,
            health_color
        )

        # Текст здоровья
        arcade.draw_text(
            f"HP: {self.hp}/{self.max_hp}",
            x + bar_width // 2, y + 10,
            (255, 255, 255), 10,
            anchor_x="center"
        )

    def update(self, delta_time):
        """Обновляет состояние игрока"""
        if not self.is_alive:
            return

        # Обновляем таймеры
        current_time = time.time()

        # Обработка перезарядки выстрела
        if not self.can_shoot and current_time - self.last_shot_time > self.shoot_cooldown:
            self.can_shoot = True

        # Охлаждение оружия
        if self.heat > 0:
            self.heat -= self.cooling_rate * delta_time
            self.heat = max(0, self.heat)

            # Проверяем, остыло ли оружие
            if self.overheated and self.heat < 30:
                self.overheated = False

        # Обновление супер-выстрела
        if not self.super_shot_ready:
            self.super_shot_timer += delta_time
            self.super_shot_charge = min(100, (self.super_shot_timer / self.super_shot_cooldown) * 100)

            if self.super_shot_timer >= self.super_shot_cooldown:
                self.super_shot_ready = True
                self.super_shot_timer = 0
                self.super_shot_charge = 100

        # Обновление анимационных таймеров
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= delta_time

        if self.overheat_flash_timer > 0:
            self.overheat_flash_timer -= delta_time

        # обновление позиций пуль
        for bullet in self.bullets[:]:  # Копируем список для безопасного удаления
            bullet.update(delta_time)
            if not bullet.active:
                self.bullets.remove(bullet)

    def move_left(self):
        """Двигает корабль влево"""
        if self.is_alive and self.center_x > 30:  # Не выходим за левую границу
            self.center_x -= self.speed

    def move_right(self):
        """Двигает корабль вправо"""
        if self.is_alive and self.center_x < SCREEN_WIDTH - 30:  # Не выходим за правую границу
            self.center_x += self.speed

    def shoot(self):
        """Совершает обычный выстрел"""
        if not self.is_alive or not self.can_shoot or self.overheated:
            return None

        # Проверяем перегрев
        if self.heat >= self.overheat_threshold:
            self.overheated = True
            self.overheat_flash_timer = 0.5
            return None

        # Создаем обычную пулю
        bullet = Bullet(self.center_x, self.center_y + 30, is_super=False)
        self.bullets.append(bullet)

        # Обновляем таймеры и перегрев
        self.last_shot_time = time.time()
        self.can_shoot = False
        self.heat += self.heat_per_shot
        self.heat = min(self.heat, self.max_heat)

        # Если достигли порога перегрева
        if self.heat >= self.overheat_threshold:
            self.overheated = True
            self.overheat_flash_timer = 0.5

        return bullet

    def super_shoot(self):
        """Совершает супер-выстрел"""
        if not self.is_alive or not self.super_shot_ready:
            return None

        # Создаем супер-пулю
        bullet = Bullet(self.center_x, self.center_y + 30, is_super=True)
        self.bullets.append(bullet)

        # Сбрасываем заряд
        self.super_shot_ready = False
        self.super_shot_timer = 0
        self.super_shot_charge = 0

        return bullet

    def take_damage(self, damage=1):
        """Наносит урон игроку"""
        if not self.is_alive:
            return

        self.hp -= damage
        self.hit_flash_timer = 0.3  # Запускаем мигание

        if self.hp <= 0:
            self.die()

        return self.hp > 0  # Возвращаем True если еще жив

    def die(self):
        """Обрабатывает смерть игрока"""
        self.is_alive = False
        self.hp = 0
        print("💀 Игрок уничтожен!")

    def reset(self):
        """Сбрасывает состояние игрока к начальному"""
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = 50
        self.hp = self.max_hp
        self.is_alive = True
        self.heat = 0
        self.overheated = False
        self.super_shot_ready = True
        self.super_shot_timer = 0
        self.super_shot_charge = 100
        self.bullets.clear()
        self.can_shoot = True

    def get_shoot_info(self):
        """Возвращает информацию о состоянии стрельбы для UI"""
        return {
            "can_shoot": self.can_shoot,
            "heat": self.heat,
            "overheated": self.overheated,
            "super_shot_ready": self.super_shot_ready,
            "super_shot_charge": self.super_shot_charge,
            "bullets_count": len(self.bullets)
        }
