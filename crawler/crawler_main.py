import argparse
import logging
from pathlib import Path
from crawler.crawler_core import Crawler
from crawler.crawler_output import save_to_json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Web crawler for scanning a website.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url",
        help="Starting URL or domain (e.g., example.com or https://example.com)"
    )
    group.add_argument(
        "--url-file",
        type=Path,
        help="Path to a file containing URLs (one per line)"
    )
    parser.add_argument(
        "--output",
        default="results.json",
        help="Output JSON file (default: results.json)"
    )
    return parser.parse_args()


def process_results(data: dict) -> dict:
    """Форматирует результаты, добавляя сообщения для пустых данных."""
    result = data.copy()
    messages = {}

    if not data['links']:
        messages['message_links'] = "Не удалось найти ссылки."
    if not data['directories']:
        messages['message_directories'] = "Не удалось найти каталоги."
    if not data['files']:
        messages['message_files'] = "Не удалось найти файлы."
    if not data['emails']:
        messages['message_emails'] = "Не удалось найти email-адреса."

    if messages:
        result['messages'] = messages

    return result


def main():
    """Основная функция программы."""
    args = parse_arguments()

    # Получение списка URL
    urls = []
    if args.url:
        urls = [args.url]
        logger.info(f"Запуск краулера с URL: {args.url}")
    elif args.url_file:
        try:
            with args.url_file.open('r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            logger.info(f"Запуск краулера с файлом URL: {args.url_file} ({len(urls)} URL)")
        except IOError as e:
            logger.error(f"Ошибка чтения файла {args.url_file}: {e}")
            exit(1)

    if not urls:
        logger.error("Не предоставлены URL для сканирования.")
        exit(1)

    # Сбор результатов
    all_results = []
    for url in urls:
        try:
            crawler = Crawler(url)
            data = crawler.crawl_site()
            formatted_result = process_results(data)
            all_results.append({
                'target': url,
                'result': formatted_result
            })
        except Exception as e:
            logger.error(f"Ошибка при сканировании {url}: {e}")
            all_results.append({
                'target': url,
                'result': {'messages': {'message_error': f"Ошибка сканирования: {e}"}}
            })

    # Сохранение результатов
    try:
        save_to_json(all_results, args.output)
        logger.info(f"Результаты сохранены в {args.output}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении результатов: {e}")
        exit(1)
    exit()
