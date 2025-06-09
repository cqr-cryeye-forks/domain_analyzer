import argparse
import logging
import asyncio
from crawler.src.crawler_core import Crawler
from crawler.src.crawler_constants import FILE_EXTENSIONS
from domain_analyzer.dns_utils import get_A_records
from domain_analyzer.output_utils import save_json
from domain_analyzer.nmap_utils import scan_host
from domain_analyzer.constants import DEFAULT_MAX_CRAWL

logger = logging.getLogger(__name__)


class IntegratedAnalyzer:
    def __init__(self, args):
        self.domain = args.domain
        self.max_urls = args.max_urls
        self.fetch_files = args.fetch_files
        self.subdomains = args.subdomains
        self.output_file = args.output or f"{self.domain}.json"
        self.domain_data = {
            "domain": self.domain,
            "ips": [],
            "crawler_results": {}
        }

    async def analyze(self):
        logger.info(f"Начинается анализ домена {self.domain}")

        # Сбор A-записей (DNS)
        a_records = get_A_records(self.domain)
        for record in a_records:
            ip = record["ip"]
            self.domain_data["ips"].append({"ip": ip})

            # Сканирование портов с помощью Nmap
            ports = scan_host(ip, self.domain)
            self.domain_data["ips"][-1]["ports"] = ports

            # Запуск веб-краулинга
            url = f"http://{self.domain}"
            crawler = Crawler(
                base_url=url,
                max_urls=self.max_urls,
                fetch_files=self.fetch_files,
                subdomains=self.subdomains,
                extensions=FILE_EXTENSIONS,
                exclude_extensions=[]
            )
            crawl_results = await crawler.crawl_site()  # Асинхронный вызов
            self.domain_data["crawler_results"][url] = crawl_results

        # Сохранение результатов в JSON
        save_json(self.domain_data, self.output_file)
        logger.info(f"Анализ домена {self.domain} завершен")


def parse_args():
    parser = argparse.ArgumentParser(description="Интегрированный анализатор доменов с веб-краулингом")
    parser.add_argument("-d", "--domain", required=True, help="Домен для анализа")
    parser.add_argument("--max-urls", type=int, default=DEFAULT_MAX_CRAWL,
                        help="Максимальное количество URL для краулинга")
    parser.add_argument("--fetch-files", action="store_true", help="Скачивать файлы во время краулинга")
    parser.add_argument("--subdomains", action="store_true", help="Анализировать поддомены")
    parser.add_argument("--output", help="Выходной JSON-файл")
    return parser.parse_args()


async def main():
    args = parse_args()
    analyzer = IntegratedAnalyzer(args)
    await analyzer.analyze()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())