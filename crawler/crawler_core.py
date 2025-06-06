import logging
import os
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from crawler.crawler_constants import email_regex

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Crawler:
    """Класс для веб-сканирования сайта с заданного URL."""

    # Предопределенные настройки
    MAX_DEPTH = 100  # Максимальное количество страниц для сканирования
    TIMEOUT = 5  # Таймаут для HTTP-запросов (секунды)
    ALLOW_SUBDOMAINS = False  # Не сканировать поддомены
    ALLOW_REDIRECTS = True  # Следовать редиректам
    FILE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx'}  # Разрешенные расширения файлов

    def __init__(self, start_url: str):
        """Инициализация краулера с начальным URL."""
        # Нормализация URL
        if not start_url.startswith(('http://', 'https://')):
            start_url = f'https://{start_url}'
        self.start_url = start_url
        self.base_domain = urlparse(self.start_url).netloc
        # Структуры данных
        self.to_crawl = [(self.start_url, 0)]  # (URL, глубина)
        self.crawled = set()  # Обработанные URL
        self.data = {
            'links': [],  # Все найденные ссылки
            'directories': [],  # Каталоги
            'files': [],  # Ссылки на файлы
            'emails': []  # Email-адреса
        }
        # Регулярное выражение для email
        self.email_regex = re.compile(email_regex)
        logger.info(f'Инициализация краулера для {self.start_url}')

    def crawl_site(self) -> dict:
        """Запуск сканирования сайта. Возвращает собранные данные."""
        while self.to_crawl and len(self.crawled) < self.MAX_DEPTH:
            url, depth = self.to_crawl.pop(0)
            if url not in self.crawled:
                logger.info(f'Сканирование: {url} (глубина {depth})')
                self.crawl_url(url, depth)
                self.crawled.add(url)
        logger.info(f'Сканирование завершено. Обработано {len(self.crawled)} страниц')
        return self.data

    def crawl_url(self, url: str, depth: int) -> None:
        """Обработка одного URL."""
        try:
            response = requests.get(
                url,
                timeout=self.TIMEOUT,
                allow_redirects=self.ALLOW_REDIRECTS
            )
            if response.status_code != 200:
                logger.warning(f'Не удалось загрузить {url}: статус {response.status_code}')
                return

            # Парсинг страницы
            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлечение email-адресов
            self.extract_emails(response.text)

            # Обработка ссылок
            for link_tag in soup.find_all('a', href=True):
                href = link_tag['href']
                absolute_url = self.normalize_url(href, url)
                if absolute_url:
                    self.process_link(absolute_url, depth)

        except requests.RequestException as e:
            logger.error(f'Ошибка при загрузке {url}: {e}')

    def normalize_url(self, href: str, base_url: str) -> str | None:
        """Преобразование ссылки в абсолютный URL с проверкой домена."""
        # Преобразование в абсолютный URL
        absolute_url = urljoin(base_url, href.strip())
        parsed_url = urlparse(absolute_url)

        # Проверка домена
        if not self.ALLOW_SUBDOMAINS:
            if parsed_url.netloc != self.base_domain:
                return None

        # Удаление якорей
        if '#' in absolute_url:
            absolute_url = absolute_url.split('#')[0]

        return absolute_url

    def process_link(self, url: str, depth: int) -> None:
        """Обработка найденной ссылки."""
        if url not in self.data['links']:
            self.data['links'].append(url)

            # Проверка на файл
            parsed_url = urlparse(url)
            _, ext = os.path.splitext(parsed_url.path)
            if ext.lower() in self.FILE_EXTENSIONS:
                self.data['files'].append(url)
                logger.debug(f'Найден файл: {url}')

            # Проверка на каталог
            if parsed_url.path.endswith('/') and parsed_url.path not in self.data['directories']:
                self.data['directories'].append(parsed_url.path)
                logger.debug(f'Найден каталог: {parsed_url.path}')

            # Добавление в очередь, если глубина позволяет
            if depth + 1 < self.MAX_DEPTH and url not in self.crawled:
                self.to_crawl.append((url, depth + 1))

    def extract_emails(self, text: str) -> None:
        """Извлечение email-адресов из текста страницы."""
        found_emails = self.email_regex.findall(text)
        for email in found_emails:
            if email not in self.data['emails']:
                self.data['emails'].append(email)
                logger.debug(f'Найден email: {email}')
