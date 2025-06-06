import logging
import os
import re
from urllib.parse import urlparse, urljoin

import requests

from crawler.crawler_core import Crawler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def normalize_url(href: str, base_url: str) -> str | None:
    """Преобразует ссылку в абсолютный URL с проверкой валидности."""
    try:
        # Преобразование в абсолютный URL
        absolute_url = urljoin(base_url, href.strip())
        parsed_url = urlparse(absolute_url)

        # Проверка, что URL имеет допустимую схему
        if parsed_url.scheme not in ('http', 'https'):
            return None

        # Удаление якорей
        absolute_url = absolute_url.split('#')[0]

        # Проверка домена (если поддомены отключены)
        base_domain = urlparse(base_url).netloc
        if not Crawler.ALLOW_SUBDOMAINS and parsed_url.netloc != base_domain:
            return None

        return absolute_url
    except ValueError as e:
        logger.debug(f"Невалидная ссылка {href}: {e}")
        return None


def extract_directories(url: str) -> list[str]:
    """Извлекает структуру каталогов из URL."""
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    if not path:
        return []

    # Разбиение пути на каталоги
    parts = path.split('/')
    directories = []
    current_path = ''
    for part in parts:
        if part:  # Пропуск пустых частей
            current_path += f'/{part}'
            directory = f'{parsed_url.scheme}://{parsed_url.netloc}{current_path}/'
            if directory not in directories:
                directories.append(directory)
    return directories


def check_directory_indexing(url: str, timeout: int = 5) -> bool:
    """Проверяет, доступна ли индексация каталога."""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
            logger.debug(f"Каталог с индексацией найден: {url}")
            return True
        return False
    except requests.RequestException as e:
        logger.debug(f"Ошибка проверки индексации {url}: {e}")
        return False


def extract_emails(text: str) -> list[str]:
    """Извлекает email-адреса из текста."""
    email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    emails = list(set(email_regex.findall(text)))  # Удаление дубликатов
    if emails:
        logger.debug(f"Найдены email-адреса: {', '.join(emails)}")
    return emails


def is_file_url(url: str) -> bool:
    """Проверяет, является ли URL ссылкой на файл."""
    parsed_url = urlparse(url)
    _, ext = os.path.splitext(parsed_url.path)
    return ext.lower() in Crawler.FILE_EXTENSIONS
