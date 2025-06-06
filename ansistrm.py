import logging

class ColorizingStreamHandler(logging.StreamHandler):
    """Обработчик логов с цветным форматированием для консоли на Linux."""

    # Цвета и их ANSI-коды
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    # Уровни логов и их стили: (фон, текст, жирность)
    level_map = {
        logging.DEBUG: (None, 'cyan', True),
        logging.INFO: (None, 'blue', False),
        logging.WARNING: (None, 'magenta', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }

    # ANSI-последовательности
    csi = '\x1b['  # Начало ANSI-кода
    reset = '\x1b[0m'  # Сброс форматирования

    @property
    def is_tty(self):
        """Проверка, является ли поток терминалом."""
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        """Вывод сообщения лога."""
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                stream.write(message)  # В Linux цвет уже в message
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except Exception as e:
            self.handleError(record)

    def colorize(self, message, record):
        """Добавление ANSI-кодов для цветного форматирования."""
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))  # Код фона
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))  # Код текста
            if bold:
                params.append('1')  # Жирный текст
            if params:
                message = f"{self.csi}{';'.join(params)}m{message}{self.reset}"
        return message

    def format(self, record):
        """Форматирование сообщения с учетом цвета."""
        message = super().format(record)
        if self.is_tty:
            # Обрабатываем только первую строку для цвета
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message

def main():
    """Пример использования обработчика."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(ColorizingStreamHandler())
    # logging.debug('Это отладочное сообщение')
    # logging.info('Информация для вас')
    # logging.warning('Осторожно, предупреждение')
    # logging.error('Ошибка случилась')
    # logging.critical('Критическая ситуация!')

if __name__ == '__main__':
    main()