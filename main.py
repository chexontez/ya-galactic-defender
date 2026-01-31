#!/usr/bin/env python3
"""
Главный запускатель Galactic Defender
Запускает QT-лаунчер, который затем запускает игру
"""

import sys
import os

# Добавляем папки в PYTHONPATH для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), 'launcher'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))


def main():
    print("=" * 50)
    print("   GALACTIC DEFENDER - Космический шутер")
    print("=" * 50)

    # Проверяем зависимости
    try:
        import arcade
        from PyQt6.QtWidgets import QApplication
        print("✓ Все зависимости установлены")
    except ImportError as e:
        print(f"✗ Ошибка: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return

    # Запускаем QT-лаунчер
    from launcher.qt_launcher import GameLauncher

    app = QApplication(sys.argv)
    window = GameLauncher()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()