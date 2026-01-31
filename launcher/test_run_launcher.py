"""
Альтернативный скрипт для запуска только QT-лаунчера
Используется для тестирования лаунчера отдельно от игры
"""

import sys
import os

# Добавляем родительскую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if __name__ == "__main__":
    from launcher.qt_launcher import main
    main()