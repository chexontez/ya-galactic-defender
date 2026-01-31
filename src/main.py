"""
Точка входа в игру Galactic Defender
"""

import arcade
from src.game import GameWindow
from src.constants import print_config_info


def main():
    """Главная функция запуска игры"""
    print("=" * 50)
    print("   GALACTIC DEFENDER - Космический шутер")
    print("=" * 50)

    # Выводим информацию о конфиге
    print_config_info()

    try:
        # Создаем и запускаем игру
        window = GameWindow()
        window.setup()
        arcade.run()
    except Exception as e:
        print(f"✗ Ошибка запуска игры: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()