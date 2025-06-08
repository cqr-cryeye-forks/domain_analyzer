import logging
import os
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from crawler.crawler_constants import FILE_EXTENSIONS
from crawler.crawler_utils import (
    normalize_url,
    extract_directories,
    check_directory_indexing,
    extract_emails,
    is_file_url
)

# Настройка логирования
logger = logging.getLogger(__name__)


class Crawler:
    """Класс для сканирования веб-сайта."""

    ALLOW_SUBDOMAINS = False

    def __init__(
            self,
            base_url: str,
            max_urls: int = 5000,
            fetch_files: bool = False,
            subdomains: bool = False,
            follow_redirects: bool = True,
            extensions: list[str] = None,
            exclude_extensions: list[str] = None
    ):
        """Инициализация краулера."""
        self.base_url = self._normalize_base_url(base_url)
        self.max_urls = max_urls
        self.fetch_files = fetch_files
        self.ALLOW_SUBDOMAINS = subdomains
        self.follow_redirects = follow_redirects
        self.extensions = extensions if extensions else FILE_EXTENSIONS
        self.exclude_extensions = exclude_extensions if exclude_extensions else []
        self.data = {
            'links': [],
            'directories': [],
            'files': [],
            'emails': [],
            'externals': [],
            'directories_with_indexing': [],
            'messages': {}
        }
        self.to_crawl = [(self.base_url, 0)]
        self.crawled = set()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)'})

    def _normalize_base_url(self, url: str) -> str:
        """Добавляет схему http, если отсутствует."""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url.rstrip('/')

    def _fetch_file(self, url: str, directory: str) -> bool:
        """Скачивает файл по URL в указанную папку."""
        try:
            response = self.session.get(url, timeout=50, allow_redirects=self.follow_redirects)
            if response.status_code == 200:
                filename = url.split('/')[-1]
                filepath = os.path.join(directory, filename)
                os.makedirs(directory, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Файл скачан: {filepath}")
                return True
            else:
                logger.debug(f"Ошибка скачивания {url}: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.debug(f"Ошибка скачивания {url}: {e}")
            return False

    def crawl_url(self, url: str) -> bool:
        """Сканирует одну страницу и извлекает данные."""
        if is_file_url(url):
            if url not in self.data['files']:
                self.data['files'].append(url)
                logger.debug(f"Найден файл: {url}")
            if self.fetch_files and not any(url.endswith(ext) for ext in self.exclude_extensions):
                parsed = urlparse(self.base_url)
                domain = parsed.netloc.replace('www.', '').split(':')[0]
                directory = os.path.join(domain, 'Files')
                self._fetch_file(url, directory)
            return False

        try:
            response = self.session.get(
                url.replace(' ', '%20'),
                timeout=5,
                allow_redirects=self.follow_redirects
            )
            if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                if response.status_code in (301, 302) and self.follow_redirects:
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        normalized = normalize_url(redirect_url, self.base_url)
                        if normalized and normalized not in self.crawled:
                            self.to_crawl.append((normalized, 0))
                            logger.debug(f"Редирект на: {normalized}")
                logger.debug(f"Пропуск {url}: код {response.status_code} или не HTML")
                return False

            soup = BeautifulSoup(response.text, 'html.parser')
            self.data['emails'].extend(extract_emails(response.text))
            self.data['emails'] = list(set(self.data['emails']))

            for link in soup.find_all(['a', 'iframe', 'img'], href=True):
                href = link.get('href')
                normalized = normalize_url(href, url)
                if not normalized:
                    continue
                parsed = urlparse(normalized)
                if parsed.netloc == urlparse(self.base_url).netloc or (
                        self.ALLOW_SUBDOMAINS and urlparse(self.base_url).netloc in parsed.netloc
                ):
                    if is_file_url(normalized):
                        if normalized not in self.data['files']:
                            self.data['files'].append(normalized)
                            if self.fetch_files and not any(
                                    normalized.endswith(ext) for ext in self.exclude_extensions):
                                domain = parsed.netloc.replace('www.', '').split(':')[0]
                                directory = os.path.join(domain, 'Files')
                                self._fetch_file(normalized, directory)
                    else:
                        if normalized not in self.data['links']:
                            self.data['links'].append(normalized)
                        if normalized not in self.crawled and normalized not in [x[0] for x in self.to_crawl]:
                            self.to_crawl.append((normalized, 0))
                            logger.debug(f"Добавлена ссылка: {normalized}")
                else:
                    if normalized not in self.data['externals']:
                        self.data['externals'].append(normalized)
                        logger.debug(f"Найдена внешняя ссылка: {normalized}")

            directories = extract_directories(url)
            for directory in directories:
                if directory not in self.data['directories']:
                    self.data['directories'].append(directory)
                    if check_directory_indexing(directory):
                        self.data['directories_with_indexing'].append(directory)
                        logger.info(f"Найден каталог с индексацией: {directory}")
            return True

        except requests.RequestException as e:
            logger.debug(f"Ошибка сканирования {url}: {e}")
            self.data['messages'][f"error_{url}"] = str(e)
            return False
        except KeyboardInterrupt:
            logger.info("Прерывание пользователем при сканировании URL")
            return False

    def crawl_site(self) -> dict:
        """Запускает сканирование сайта."""
        logger.info(f"Начало сканирования: {self.base_url}")
        try:
            while self.to_crawl and len(self.crawled) < self.max_urls:
                url, _ = self.to_crawl.pop(0)
                if url in self.crawled:
                    continue
                logger.debug(f"Сканирование URL: {url}")
                self.crawled.add(url)
                self.crawl_url(url)
        except KeyboardInterrupt:
            logger.info("Сканирование прервано пользователем")

        self.data['links'] = sorted(list(set(self.data['links'])))
        self.data['directories'] = sorted(list(set(self.data['directories'])))
        self.data['files'] = sorted(list(set(self.data['files'])))
        self.data['externals'] = sorted(list(set(self.data['externals'])))
        self.data['directories_with_indexing'] = sorted(list(set(self.data['directories_with_indexing'])))
        self.data['emails'] = sorted(list(set(self.data['emails'])))

        if not self.data['links']:
            self.data['messages']['message_links'] = "Не удалось найти ссылки"
        if not self.data['directories']:
            self.data['messages']['message_directories'] = "Не удалось найти каталоги"
        if not self.data['files']:
            self.data['messages']['message_files'] = "Не удалось найти файлы"
        if not self.data['emails']:
            self.data['messages']['message_emails'] = "Не удалось найти email-адреса"
        if not self.data['externals']:
            self.data['messages']['message_externals'] = "Не удалось найти внешние ссылки"
        if not self.data['directories_with_indexing']:
            self.data['messages']['message_directories_with_indexing'] = "Не удалось найти каталоги с индексацией"

        logger.info(f"Сканирование завершено: {len(self.crawled)} URL обработано")
        return self.data
