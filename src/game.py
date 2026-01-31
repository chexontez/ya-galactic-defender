"""
Основной класс игры Galactic Defender
Управляет состоянием игры, отрисовкой, логикой и коллизиями
"""

import arcade
import time
import sqlite3
from datetime import datetime
from src.constants import *
from src.player import Player
from src.enemy import Enemy
from src.asteroid import Asteroid

class GameWindow(arcade.Window):
    """
    Главное окно игры. Управляет всеми состояниями и логикой.
    """

    def __init__(self):
        """Инициализация игры с настройками из конфига"""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Состояния игры
        self.game_state = "MENU"  # MENU, PLAYING, GAME_OVER
        self.last_game_stats = None  # Статистика последней игры

        # Игровые объекты
        self.player = None
        self.enemies = arcade.SpriteList()
        self.asteroids = arcade.SpriteList()
        self.bullets = arcade.SpriteList()

        # Статистика текущей игры
        self.score = 0
        self.enemies_killed = 0
        self.asteroids_destroyed = 0
        self.start_time = 0
        self.game_time = 0
        self.total_game_time = 0

        # Таймеры
        self.enemy_spawn_timer = 0
        self.asteroid_spawn_timer = 0

        # UI элементы меню
        self.play_button = None
        self.last_game_button = None

        # Загружаем статистику последней игры
        self.load_last_game_stats()

        # Настраиваем игру
        arcade.set_background_color(arcade.color.BLACK)

        print("✓ Игра инициализирована")

    def setup(self):
        """Настройка новой игры"""
        # Создаем игрока
        self.player = Player()

        # Очищаем списки объектов
        self.enemies = arcade.SpriteList()
        self.asteroids = arcade.SpriteList()
        self.bullets = arcade.SpriteList()

        # Сброс статистики
        self.score = 0
        self.enemies_killed = 0
        self.asteroids_destroyed = 0
        self.start_time = time.time()
        self.game_time = 0
        self.total_game_time = 0

        # Сброс таймеров
        self.enemy_spawn_timer = 0
        self.asteroid_spawn_timer = 0

        # Устанавливаем состояние игры
        self.game_state = "PLAYING"

        print("✓ Новая игра начата")

    def load_last_game_stats(self):
        """Загружает статистику последней игры из базы данных"""
        try:
            conn = sqlite3.connect("src/logs.db")
            cursor = conn.cursor()

            # Создаем таблицу если её нет
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    score INTEGER,
                    enemies_killed INTEGER,
                    asteroids_destroyed INTEGER,
                    game_time REAL,
                    total_time REAL
                )
            """)

            # Получаем последнюю запись
            cursor.execute("""
                SELECT * FROM game_logs 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)

            result = cursor.fetchone()
            if result:
                self.last_game_stats = {
                    "id": result[0],
                    "timestamp": result[1],
                    "score": result[2],
                    "enemies_killed": result[3],
                    "asteroids_destroyed": result[4],
                    "game_time": result[5],
                    "total_time": result[6]
                }
                print(f"✓ Загружена статистика последней игры: {self.last_game_stats['score']} очков")
            else:
                print("⚠ Нет записей о предыдущих играх")
                self.last_game_stats = {
                    "score": 0,
                    "enemies_killed": 0,
                    "game_time": 0,
                    "timestamp": "Нет данных"
                }

            conn.close()
        except Exception as e:
            print(f"✗ Ошибка загрузки статистики: {e}")
            self.last_game_stats = {
                "score": 0,
                "enemies_killed": 0,
                "game_time": 0,
                "timestamp": "Ошибка загрузки"
            }

    def save_game_stats(self):
        """Сохраняет статистику текущей игры в базу данных"""
        try:
            conn = sqlite3.connect("src/logs.db")
            cursor = conn.cursor()

            # Вставляем новую запись
            cursor.execute("""
                INSERT INTO game_logs 
                (timestamp, score, enemies_killed, asteroids_destroyed, game_time, total_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.score,
                self.enemies_killed,
                self.asteroids_destroyed,
                self.game_time,
                self.total_game_time
            ))

            conn.commit()
            conn.close()

            print(f"✓ Статистика сохранена: {self.score} очков, {self.enemies_killed} врагов")
        except Exception as e:
            print(f"✗ Ошибка сохранения статистики: {e}")

    def on_draw(self):
        """Отрисовка игры в зависимости от состояния"""
        arcade.start_render()

        if self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state == "PLAYING":
            self.draw_game()
        elif self.game_state == "GAME_OVER":
            self.draw_game_over()

    def draw_menu(self):
        """Отрисовка главного меню"""
        # Заголовок
        arcade.draw_text(
            "GALACTIC DEFENDER",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.CYAN, 48,
            anchor_x="center", anchor_y="center",
            bold=True
        )

        # Подзаголовок
        arcade.draw_text(
            "Космический шутер",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 160,
            arcade.color.LIGHT_GRAY, 24,
            anchor_x="center", anchor_y="center"
        )

        # Кнопка "Играть"
        play_x = SCREEN_WIDTH // 2
        play_y = SCREEN_HEIGHT // 2 + 50
        play_width = 200
        play_height = 60

        arcade.draw_rectangle_filled(
            play_x, play_y,
            play_width, play_height,
            arcade.color.GREEN
        )
        arcade.draw_rectangle_outline(
            play_x, play_y,
            play_width, play_height,
            arcade.color.WHITE, 3
        )
        arcade.draw_text(
            "ИГРАТЬ",
            play_x, play_y,
            arcade.color.BLACK, 28,
            anchor_x="center", anchor_y="center",
            bold=True
        )
        self.play_button = (play_x, play_y, play_width, play_height)

        # Кнопка "Предыдущая игра"
        last_x = SCREEN_WIDTH // 2
        last_y = SCREEN_HEIGHT // 2 - 50
        last_width = 300
        last_height = 60

        arcade.draw_rectangle_filled(
            last_x, last_y,
            last_width, last_height,
            arcade.color.BLUE_GRAY
        )
        arcade.draw_rectangle_outline(
            last_x, last_y,
            last_width, last_height,
            arcade.color.WHITE, 3
        )
        arcade.draw_text(
            "ПРЕДЫДУЩАЯ ИГРА",
            last_x, last_y,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center"
        )
        self.last_game_button = (last_x, last_y, last_width, last_height)

        # Информация о последней игре
        if self.last_game_stats:
            info_y = SCREEN_HEIGHT // 2 - 150

            arcade.draw_text(
                "Последняя игра:",
                SCREEN_WIDTH // 2, info_y,
                arcade.color.YELLOW, 20,
                anchor_x="center", anchor_y="center"
            )

            arcade.draw_text(
                f"Очки: {self.last_game_stats['score']}",
                SCREEN_WIDTH // 2, info_y - 30,
                arcade.color.WHITE, 18,
                anchor_x="center", anchor_y="center"
            )

            arcade.draw_text(
                f"Врагов убито: {self.last_game_stats['enemies_killed']}",
                SCREEN_WIDTH // 2, info_y - 60,
                arcade.color.WHITE, 18,
                anchor_x="center", anchor_y="center"
            )

            if 'game_time' in self.last_game_stats:
                arcade.draw_text(
                    f"Время: {self.last_game_stats['game_time']:.1f} сек",
                    SCREEN_WIDTH // 2, info_y - 90,
                    arcade.color.WHITE, 18,
                    anchor_x="center", anchor_y="center"
                )

    def draw_game(self):
        """Отрисовка игрового процесса"""
        # Рисуем фон (звездное небо)
        self.draw_background()

        # Рисуем игровые объекты
        if self.player:
            self.player.draw()

        self.enemies.draw()
        self.asteroids.draw()

        # Рисуем пули игрока
        for bullet in self.player.bullets:
            bullet.draw()

        # Рисуем интерфейс внизу
        self.draw_game_ui()

        # Рисуем статистику вверху
        self.draw_game_stats()

    def draw_background(self):
        """Рисует звездный фон"""
        # Здесь можно добавить звезды, но пока просто градиент
        arcade.draw_lrtb_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_HEIGHT * 0.7,
            (10, 10, 40)  # Темно-синий сверху
        )
        arcade.draw_lrtb_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT * 0.7, 0,
            (20, 20, 50)  # Более светлый снизу
        )

    def draw_game_ui(self):
        """Рисует игровой интерфейс внизу экрана"""
        ui_height = 80
        ui_y = ui_height // 2

        # Фон интерфейса
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, ui_y,
            SCREEN_WIDTH, ui_height,
            (30, 30, 60, 200)
        )

        if self.player:
            # 1. HP игрока
            hp_x = 100
            hp_text = f"HP: {self.player.hp}/{self.player.max_hp}"
            arcade.draw_text(
                hp_text, hp_x, ui_y,
                arcade.color.WHITE, 20,
                anchor_x="center", anchor_y="center"
            )

            # Полоска HP
            hp_bar_width = 150
            hp_bar_height = 15
            hp_percent = self.player.hp / self.player.max_hp

            arcade.draw_rectangle_filled(
                hp_x, ui_y - 25,
                hp_bar_width, hp_bar_height,
                (50, 50, 50)
            )

            hp_color = (
                int(255 * (1 - hp_percent)),  # Красный при малом HP
                int(255 * hp_percent),       # Зеленый при полном HP
                50
            )

            arcade.draw_rectangle_filled(
                hp_x - hp_bar_width//2 + (hp_bar_width * hp_percent)//2,
                ui_y - 25,
                hp_bar_width * hp_percent, hp_bar_height,
                hp_color
            )

            # 2. Уровень перегрева
            heat_x = SCREEN_WIDTH // 4
            heat_text = f"Перегрев: {int(self.player.heat)}%"
            arcade.draw_text(
                heat_text, heat_x, ui_y,
                arcade.color.WHITE, 20,
                anchor_x="center", anchor_y="center"
            )

            # Полоска перегрева
            heat_bar_width = 150
            heat_bar_height = 15

            arcade.draw_rectangle_filled(
                heat_x, ui_y - 25,
                heat_bar_width, heat_bar_height,
                (50, 50, 50)
            )

            heat_color = (
                255,  # Красный
                int(255 * (1 - self.player.heat / 100)),  # Меньше зеленого при нагреве
                50
            )

            arcade.draw_rectangle_filled(
                heat_x - heat_bar_width//2 + (heat_bar_width * self.player.heat / 100)//2,
                ui_y - 25,
                heat_bar_width * self.player.heat / 100, heat_bar_height,
                heat_color
            )

            # 3. Время игры
            time_x = SCREEN_WIDTH // 2 + 100
            time_text = f"Время: {self.game_time:.1f}с"
            arcade.draw_text(
                time_text, time_x, ui_y,
                arcade.color.WHITE, 20,
                anchor_x="center", anchor_y="center"
            )

            # 4. Время до супер выстрела
            super_x = SCREEN_WIDTH - 150
            if self.player.super_shot_ready:
                super_text = "СУПЕР ГОТОВ!"
                super_color = arcade.color.GREEN
            else:
                super_text = f"Супер: {int(self.player.super_shot_charge)}%"
                super_color = arcade.color.YELLOW

            arcade.draw_text(
                super_text, super_x, ui_y,
                super_color, 20,
                anchor_x="center", anchor_y="center"
            )

            # Круговая шкала для супер выстрела
            if not self.player.super_shot_ready:
                radius = 15
                arcade.draw_circle_outline(
                    super_x, ui_y - 25,
                    radius, arcade.color.YELLOW, 2
                )
                arcade.draw_arc_filled(
                    super_x, ui_y - 25, radius,
                    (100, 200, 255),
                    0, 360 * (self.player.super_shot_charge / 100)
                )

    def draw_game_stats(self):
        """Рисует статистику вверху экрана"""
        # Счет
        arcade.draw_text(
            f"СЧЕТ: {self.score}",
            20, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 24
        )

        # Убито врагов
        arcade.draw_text(
            f"ВРАГОВ: {self.enemies_killed}",
            20, SCREEN_HEIGHT - 60,
            arcade.color.LIGHT_GRAY, 18
        )

        # Уничтожено астероидов
        arcade.draw_text(
            f"АСТЕРОИДОВ: {self.asteroids_destroyed}",
            20, SCREEN_HEIGHT - 90,
            arcade.color.LIGHT_GRAY, 18
        )

        # FPS (для отладки)
        arcade.draw_text(
            f"FPS: {int(1/self.frame_rate if self.frame_rate > 0 else 0)}",
            SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30,
            arcade.color.GRAY, 16
        )

    def draw_game_over(self):
        """Отрисовка экрана окончания игры"""
        # Полупрозрачный черный фон
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (0, 0, 0, 200)
        )

        # Заголовок
        arcade.draw_text(
            "ИГРА ОКОНЧЕНА",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7,
            arcade.color.RED, 48,
            anchor_x="center", anchor_y="center",
            bold=True
        )

        # Статистика игры
        stats_y = SCREEN_HEIGHT * 0.5

        arcade.draw_text(
            f"Итоговый счет: {self.score}",
            SCREEN_WIDTH // 2, stats_y,
            arcade.color.WHITE, 32,
            anchor_x="center", anchor_y="center"
        )

        arcade.draw_text(
            f"Врагов убито: {self.enemies_killed}",
            SCREEN_WIDTH // 2, stats_y - 50,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center"
        )

        arcade.draw_text(
            f"Астероидов уничтожено: {self.asteroids_destroyed}",
            SCREEN_WIDTH // 2, stats_y - 90,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center"
        )

        arcade.draw_text(
            f"Время выживания: {self.total_game_time:.1f} секунд",
            SCREEN_WIDTH // 2, stats_y - 130,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center"
        )

        # Кнопка "В меню"
        menu_x = SCREEN_WIDTH // 2
        menu_y = SCREEN_HEIGHT * 0.3
        menu_width = 250
        menu_height = 60

        arcade.draw_rectangle_filled(
            menu_x, menu_y,
            menu_width, menu_height,
            arcade.color.BLUE
        )
        arcade.draw_rectangle_outline(
            menu_x, menu_y,
            menu_width, menu_height,
            arcade.color.WHITE, 3
        )
        arcade.draw_text(
            "ВЕРНУТЬСЯ В МЕНЮ",
            menu_x, menu_y,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center"
        )
        self.menu_button = (menu_x, menu_y, menu_width, menu_height)

    def on_update(self, delta_time):
        """Обновление игровой логики"""
        if self.game_state == "PLAYING":
            self.update_game(delta_time)

    def update_game(self, delta_time):
        """Обновление игрового процесса"""
        # Обновляем время игры
        self.game_time = time.time() - self.start_time
        self.total_game_time = self.game_time

        # Обновляем игрока
        if self.player:
            self.player.update(delta_time)

            # Проверяем смерть игрока
            if not self.player.is_alive:
                self.end_game()
                return

        # Генерация врагов
        self.enemy_spawn_timer += delta_time
        if self.enemy_spawn_timer >= 1.0 / ENEMY_SPAWN_RATE:
            enemy = Enemy()
            self.enemies.append(enemy)
            self.enemy_spawn_timer = 0

        # Генерация астероидов
        self.asteroid_spawn_timer += delta_time
        if self.asteroid_spawn_timer >= 1.0 / ASTEROID_SPAWN_RATE:
            asteroid = Asteroid()
            self.asteroids.append(asteroid)
            self.asteroid_spawn_timer = 0

        # Обновление врагов и астероидов
        self.enemies.update()
        self.asteroids.update()

        # Удаление объектов вышедших за экран
        for enemy in self.enemies:
            if enemy.bottom > SCREEN_HEIGHT + 50:
                enemy.remove_from_sprite_lists()

        for asteroid in self.asteroids:
            if asteroid.bottom > SCREEN_HEIGHT + 50:
                asteroid.remove_from_sprite_lists()

        # Проверка коллизий
        self.check_collisions()

    def check_collisions(self):
        """Проверка всех столкновений в игре"""
        if not self.player:
            return

        # 1. Столкновения пуль с врагами
        for bullet in self.player.bullets[:]:
            # С врагами
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemies)
            for enemy in hit_list:
                bullet.remove_from_sprite_lists()
                enemy.remove_from_sprite_lists()
                self.score += 10
                self.enemies_killed += 1

            # С астероидами
            hit_list = arcade.check_for_collision_with_list(bullet, self.asteroids)
            for asteroid in hit_list:
                bullet.remove_from_sprite_lists()
                asteroid.take_damage(1)
                if asteroid.hp <= 0:
                    asteroid.remove_from_sprite_lists()
                    self.score += 20
                    self.asteroids_destroyed += 1

        # 2. Столкновения игрока с врагами
        hit_list = arcade.check_for_collision_with_list(self.player, self.enemies)
        for enemy in hit_list:
            enemy.remove_from_sprite_lists()
            if self.player.take_damage(1):
                # Игрок умер
                self.end_game()
                return

        # 3. Столкновения игрока с астероидами
        hit_list = arcade.check_for_collision_with_list(self.player, self.asteroids)
        for asteroid in hit_list:
            asteroid.remove_from_sprite_lists()
            if self.player.take_damage(2):  # Астероид наносит больше урона
                self.end_game()
                return

    def end_game(self):
        """Завершает текущую игру"""
        self.game_state = "GAME_OVER"
        self.save_game_stats()
        print(f"✗ Игра окончена. Счет: {self.score}")

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if self.game_state == "PLAYING" and self.player:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.player.move_left()
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.player.move_right()
            elif key == arcade.key.SPACE:
                self.player.shoot()
            elif key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
                self.player.super_shoot()

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if self.game_state == "PLAYING" and self.player:
            if key == arcade.key.LEFT or key == arcade.key.A:
                # Можно добавить логику плавного движения если нужно
                pass
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                pass

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.game_state == "MENU":
                # Проверка клика по кнопке "Играть"
                if self.play_button:
                    bx, by, bw, bh = self.play_button
                    if (bx - bw/2 <= x <= bx + bw/2 and
                        by - bh/2 <= y <= by + bh/2):
                        self.setup()

                # Проверка клика по кнопке "Предыдущая игра"
                if self.last_game_button:
                    bx, by, bw, bh = self.last_game_button
                    if (bx - bw/2 <= x <= bx + bw/2 and
                        by - bh/2 <= y <= by + bh/2):
                        # Показываем статистику (уже отображается)
                        pass

            elif self.game_state == "GAME_OVER":
                # Проверка клика по кнопке "В меню"
                if hasattr(self, 'menu_button'):
                    bx, by, bw, bh = self.menu_button
                    if (bx - bw/2 <= x <= bx + bw/2 and
                        by - bh/2 <= y <= by + bh/2):
                        self.game_state = "MENU"
                        self.load_last_game_stats()