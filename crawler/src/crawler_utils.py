import logging
import os
import re
from urllib.parse import urlparse, urljoin

import requests

from crawler.src.crawler_constants import FILE_EXTENSIONS

# Настройка логирования
logger = logging.getLogger(__name__)


def normalize_url(href: str, base_url: str, allow_subdomains: bool = False) -> str | None:
    try:
        absolute_url = urljoin(base_url, href.strip())
        parsed_url = urlparse(absolute_url)
        if parsed_url.scheme not in ('http', 'https'):
            return None
        absolute_url = absolute_url.split('#')[0]
        base_domain = urlparse(base_url).netloc
        if not allow_subdomains and parsed_url.netloc != base_domain:
            if not (allow_subdomains and base_domain in parsed_url.netloc):
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
    parts = path.split('/')
    directories = []
    current_path = ''
    for part in parts:
        if part:
            current_path += f'/{part}'
            directory = f'{parsed_url.scheme}://{parsed_url.netloc}{current_path}/'
            if directory not in directories:
                directories.append(directory)
    return directories


def check_directory_indexing(url: str, timeout: int = 5) -> bool:
    """Проверяет, доступна ли индексация каталога."""
    try:
        response = requests.head(url.replace(' ', '%20'), timeout=timeout, allow_redirects=True)
        if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
            if 'Index of' in requests.get(url, timeout=timeout).text:
                logger.debug(f"Каталог с индексацией найден: {url}")
                return True
        return False
    except requests.RequestException as e:
        logger.debug(f"Ошибка проверки индексации {url}: {e}")
        return False


def extract_emails(text: str) -> list[str]:
    """Извлекает email-адреса из текста."""
    email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    emails = list(set(email_regex.findall(text)))
    if emails:
        logger.debug(f"Найдены email-адреса: {', '.join(emails)}")
    return emails


def is_file_url(url: str, extensions: list[str] = None) -> bool:
    """Проверяет, является ли URL ссылкой на файл с заданными расширениями."""
    parsed_url = urlparse(url)
    _, ext = os.path.splitext(parsed_url.path)
    if not extensions:
        extensions = FILE_EXTENSIONS
    return ext.lower() in [e.lower() for e in extensions]


def is_excluded_url(url: str, exclude_extensions: list[str]) -> bool:
    """Проверяет, исключен ли URL на основе расширений."""
    if not exclude_extensions:
        return False
    parsed_url = urlparse(url)
    _, ext = os.path.splitext(parsed_url.path)
    return ext.lower() in [e.lower() for e in exclude_extensions]
