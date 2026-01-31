"""
Константы игры, загружаемые из конфигурационного файла
"""

import json
import os

def load_config():
    """Загружает конфигурацию из JSON файла"""
    # Путь к файлу конфигурации
    config_paths = [
        os.path.join("config", "current_config.json"),
        os.path.join("config", "default_config.json")
    ]

    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✓ Конфиг загружен из: {path}")
                    return config
            except Exception as e:
                print(f"✗ Ошибка загрузки конфига {path}: {e}")
                continue

    # Конфиг по умолчанию (если файлов нет)
    print("⚠ Конфиг не найден, используются значения по умолчанию")
    return {
        "screen_width": 800,
        "screen_height": 600,
        "player_speed": 5,
        "enemy_speed": 2,
        "laser_speed": 7,
        "player_lives": 3,
        "difficulty": "medium"
    }

# Загружаем конфигурацию
CONFIG = load_config()

# Извлекаем константы ИЗ КОНФИГА
SCREEN_WIDTH = CONFIG.get("screen_width", 800)
SCREEN_HEIGHT = CONFIG.get("screen_height", 600)
SCREEN_TITLE = "Galactic Defender"
PLAYER_SPEED = CONFIG.get("player_speed", 5)
ENEMY_SPEED = CONFIG.get("enemy_speed", 2)
BULLET_SPEED = CONFIG.get("laser_speed", 7)
PLAYER_LIVES = CONFIG.get("player_lives", 3)
DIFFICULTY = CONFIG.get("difficulty", "medium")

# Игровые константы (могут быть в конфиге или по умолчанию)
PLAYER_HP = CONFIG.get("player_hp", 5)
ENEMY_HP = CONFIG.get("enemy_hp", 1)
ENEMY_SPAWN_RATE = CONFIG.get("enemy_spawn_rate", 1.0)
ASTEROID_SPAWN_RATE = CONFIG.get("asteroid_spawn_rate", 0.3)

# Цвета (не настраиваются через конфиг)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
CYAN = (0, 255, 255)
PURPLE = (180, 50, 230)
ORANGE = (255, 150, 50)

# Дополнительная информация о конфиге для отладки
def print_config_info():
    """Выводит информацию о загруженном конфиге"""
    print("\n" + "="*50)
    print("ТЕКУЩАЯ КОНФИГУРАЦИЯ ИГРЫ:")
    print("="*50)
    print(f"Разрешение: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"Скорость корабля: {PLAYER_SPEED}")
    print(f"Скорость врагов: {ENEMY_SPEED}")
    print(f"Скорость лазера: {BULLET_SPEED}")
    print(f"Жизни игрока: {PLAYER_LIVES}")
    print(f"HP игрока: {PLAYER_HP}")
    print(f"Сложность: {DIFFICULTY}")
    print("="*50 + "\n")