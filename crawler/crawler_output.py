import json
import logging
import pathlib

# Настройка логирования
logger = logging.getLogger(__name__)

def output_results(results: list[dict], output_file: pathlib.Path) -> None:
    """Сохраняет результаты сканирования в JSON и, при необходимости, в текстовый файл."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logger.info(f"Результаты сохранены в JSON: {str(output_file)}")

    except IOError as e:
        logger.error(f"Ошибка сохранения результатов: {e}")
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при выводе результатов: {e}")
        raise
