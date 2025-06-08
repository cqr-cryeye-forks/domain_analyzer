import argparse
import logging
import pathlib
from pathlib import Path
from crawler.crawler_core import Crawler
from crawler.crawler_output import output_results

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
        help="URL or domain to start crawling (e.g., example.com or https://example.com)"
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
    parser.add_argument(
        "--max-urls",
        type=int,
        default=5000,
        help="Maximum number of URLs to crawl (default: 5000)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-D", "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "-f", "--fetch-files",
        action="store_true",
        help="Download detected files to domain/Files/"
    )
    parser.add_argument(
        "-s", "--subdomains",
        action="store_true",
        help="Also scan subdomains matching the URL domain"
    )
    parser.add_argument(
        "-r", "--follow-redirect",
        action="store_false",
        help="Do not follow redirects (default: follow redirects)"
    )
    parser.add_argument(
        "-F", "--file-extension",
        help="Download files with specified extensions (comma-separated, e.g., pdf,doc)"
    )
    parser.add_argument(
        "-d", "--docs-files",
        action="store_true",
        help="Download document files (pdf, doc, xls, etc.)"
    )
    parser.add_argument(
        "-E", "--exclude-extensions",
        help="Exclude files with specified extensions (comma-separated, e.g., jpg,png)"
    )
    return parser.parse_args()


def main():
    """Основная функция программы."""
    args = parse_arguments()

    max_urls: int = int(args.max_urls)
    urls_input_file = args.url_file
    target_url = args.url

    # Настройка уровня логирования
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    # Обработка расширений файлов
    extensions = []
    if args.file_extension:
        extensions = [f".{ext.lower()}" for ext in args.file_extension.split(',')]
        extensions.extend([f".{ext.upper()}" for ext in args.file_extension.split(',')])
    elif args.docs_files:
        extensions = [
            '.doc', '.DOC', '.ppt', '.PPT', '.pps', '.PPS', '.xls', '.XLS',
            '.docx', '.DOCX', '.pptx', '.PPTX', '.ppsx', '.PPSX', '.xlsx', '.XLSX',
            '.sxw', '.SXW', '.sxc', '.SXC', '.sxi', '.SXI', '.odt', '.ODT',
            '.ods', '.ODS', '.odg', '.ODG', '.odp', '.ODP', '.pdf', '.PDF',
            '.wpd', '.WPD', '.txt', '.TXT', '.gnumeric', '.GNUMERIC', '.csv', '.CSV'
        ]
    exclude_extensions = []
    if args.exclude_extensions:
        exclude_extensions = [f".{ext.lower()}" for ext in args.exclude_extensions.split(',')]
        exclude_extensions.extend([f".{ext.upper()}" for ext in args.exclude_extensions.split(',')])

    # Получение списка URL
    urls = []
    if target_url:
        urls = [target_url]
        logger.info(f"Запуск краулера с URL: {target_url}")
    elif urls_input_file:
        try:
            with urls_input_file.open('r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            logger.info(f"Запуск краулера с файлом URL: {urls_input_file} ({len(urls)} URL)")
        except IOError as e:
            logger.error(f"Ошибка чтения файла {urls_input_file}: {e}")
            exit(1)

    if not urls:
        logger.error("Не предоставлены URL для сканирования.")
        exit(1)

    fetch_files = args.fetch_files or args.file_extension or args.docs_files
    subdomains = args.subdomains
    follow_redirect = args.follow_redirect

    all_results = []
    for url in urls:
        try:
            crawler = Crawler(
                base_url=url,
                max_urls=max_urls,
                fetch_files=fetch_files,
                subdomains=subdomains,
                follow_redirects=follow_redirect,
                extensions=extensions,
                exclude_extensions=exclude_extensions
            )
            data = crawler.crawl_site()
            all_results.append({
                'target': url,
                'result': data
            })
        except Exception as e:
            logger.error(f"Ошибка при сканировании {url}: {e}")
            all_results.append({
                'target': url,
                'result': {'messages': {'message_error': f"Ошибка сканирования: {e}"}}
            })

    try:
        JSON_OUTPUT: pathlib.Path = pathlib.Path(args.output)
        OUTPUT_PATH: pathlib.Path = MAIN_DIR / JSON_OUTPUT
        output_results(all_results, OUTPUT_PATH)
        logger.info(f"Результаты сохранены в {OUTPUT_PATH}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении результатов: {e}")
        exit(1)
