import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def print_results(data: dict[str, list[str]]) -> None:
    """Выводит результаты сканирования в консоль."""
    logger.info("Результаты сканирования:")

    if data['links']:
        logger.info("Найденные ссылки:")
        for link in data['links']:
            print(f"  - {link}")

    if data['directories']:
        logger.info("Найденные каталоги:")
        for directory in data['directories']:
            print(f"  - {directory}")

    if data['files']:
        logger.info("Найденные файлы:")
        for file in data['files']:
            print(f"  - {file}")

    if data['emails']:
        logger.info("Найденные email-адреса:")
        for email in data['emails']:
            print(f"  - {email}")

    if not any(data.values()):
        logger.info("Данные не найдены.")


def save_to_json(data: dict[str, list[str]], filename: str) -> None:
    """Сохраняет результаты сканирования в JSON-файл."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Данные успешно сохранены в {filename}")
    except IOError as e:
        logger.error(f"Ошибка при сохранении в {filename}: {e}")
        raise
