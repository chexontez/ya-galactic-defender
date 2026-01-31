"""
QT-лаунчер для игры Galactic Defender
Позволяет настроить параметры игры перед запуском
"""

import sys
import os
import json
from PyQt6.QtWidgets import (QMainWindow, QApplication, QMessageBox,
                             QVBoxLayout, QWidget)
from PyQt6.QtGui import QIntValidator
from PyQt6 import uic


class GameLauncher(QMainWindow):
    """Основной класс лаунчера"""

    def __init__(self):
        super().__init__()

        # Загружаем интерфейс из .ui файла
        ui_path = os.path.join(os.path.dirname(__file__), "startwindow.ui")
        uic.loadUi(ui_path, self)

        # Настраиваем валидацию
        self.setup_validators()

        # Подключаем обработчики
        self.connect_signals()

        # Устанавливаем заголовок окна
        self.setWindowTitle("Galactic Defender - Настройки запуска")

        # Устанавливаем фиксированный размер
        self.setFixedSize(self.size())

    def setup_validators(self):
        """Настраивает валидаторы для полей ввода"""
        # Валидатор для цифр от 100 до 9999
        int_validator = QIntValidator(100, 9999, self)
        self.width.setValidator(int_validator)
        self.height.setValidator(int_validator)

    def connect_signals(self):
        """Подключает обработчики событий"""
        # Кнопка запуска игры
        self.sumbit.clicked.connect(self.launch_game)

        # Автопроверка при изменении текста
        self.width.textChanged.connect(self.validate_resolution)
        self.height.textChanged.connect(self.validate_resolution)

    def validate_resolution(self):
        """Проверяет корректность введённого разрешения"""
        width_text = self.width.text()
        height_text = self.height.text()

        # Если поля не пустые, проверяем значения
        if width_text and height_text:
            try:
                width = int(width_text)
                height = int(height_text)

                # Проверяем минимальные значения
                if width < 640 or height < 480:
                    self.sumbit.setEnabled(False)
                    self.statusbar.showMessage("Минимальное разрешение: 640x480")
                    return

                # Проверяем соотношение сторон (опционально)
                if width / height > 3 or height / width > 3:
                    self.statusbar.showMessage("Предупреждение: нестандартное соотношение сторон")
                else:
                    self.statusbar.showMessage("")

                self.sumbit.setEnabled(True)

            except ValueError:
                self.sumbit.setEnabled(False)
                self.statusbar.showMessage("Введите числовые значения")
        else:
            self.sumbit.setEnabled(False)

    def validate_inputs(self):
        """
        Проверяет все поля ввода
        Возвращает список ошибок или пустой список если всё OK
        """
        errors = []

        # Проверка ширины
        width_text = self.width.text().strip()
        if not width_text:
            errors.append("Поле 'Ширина' не может быть пустым")
        elif not width_text.isdigit():
            errors.append("Поле 'Ширина' должно содержать только цифры")
        else:
            width = int(width_text)
            if width < 640:
                errors.append("Минимальная ширина: 640")
            elif width > 3840:
                errors.append("Максимальная ширина: 3840")

        # Проверка высоты
        height_text = self.height.text().strip()
        if not height_text:
            errors.append("Поле 'Высота' не может быть пустым")
        elif not height_text.isdigit():
            errors.append("Поле 'Высота' должно содержать только цифры")
        else:
            height = int(height_text)
            if height < 480:
                errors.append("Минимальная высота: 480")
            elif height > 2160:
                errors.append("Максимальная высота: 2160")

        return errors

    # В методе get_game_settings():
    def get_game_settings(self):
        """
        Возвращает настройки игры в виде словаря
        """
        # Получаем значения из полей
        try:
            width = int(self.width.text())
        except ValueError:
            width = 800

        try:
            height = int(self.height.text())
        except ValueError:
            height = 600

        return {
            "screen_width": width,
            "screen_height": height,
            "player_speed": self.player_speed.value(),
            "enemy_speed": self.enemy_speed.value(),
            "laser_speed": self.laser_speed.value(),
            "player_lives": 3,  # Можно добавить в интерфейс
            "player_hp": 5,  # Можно добавить в интерфейс
            "enemy_hp": 1,  # Можно добавить в интерфейс
            "difficulty": "custom",
            "enemy_spawn_rate": 1.0,
            "asteroid_spawn_rate": 0.3,
            "music_volume": 70,
            "sound_volume": 80,
            "config_version": "1.0",
            "timestamp": "2024-01-01"  # Можно добавить текущее время
        }

    # В методе save_settings_to_file():
    def save_settings_to_file(self, settings):
        """
        Сохраняет настройки в JSON файл для игры
        """
        # Определяем путь к папке config
        project_root = os.path.dirname(os.path.dirname(__file__))
        config_dir = os.path.join(project_root, "config")

        # Создаём папку если её нет
        os.makedirs(config_dir, exist_ok=True)

        # Сохраняем текущие настройки
        current_config_path = os.path.join(config_dir, "current_config.json")
        try:
            with open(current_config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            print(f"✓ Настройки сохранены в: {current_config_path}")
            return current_config_path
        except Exception as e:
            print(f"✗ Ошибка сохранения: {e}")
            return None

    def launch_game(self):
        """
        Основная функция запуска игры
        """
        print("=" * 50)
        print("Попытка запуска игры...")

        # Проверяем ввод
        errors = self.validate_inputs()
        if errors:
            error_msg = "Обнаружены ошибки:\n\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.critical(self, "Ошибка ввода", error_msg)
            return

        # Получаем настройки
        settings = self.get_game_settings()

        # Выводим настройки в консоль
        print("Настройки игры:")
        print(f"  • Разрешение: {settings['screen_width']}x{settings['screen_height']}")
        print(f"  • Скорость корабля: {settings['player_speed']}")
        print(f"  • Скорость врагов: {settings['enemy_speed']}")
        print(f"  • Скорость лазера: {settings['laser_speed']}")

        # Сохраняем настройки
        try:
            config_path = self.save_settings_to_file(settings)
        except Exception:
            return 0

        # Закрываем лаунчер
        self.close()

        # Запускаем игру
        try:
            self.start_arcade_game()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска",
                                 f"Не удалось запустить игру:\n{str(e)}")
            # Открываем лаунчер снова при ошибке
            self.show()

    def start_arcade_game(self):
        """
        Запускает игру на Arcade
        """
        print("Запуск игры Arcade...")

        # Импортируем здесь, чтобы не загружать arcade раньше времени
        import subprocess
        import sys

        # Определяем путь к игре
        project_root = os.path.dirname(os.path.dirname(__file__))
        game_path = os.path.join(project_root, "src", "main.py")

        # Проверяем существование файла игры
        if not os.path.exists(game_path):
            # Пробуем альтернативный путь
            game_path = os.path.join(project_root, "src", "game.py")

        if not os.path.exists(game_path):
            raise FileNotFoundError(f"Не найден файл игры: {game_path}")

        # Запускаем игру в отдельном процессе
        print(f"Запуск: {sys.executable} {game_path}")

        try:
            subprocess.Popen([
                sys.executable,
                game_path
            ], cwd=project_root)

            print("✓ Игра успешно запущена!")

        except Exception as e:
            print(f"✗ Ошибка при запуске игры: {e}")
            raise

    def closeEvent(self, event):
        """
        Обработчик закрытия окна
        """
        print("Лаунчер закрыт")
        event.accept()


def main():
    """
    Точка входа для запуска лаунчера отдельно
    """
    app = QApplication(sys.argv)

    # Устанавливаем стиль приложения
    app.setStyle('Fusion')

    # Создаём и показываем окно лаунчера
    launcher = GameLauncher()
    launcher.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
